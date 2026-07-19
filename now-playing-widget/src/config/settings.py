"""
Application Settings and Configuration
"""

import json
from pathlib import Path
from typing import Dict, Any, Optional
from dataclasses import dataclass, asdict


@dataclass
class OBSSettings:
    """OBS streaming settings"""
    host: str = "localhost"
    port: int = 4444
    password: str = ""
    enabled: bool = False


@dataclass
class CamoSettings:
    """Camo streaming settings"""
    enabled: bool = False
    resolution: str = "1280x720"  # "640x480", "1280x720", "1920x1080"
    framerate: int = 30


@dataclass
class AudioSettings:
    """Audio input settings"""
    device_index: int = -1  # -1 for default
    sample_rate: int = 44100
    channels: int = 1
    buffer_size: int = 2048


@dataclass
class VisualizerSettings:
    """Visualizer settings"""
    bar_count: int = 32
    smoothing: float = 0.85
    style: str = "bars"  # "bars", "waveform", "radial"
    color_palette: str = "nova"


@dataclass
class AppSettings:
    """Main application settings"""
    theme: str = "nova"  # "nova", "nova_light", "nova_dark"
    poweramp_skin: str = "default"
    window_width: int = 800
    window_height: int = 600
    
    obs: OBSSettings = None
    camo: CamoSettings = None
    audio: AudioSettings = None
    visualizer: VisualizerSettings = None
    
    def __post_init__(self):
        if self.obs is None:
            self.obs = OBSSettings()
        if self.camo is None:
            self.camo = CamoSettings()
        if self.audio is None:
            self.audio = AudioSettings()
        if self.visualizer is None:
            self.visualizer = VisualizerSettings()


class SettingsManager:
    """Manages application settings"""
    
    CONFIG_FILENAME = "config.json"
    
    def __init__(self, config_dir: Optional[Path] = None):
        """
        Initialize settings manager
        
        Args:
            config_dir: Configuration directory path
        """
        if config_dir is None:
            config_dir = Path.home() / ".now_playing_widget"
        
        self.config_dir = Path(config_dir)
        self.config_dir.mkdir(parents=True, exist_ok=True)
        
        self.config_file = self.config_dir / self.CONFIG_FILENAME
        self.settings = self._load_settings()
    
    def _load_settings(self) -> AppSettings:
        """Load settings from file or use defaults"""
        if self.config_file.exists():
            try:
                with open(self.config_file, 'r') as f:
                    data = json.load(f)
                    return self._dict_to_settings(data)
            except Exception as e:
                print(f"Error loading settings: {e}")
        
        return AppSettings()
    
    def save_settings(self) -> bool:
        """Save settings to file"""
        try:
            data = self._settings_to_dict(self.settings)
            with open(self.config_file, 'w') as f:
                json.dump(data, f, indent=2)
            return True
        except Exception as e:
            print(f"Error saving settings: {e}")
            return False
    
    def _settings_to_dict(self, settings: AppSettings) -> Dict[str, Any]:
        """Convert settings to dictionary"""
        return {
            "theme": settings.theme,
            "poweramp_skin": settings.poweramp_skin,
            "window_width": settings.window_width,
            "window_height": settings.window_height,
            "obs": asdict(settings.obs),
            "camo": asdict(settings.camo),
            "audio": asdict(settings.audio),
            "visualizer": asdict(settings.visualizer),
        }
    
    def _dict_to_settings(self, data: Dict[str, Any]) -> AppSettings:
        """Convert dictionary to settings"""
        obs = OBSSettings(**data.get("obs", {})) if "obs" in data else OBSSettings()
        camo = CamoSettings(**data.get("camo", {})) if "camo" in data else CamoSettings()
        audio = AudioSettings(**data.get("audio", {})) if "audio" in data else AudioSettings()
        visualizer = VisualizerSettings(**data.get("visualizer", {})) if "visualizer" in data else VisualizerSettings()
        
        return AppSettings(
            theme=data.get("theme", "nova"),
            poweramp_skin=data.get("poweramp_skin", "default"),
            window_width=data.get("window_width", 800),
            window_height=data.get("window_height", 600),
            obs=obs,
            camo=camo,
            audio=audio,
            visualizer=visualizer,
        )
    
    def get_setting(self, key: str, default: Any = None) -> Any:
        """Get a specific setting"""
        keys = key.split(".")
        obj = self.settings
        
        for k in keys:
            if hasattr(obj, k):
                obj = getattr(obj, k)
            else:
                return default
        
        return obj
    
    def set_setting(self, key: str, value: Any) -> None:
        """Set a specific setting"""
        keys = key.split(".")
        obj = self.settings
        
        for k in keys[:-1]:
            if not hasattr(obj, k):
                setattr(obj, k, {})
            obj = getattr(obj, k)
        
        setattr(obj, keys[-1], value)
