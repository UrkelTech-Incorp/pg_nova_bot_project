"""
Audio Visualization Engine
Generates real-time waveform visualizations
"""

import numpy as np
from typing import List, Tuple, Optional
from dataclasses import dataclass


@dataclass
class VisualizerConfig:
    """Configuration for audio visualizer"""
    sample_rate: int = 44100
    fft_size: int = 2048
    freq_min: float = 20.0
    freq_max: float = 20000.0
    smoothing_factor: float = 0.85
    bar_count: int = 32
    db_min: float = -80.0
    db_max: float = 0.0


class AudioVisualizer:
    """Real-time audio waveform visualizer"""
    
    def __init__(self, config: VisualizerConfig = None):
        """
        Initialize audio visualizer
        
        Args:
            config: Visualizer configuration
        """
        self.config = config or VisualizerConfig()
        self.prev_spectrum = np.zeros(self.config.bar_count)
        self.freq_bins = self._create_freq_bins()
    
    def _create_freq_bins(self) -> np.ndarray:
        """Create frequency bins for visualization"""
        # Logarithmic frequency spacing
        log_min = np.log10(self.config.freq_min)
        log_max = np.log10(self.config.freq_max)
        freq_bins = np.logspace(log_min, log_max, self.config.bar_count)
        return freq_bins
    
    def process_audio(self, audio_data: np.ndarray) -> np.ndarray:
        """
        Process audio data and generate visualization spectrum
        
        Args:
            audio_data: Audio samples (mono or stereo)
            
        Returns:
            Array of bar heights (0.0-1.0)
        """
        if len(audio_data) == 0:
            return self.prev_spectrum.copy()
        
        # Convert to mono if stereo
        if len(audio_data.shape) > 1:
            audio_data = np.mean(audio_data, axis=1)
        
        # Apply Hann window
        window = np.hanning(len(audio_data))
        audio_windowed = audio_data * window
        
        # Compute FFT
        fft_data = np.fft.fft(audio_windowed)
        magnitude = np.abs(fft_data[:len(fft_data)//2])
        
        # Convert to dB scale
        magnitude_db = 20 * np.log10(magnitude + 1e-10)
        
        # Normalize
        magnitude_db = np.clip(
            (magnitude_db - self.config.db_min) / (self.config.db_max - self.config.db_min),
            0, 1
        )
        
        # Map to frequency bins
        spectrum = self._map_to_bins(magnitude_db)
        
        # Apply smoothing
        spectrum = (
            self.config.smoothing_factor * self.prev_spectrum +
            (1 - self.config.smoothing_factor) * spectrum
        )
        
        self.prev_spectrum = spectrum
        return spectrum
    
    def _map_to_bins(self, magnitude: np.ndarray) -> np.ndarray:
        """Map magnitude spectrum to visualization bars"""
        freqs = np.fft.fftfreq(len(magnitude) * 2, 1 / self.config.sample_rate)[:len(magnitude)]
        
        bins = np.zeros(self.config.bar_count)
        
        for i, freq_bin in enumerate(self.freq_bins):
            # Find magnitude values in this frequency range
            if i == 0:
                lower_freq = self.config.freq_min
            else:
                lower_freq = (self.freq_bins[i-1] + freq_bin) / 2
            
            if i == len(self.freq_bins) - 1:
                upper_freq = self.config.freq_max
            else:
                upper_freq = (freq_bin + self.freq_bins[i+1]) / 2
            
            mask = (freqs >= lower_freq) & (freqs < upper_freq)
            if np.any(mask):
                bins[i] = np.max(magnitude[mask])
        
        return bins
    
    def get_spectrum(self) -> np.ndarray:
        """Get current spectrum"""
        return self.prev_spectrum.copy()


class WaveformVisualizer:
    """Waveform display visualizer"""
    
    def __init__(self, width: int = 1024, height: int = 256):
        """
        Initialize waveform visualizer
        
        Args:
            width: Display width in pixels
            height: Display height in pixels
        """
        self.width = width
        self.height = height
        self.buffer_size = width
        self.waveform_buffer = np.zeros(self.buffer_size)
    
    def process_audio(self, audio_data: np.ndarray) -> np.ndarray:
        """
        Process audio and generate waveform
        
        Args:
            audio_data: Audio samples
            
        Returns:
            2D array for rendering (height x width)
        """
        if len(audio_data) == 0:
            return np.zeros((self.height, self.width))
        
        # Resample to buffer size
        indices = np.linspace(0, len(audio_data) - 1, self.buffer_size)
        resampled = np.interp(indices, np.arange(len(audio_data)), audio_data)
        
        # Update buffer (scroll effect)
        self.waveform_buffer = np.roll(self.waveform_buffer, -1)
        self.waveform_buffer[-1] = resampled[-1]
        
        # Generate visualization
        viz = self._render_waveform(self.waveform_buffer)
        return viz
    
    def _render_waveform(self, waveform: np.ndarray) -> np.ndarray:
        """Render waveform as 2D array"""
        viz = np.zeros((self.height, self.width))
        
        center = self.height // 2
        scale = (self.height // 2 - 2)
        
        for x, sample in enumerate(waveform):
            if x < self.width:
                y = int(center - sample * scale)
                y = np.clip(y, 0, self.height - 1)
                viz[y, x] = 1.0
        
        return viz


class RadialVisualizer:
    """Radial/circular audio visualizer"""
    
    def __init__(self, size: int = 512, bar_count: int = 64):
        """
        Initialize radial visualizer
        
        Args:
            size: Canvas size (square)
            bar_count: Number of frequency bars
        """
        self.size = size
        self.bar_count = bar_count
        self.radius = size // 2
        self.audio_processor = AudioVisualizer(
            VisualizerConfig(bar_count=bar_count)
        )
    
    def process_audio(self, audio_data: np.ndarray) -> Tuple[np.ndarray, List[float]]:
        """
        Process audio for radial visualization
        
        Args:
            audio_data: Audio samples
            
        Returns:
            Tuple of (canvas, heights)
        """
        spectrum = self.audio_processor.process_audio(audio_data)
        canvas = self._render_radial(spectrum)
        return canvas, spectrum.tolist()
    
    def _render_radial(self, spectrum: np.ndarray) -> np.ndarray:
        """Render spectrum as radial visualization"""
        canvas = np.zeros((self.size, self.size), dtype=np.float32)
        
        angles = np.linspace(0, 2 * np.pi, len(spectrum), endpoint=False)
        
        for i, (angle, height) in enumerate(zip(angles, spectrum)):
            # Draw from center outward
            inner_r = self.radius * 0.3
            outer_r = inner_r + (self.radius * 0.6 * height)
            
            x = self.size // 2
            y = self.size // 2
            
            # Simple line drawing (would use Bresenham in production)
            r_start = int(inner_r)
            r_end = int(outer_r)
            
            for r in range(r_start, r_end):
                px = int(x + r * np.cos(angle))
                py = int(y + r * np.sin(angle))
                
                if 0 <= px < self.size and 0 <= py < self.size:
                    canvas[py, px] = height
        
        return canvas
