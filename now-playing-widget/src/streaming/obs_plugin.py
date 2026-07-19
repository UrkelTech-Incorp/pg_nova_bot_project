"""
OBS Studio Plugin Integration
Stream now-playing information to OBS
"""

import json
import asyncio
import websocket
from typing import Dict, Optional, Callable
from dataclasses import dataclass, asdict


@dataclass
class NowPlayingData:
    """Now playing information"""
    title: str
    artist: str
    album: str
    duration: int  # milliseconds
    position: int  # milliseconds
    is_playing: bool
    cover_art_url: Optional[str] = None


@dataclass
class VisualizerData:
    """Visualizer data to stream"""
    spectrum: list  # Array of 0.0-1.0 values
    waveform: list  # Optional waveform data
    timestamp: float


class OBSWebSocketClient:
    """OBS WebSocket protocol client"""
    
    def __init__(self, host: str = "localhost", port: int = 4444, password: str = ""):
        """
        Initialize OBS WebSocket client
        
        Args:
            host: OBS host
            port: OBS WebSocket port
            password: OBS WebSocket password
        """
        self.host = host
        self.port = port
        self.password = password
        self.ws: Optional[websocket.WebSocket] = None
        self.connected = False
        self.request_id = 0
    
    def connect(self) -> bool:
        """Connect to OBS"""
        try:
            self.ws = websocket.create_connection(f"ws://{self.host}:{self.port}")
            self.connected = True
            return True
        except Exception as e:
            print(f"Failed to connect to OBS: {e}")
            return False
    
    def disconnect(self) -> None:
        """Disconnect from OBS"""
        if self.ws:
            self.ws.close()
        self.connected = False
    
    def send_request(self, request_type: str, data: Dict) -> Optional[Dict]:
        """
        Send request to OBS
        
        Args:
            request_type: Type of request
            data: Request data
            
        Returns:
            Response data or None
        """
        if not self.connected or not self.ws:
            return None
        
        self.request_id += 1
        message = {
            "request-type": request_type,
            "message-id": str(self.request_id),
            "type": "request",
            "data": data
        }
        
        try:
            self.ws.send(json.dumps(message))
            response = self.ws.recv()
            return json.loads(response)
        except Exception as e:
            print(f"Error sending request: {e}")
            return None
    
    def get_scene_list(self) -> Optional[list]:
        """Get list of scenes"""
        response = self.send_request("GetSceneList", {})
        if response and "scenes" in response:
            return response["scenes"]
        return None
    
    def get_sources(self, scene_name: str) -> Optional[list]:
        """Get sources in scene"""
        response = self.send_request("GetSourcesList", {"sceneName": scene_name})
        if response and "sources" in response:
            return response["sources"]
        return None
    
    def set_source_settings(self, source_name: str, settings: Dict) -> bool:
        """Set source settings"""
        response = self.send_request(
            "SetSourceSettings",
            {"sourceName": source_name, "sourceSettings": settings}
        )
        return response is not None


class OBSNowPlayingPlugin:
    """OBS plugin for displaying now-playing information"""
    
    def __init__(self, obs_client: Optional[OBSWebSocketClient] = None):
        """
        Initialize OBS now-playing plugin
        
        Args:
            obs_client: OBSWebSocketClient instance
        """
        self.obs_client = obs_client or OBSWebSocketClient()
        self.source_name = "NowPlaying"
        self.is_running = False
    
    def start(self) -> bool:
        """Start plugin"""
        if not self.obs_client.connect():
            return False
        
        self.is_running = True
        return True
    
    def stop(self) -> None:
        """Stop plugin"""
        self.is_running = False
        self.obs_client.disconnect()
    
    def update_now_playing(self, data: NowPlayingData) -> bool:
        """
        Update now-playing information in OBS
        
        Args:
            data: NowPlayingData object
            
        Returns:
            True if successful
        """
        if not self.is_running:
            return False
        
        settings = {
            "text": self._format_text(data),
            "file": data.cover_art_url or "",
        }
        
        return self.obs_client.set_source_settings(self.source_name, settings)
    
    def update_visualizer(self, data: VisualizerData) -> bool:
        """
        Update visualizer data in OBS
        
        Args:
            data: VisualizerData object
            
        Returns:
            True if successful
        """
        if not self.is_running:
            return False
        
        # Convert spectrum data to a format OBS can display
        spectrum_str = ",".join(f"{v:.2f}" for v in data.spectrum)
        
        settings = {
            "text": spectrum_str,
        }
        
        return self.obs_client.set_source_settings("Visualizer", settings)
    
    @staticmethod
    def _format_text(data: NowPlayingData) -> str:
        """Format now-playing text"""
        text = f"{data.title}\n{data.artist}"
        if data.album:
            text += f"\n{data.album}"
        
        # Add progress
        progress_pct = (data.position / data.duration * 100) if data.duration > 0 else 0
        text += f"\n{progress_pct:.0f}%"
        
        return text


class OBSStreamingServer:
    """HTTP server for streaming now-playing data to OBS"""
    
    def __init__(self, host: str = "localhost", port: int = 8080):
        """
        Initialize streaming server
        
        Args:
            host: Server host
            port: Server port
        """
        self.host = host
        self.port = port
        self.current_data: Optional[NowPlayingData] = None
        self.visualizer_data: Optional[VisualizerData] = None
    
    def update_now_playing(self, data: NowPlayingData) -> None:
        """Update now-playing data"""
        self.current_data = data
    
    def update_visualizer(self, data: VisualizerData) -> None:
        """Update visualizer data"""
        self.visualizer_data = data
    
    def get_now_playing_json(self) -> str:
        """Get now-playing data as JSON"""
        if self.current_data:
            return json.dumps({
                "title": self.current_data.title,
                "artist": self.current_data.artist,
                "album": self.current_data.album,
                "duration": self.current_data.duration,
                "position": self.current_data.position,
                "is_playing": self.current_data.is_playing,
                "cover_art": self.current_data.cover_art_url,
            })
        return json.dumps({})
    
    def get_visualizer_json(self) -> str:
        """Get visualizer data as JSON"""
        if self.visualizer_data:
            return json.dumps({
                "spectrum": self.visualizer_data.spectrum,
                "waveform": self.visualizer_data.waveform,
                "timestamp": self.visualizer_data.timestamp,
            })
        return json.dumps({})
