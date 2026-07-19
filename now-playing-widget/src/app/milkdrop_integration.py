"""
MilkDrop Visualization Integration
Advanced audio visualization using MilkDrop 2 SDK
"""

import os
import ctypes
import numpy as np
from typing import Optional, Tuple, List
from dataclasses import dataclass
from pathlib import Path
import struct


@dataclass
class MilkDropConfig:
    """MilkDrop configuration"""
    width: int = 1024
    height: int = 768
    fps: int = 60
    quality: str = "high"  # low, medium, high
    preset: str = "default"


class MilkDropSDK:
    """
    MilkDrop 2 Visualization SDK Wrapper
    Integrates Milkdrop preset rendering
    """
    
    # MilkDrop library paths for different platforms
    LIBRARY_PATHS = {
        "windows": [
            r"C:\Program Files\MilkDrop 2\milk_2.dll",
            r"C:\Program Files (x86)\MilkDrop 2\milk_2.dll",
            "milk_2.dll",
        ],
        "linux": [
            "/usr/lib/libmilkdrop.so",
            "/usr/local/lib/libmilkdrop.so",
            "libmilkdrop.so",
        ],
        "darwin": [
            "/usr/local/lib/libmilkdrop.dylib",
            "/opt/homebrew/lib/libmilkdrop.dylib",
            "libmilkdrop.dylib",
        ],
    }
    
    # MilkDrop preset search paths
    PRESET_PATHS = {
        "windows": [
            r"C:\Program Files\MilkDrop 2\presets",
            r"C:\Users\%username%\AppData\Roaming\MilkDrop 2\presets",
        ],
        "linux": [
            "/usr/share/milkdrop/presets",
            os.path.expanduser("~/.milkdrop/presets"),
        ],
        "darwin": [
            "/usr/local/share/milkdrop/presets",
            os.path.expanduser("~/Library/Application Support/MilkDrop/presets"),
        ],
    }
    
    def __init__(self, config: Optional[MilkDropConfig] = None):
        """
        Initialize MilkDrop SDK
        
        Args:
            config: MilkDropConfig instance
        """
        self.config = config or MilkDropConfig()
        self.lib = None
        self.initialized = False
        self.presets: List[str] = []
        self.current_preset = ""
        
        self._detect_platform()
        self._load_library()
        self._load_presets()
    
    def _detect_platform(self) -> str:
        """Detect operating system"""
        import platform
        system = platform.system().lower()
        
        if "windows" in system:
            self.platform = "windows"
        elif "linux" in system:
            self.platform = "linux"
        elif "darwin" in system:
            self.platform = "darwin"
        else:
            self.platform = "linux"  # Default fallback
        
        return self.platform
    
    def _load_library(self) -> bool:
        """Load MilkDrop library"""
        paths = self.LIBRARY_PATHS.get(self.platform, [])
        
        for path in paths:
            try:
                expanded_path = os.path.expandvars(os.path.expanduser(path))
                if os.path.exists(expanded_path):
                    self.lib = ctypes.CDLL(expanded_path)
                    self.initialized = True
                    print(f"✓ MilkDrop library loaded: {path}")
                    return True
            except (OSError, ctypes.OSError):
                continue
        
        print("⚠ MilkDrop library not found. Running in software rendering mode.")
        return False
    
    def _load_presets(self) -> None:
        """Load available MilkDrop presets"""
        preset_dirs = self.PRESET_PATHS.get(self.platform, [])
        
        for preset_dir in preset_dirs:
            expanded_dir = os.path.expandvars(os.path.expanduser(preset_dir))
            
            if os.path.isdir(expanded_dir):
                for file in os.listdir(expanded_dir):
                    if file.endswith(('.milk', '.milkpre')):
                        self.presets.append(file)
        
        if self.presets:
            self.current_preset = self.presets[0]
            print(f"✓ Loaded {len(self.presets)} MilkDrop presets")
        else:
            print("⚠ No MilkDrop presets found")
    
    def list_presets(self) -> List[str]:
        """Get list of available presets"""
        return self.presets
    
    def load_preset(self, preset_name: str) -> bool:
        """
        Load a MilkDrop preset
        
        Args:
            preset_name: Name of preset file
            
        Returns:
            True if successful
        """
        if preset_name in self.presets:
            self.current_preset = preset_name
            return True
        return False
    
    def get_current_preset(self) -> str:
        """Get currently loaded preset"""
        return self.current_preset
    
    def process_audio(self, audio_data: np.ndarray, 
                     waveform: Optional[np.ndarray] = None) -> np.ndarray:
        """
        Process audio and generate visualization
        
        Args:
            audio_data: Audio samples
            waveform: Optional waveform data
            
        Returns:
            Rendered frame data
        """
        if not self.initialized:
            return self._render_software(audio_data)
        
        # Use MilkDrop library
        return self._render_milkdrop(audio_data, waveform)
    
    def _render_milkdrop(self, audio_data: np.ndarray, 
                        waveform: Optional[np.ndarray]) -> np.ndarray:
        """Render using MilkDrop library"""
        frame = np.zeros((self.config.height, self.config.width, 3), dtype=np.uint8)
        
        # This would call actual MilkDrop rendering functions
        # For now, return placeholder
        return frame
    
    def _render_software(self, audio_data: np.ndarray) -> np.ndarray:
        """Software rendering fallback"""
        frame = np.zeros((self.config.height, self.config.width, 3), dtype=np.uint8)
        
        # Generate simple visualization
        spectrum = np.abs(np.fft.fft(audio_data))
        spectrum = spectrum[:len(spectrum)//2]
        
        # Normalize
        spectrum = spectrum / (np.max(spectrum) + 1e-10)
        
        # Create bars
        num_bars = 64
        bar_width = self.config.width // num_bars
        
        for i in range(num_bars):
            if i < len(spectrum):
                height = int(spectrum[i] * self.config.height * 0.8)
                
                for y in range(self.config.height - height, self.config.height):
                    x_start = i * bar_width
                    x_end = (i + 1) * bar_width
                    
                    # Color gradient
                    hue = int(255 * i / num_bars)
                    
                    for x in range(x_start, min(x_end, self.config.width)):
                        frame[y, x] = [hue, 200, 255]
        
        return frame


class MilkDropVisualizer:
    """High-level MilkDrop visualizer wrapper"""
    
    def __init__(self, config: Optional[MilkDropConfig] = None):
        """
        Initialize visualizer
        
        Args:
            config: MilkDropConfig instance
        """
        self.config = config or MilkDropConfig()
        self.sdk = MilkDropSDK(config)
        self.frame_count = 0
        self.fps = config.fps
    
    def render_frame(self, audio_data: np.ndarray, 
                    waveform: Optional[np.ndarray] = None) -> np.ndarray:
        """
        Render visualization frame
        
        Args:
            audio_data: Audio samples
            waveform: Optional waveform data
            
        Returns:
            Rendered frame (RGB)
        """
        frame = self.sdk.process_audio(audio_data, waveform)
        self.frame_count += 1
        return frame
    
    def set_preset(self, preset_name: str) -> bool:
        """
        Set visualization preset
        
        Args:
            preset_name: Preset name
            
        Returns:
            True if successful
        """
        return self.sdk.load_preset(preset_name)
    
    def get_presets(self) -> List[str]:
        """Get available presets"""
        return self.sdk.list_presets()
    
    def get_current_preset(self) -> str:
        """Get current preset"""
        return self.sdk.get_current_preset()


class MilkDropPresetManager:
    """Manage MilkDrop presets"""
    
    def __init__(self):
        """Initialize preset manager"""
        self.presets: dict = {}
        self.current = None
        self._scan_presets()
    
    def _scan_presets(self) -> None:
        """Scan for presets"""
        sdk = MilkDropSDK()
        for preset in sdk.list_presets():
            self.presets[preset] = {
                "name": preset,
                "path": preset,
                "enabled": True,
            }
    
    def list_presets(self) -> List[str]:
        """List all presets"""
        return list(self.presets.keys())
    
    def get_preset_info(self, name: str) -> Optional[dict]:
        """Get preset information"""
        return self.presets.get(name)
    
    def enable_preset(self, name: str) -> None:
        """Enable a preset"""
        if name in self.presets:
            self.presets[name]["enabled"] = True
    
    def disable_preset(self, name: str) -> None:
        """Disable a preset"""
        if name in self.presets:
            self.presets[name]["enabled"] = False
    
    def get_enabled_presets(self) -> List[str]:
        """Get list of enabled presets"""
        return [name for name, info in self.presets.items() if info["enabled"]]


class MilkDropEffects:
    """MilkDrop visual effects library"""
    
    # Preset categories
    CATEGORIES = {
        "abstract": "Abstract visualizations",
        "geometric": "Geometric patterns",
        "particle": "Particle effects",
        "wave": "Wave effects",
        "tunnel": "Tunnel effects",
        "landscape": "Landscape effects",
        "organic": "Organic shapes",
        "technical": "Technical visualizations",
    }
    
    def __init__(self):
        """Initialize effects library"""
        self.manager = MilkDropPresetManager()
        self.current_category = None
    
    def get_categories(self) -> dict:
        """Get effect categories"""
        return self.CATEGORIES
    
    def categorize_presets(self) -> dict:
        """Categorize available presets"""
        categorized = {cat: [] for cat in self.CATEGORIES}
        
        for preset in self.manager.list_presets():
            # Categorize based on preset name patterns
            preset_lower = preset.lower()
            
            if any(x in preset_lower for x in ["abstract", "wild"]):
                categorized["abstract"].append(preset)
            elif any(x in preset_lower for x in ["geo", "triangle", "square", "shape"]):
                categorized["geometric"].append(preset)
            elif any(x in preset_lower for x in ["particle", "spark", "rain"]):
                categorized["particle"].append(preset)
            elif any(x in preset_lower for x in ["wave", "flow", "ripple"]):
                categorized["wave"].append(preset)
            elif any(x in preset_lower for x in ["tunnel", "vortex", "spiral"]):
                categorized["tunnel"].append(preset)
            elif any(x in preset_lower for x in ["land", "terrain", "mountain"]):
                categorized["landscape"].append(preset)
            elif any(x in preset_lower for x in ["organic", "blob", "cell"]):
                categorized["organic"].append(preset)
            else:
                categorized["technical"].append(preset)
        
        return categorized
    
    def get_presets_by_category(self, category: str) -> List[str]:
        """Get presets for a specific category"""
        categorized = self.categorize_presets()
        return categorized.get(category, [])


# Example usage
if __name__ == "__main__":
    # Initialize MilkDrop SDK
    config = MilkDropConfig(width=1280, height=720, quality="high")
    visualizer = MilkDropVisualizer(config)
    
    print("Available MilkDrop Presets:")
    presets = visualizer.get_presets()
    for i, preset in enumerate(presets[:10]):
        print(f"  {i+1}. {preset}")
    
    if presets:
        visualizer.set_preset(presets[0])
        print(f"\nLoaded preset: {visualizer.get_current_preset()}")
    
    # Test with demo audio
    import time
    audio_data = np.sin(np.linspace(0, 4 * np.pi, 2048)) * 0.5
    frame = visualizer.render_frame(audio_data)
    print(f"Generated frame: {frame.shape}")
