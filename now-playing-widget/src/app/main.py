"""
Nova Now Playing Audio Viewer - Main Application
Desktop widget with OBS/Camo streaming support
"""

import sys
import numpy as np
from pathlib import Path
from typing import Optional

from PyQt6.QtWidgets import (
    QApplication, QMainWindow, QWidget, QVBoxLayout, QHBoxLayout,
    QLabel, QComboBox, QPushButton, QCheckBox, QSpinBox
)
from PyQt6.QtCore import Qt, QTimer, pyqtSignal, QThread
from PyQt6.QtGui import QFont, QIcon, QColor
from PyQt6.QtCharts import QChart, QChartView, QBarSeries, QBarSet, QBarCategoryAxis, QValueAxis

# Import project modules
sys.path.insert(0, str(Path(__file__).parent.parent))
from ui.themes import NovaTheme, DEFAULT_NOVA_THEME, hex_to_rgb
from audio.poweramp_skins import PowerampSkinLoader, PowerampIntegration
from app.visualizer import AudioVisualizer, VisualizerConfig, RadialVisualizer
from streaming.obs_plugin import OBSWebSocketClient, OBSNowPlayingPlugin, NowPlayingData
from streaming.camo_plugin import CamoPluginManager, CamoResolution


class AudioWorker(QThread):
    """Worker thread for audio processing"""
    
    spectrum_updated = pyqtSignal(np.ndarray)
    
    def __init__(self):
        super().__init__()
        self.is_running = False
        self.visualizer = AudioVisualizer()
    
    def run(self):
        """Thread run loop"""
        self.is_running = True
        
        try:
            import pyaudio
            
            p = pyaudio.PyAudio()
            stream = p.open(
                format=pyaudio.paFloat32,
                channels=1,
                rate=44100,
                input=True,
                frames_per_buffer=2048
            )
            
            while self.is_running:
                data = stream.read(2048, exception_on_overflow=False)
                audio_data = np.frombuffer(data, dtype=np.float32)
                
                spectrum = self.visualizer.process_audio(audio_data)
                self.spectrum_updated.emit(spectrum)
            
            stream.stop_stream()
            stream.close()
            p.terminate()
        
        except ImportError:
            print("PyAudio not installed. Running in demo mode.")
            self.demo_mode()
    
    def demo_mode(self):
        """Demo mode with simulated audio"""
        while self.is_running:
            # Simulate audio spectrum
            spectrum = np.random.rand(32) * 0.8
            spectrum = np.maximum(spectrum, self.visualizer.prev_spectrum * 0.85)
            self.spectrum_updated.emit(spectrum)
            self.msleep(50)
    
    def stop(self):
        """Stop worker"""
        self.is_running = False
        self.wait()


class NowPlayingWidget(QMainWindow):
    """Main now-playing widget window"""
    
    def __init__(self):
        super().__init__()
        self.theme = DEFAULT_NOVA_THEME
        self.poweramp_integration = None
        self.obs_plugin = None
        self.camo_manager = None
        self.audio_worker = None
        
        self.setWindowTitle("Nova Now Playing")
        self.setGeometry(100, 100, 800, 600)
        
        self._setup_ui()
        self._setup_streaming()
        self._start_audio_processing()
    
    def _setup_ui(self):
        """Setup user interface"""
        main_widget = QWidget()
        self.setCentralWidget(main_widget)
        
        layout = QVBoxLayout()
        main_widget.setLayout(layout)
        
        # Title and artist display
        title_label = QLabel("Now Playing")
        title_label.setFont(QFont("Arial", 18, QFont.Weight.Bold))
        title_label.setStyleSheet(f"color: {self.theme.fg_primary};")
        layout.addWidget(title_label)
        
        artist_label = QLabel("Artist Name")
        artist_label.setFont(QFont("Arial", 12))
        artist_label.setStyleSheet(f"color: {self.theme.fg_secondary};")
        layout.addWidget(artist_label)
        
        # Visualizer area (placeholder)
        viz_label = QLabel("Visualizer")
        viz_label.setStyleSheet(f"""
            background-color: {self.theme.bg_secondary};
            border: 2px solid {self.theme.accent_primary};
            border-radius: 4px;
            padding: 20px;
            color: {self.theme.fg_secondary};
            text-align: center;
        """)
        viz_label.setMinimumHeight(200)
        layout.addWidget(viz_label)
        
        # Controls section
        controls_layout = QHBoxLayout()
        layout.addLayout(controls_layout)
        
        # Skin selector
        skin_label = QLabel("Poweramp Skin:")
        controls_layout.addWidget(skin_label)
        
        self.skin_combo = QComboBox()
        self._load_skins()
        controls_layout.addWidget(self.skin_combo)
        self.skin_combo.currentTextChanged.connect(self._on_skin_changed)
        
        # OBS checkbox
        self.obs_checkbox = QCheckBox("Stream to OBS")
        self.obs_checkbox.stateChanged.connect(self._on_obs_toggled)
        controls_layout.addWidget(self.obs_checkbox)
        
        # Camo checkbox
        self.camo_checkbox = QCheckBox("Stream to Camo")
        self.camo_checkbox.stateChanged.connect(self._on_camo_toggled)
        controls_layout.addWidget(self.camo_checkbox)
        
        # Apply styling
        self._apply_stylesheet()
    
    def _apply_stylesheet(self):
        """Apply Nova theme stylesheet"""
        stylesheet = f"""
            QMainWindow {{
                background-color: {self.theme.bg_primary};
                color: {self.theme.fg_primary};
            }}
            QLabel {{
                color: {self.theme.fg_primary};
            }}
            QComboBox {{
                background-color: {self.theme.bg_secondary};
                color: {self.theme.fg_primary};
                border: 1px solid {self.theme.border};
                border-radius: 4px;
                padding: 4px;
            }}
            QPushButton {{
                background-color: {self.theme.accent_primary};
                color: white;
                border: none;
                border-radius: 4px;
                padding: 6px 12px;
                font-weight: bold;
            }}
            QPushButton:hover {{
                background-color: {self.theme.accent_secondary};
            }}
            QCheckBox {{
                color: {self.theme.fg_primary};
            }}
        """
        self.setStyleSheet(stylesheet)
    
    def _load_skins(self):
        """Load available Poweramp skins"""
        try:
            skin_loader = PowerampSkinLoader()
            skins = skin_loader.list_skins()
            
            for skin in skins:
                self.skin_combo.addItem(skin.name)
            
            self.poweramp_integration = PowerampIntegration(skin_loader)
            
            if skins:
                self.poweramp_integration.set_skin(skins[0].name)
        
        except Exception as e:
            print(f"Error loading Poweramp skins: {e}")
    
    def _on_skin_changed(self, skin_name: str):
        """Handle skin selection change"""
        if self.poweramp_integration:
            self.poweramp_integration.set_skin(skin_name)
    
    def _setup_streaming(self):
        """Setup streaming plugins"""
        # OBS Plugin
        obs_client = OBSWebSocketClient()
        self.obs_plugin = OBSNowPlayingPlugin(obs_client)
        
        # Camo Plugin
        self.camo_manager = CamoPluginManager(CamoResolution.RES_1280x720)
    
    def _on_obs_toggled(self, state: int):
        """Handle OBS streaming toggle"""
        if state:
            if self.obs_plugin.start():
                print("OBS streaming started")
            else:
                print("Failed to connect to OBS")
                self.obs_checkbox.setChecked(False)
        else:
            self.obs_plugin.stop()
            print("OBS streaming stopped")
    
    def _on_camo_toggled(self, state: int):
        """Handle Camo streaming toggle"""
        if state:
            if self.camo_manager.start():
                print("Camo streaming started")
            else:
                print("Failed to start Camo streaming")
                self.camo_checkbox.setChecked(False)
        else:
            self.camo_manager.stop()
            print("Camo streaming stopped")
    
    def _start_audio_processing(self):
        """Start audio processing worker"""
        self.audio_worker = AudioWorker()
        self.audio_worker.spectrum_updated.connect(self._on_spectrum_updated)
        self.audio_worker.start()
    
    def _on_spectrum_updated(self, spectrum: np.ndarray):
        """Handle spectrum update from audio worker"""
        if self.camo_manager:
            self.camo_manager.update_spectrum(spectrum.tolist())
        
        if self.obs_plugin:
            # Could update OBS with spectrum data
            pass
    
    def closeEvent(self, event):
        """Handle window close"""
        if self.audio_worker:
            self.audio_worker.stop()
        
        if self.obs_plugin:
            self.obs_plugin.stop()
        
        if self.camo_manager:
            self.camo_manager.stop()
        
        event.accept()


def main():
    """Main entry point"""
    app = QApplication(sys.argv)
    window = NowPlayingWidget()
    window.show()
    sys.exit(app.exec())


if __name__ == "__main__":
    main()
