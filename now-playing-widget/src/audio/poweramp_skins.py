"""
Poweramp Skin Loader and Handler
Integrates Poweramp skins from Play Store
"""

import os
import json
import zipfile
from pathlib import Path
from typing import Dict, List, Optional, Tuple
from dataclasses import dataclass
import xml.etree.ElementTree as ET


@dataclass
class PowerampSkin:
    """Poweramp skin metadata"""
    name: str
    author: str
    version: str
    colors: Dict[str, str]
    path: Path
    icon_path: Optional[Path] = None
    
    def __repr__(self):
        return f"PowerampSkin(name='{self.name}', author='{self.author}', version='{self.version}')"


class PowerampSkinLoader:
    """Loads and manages Poweramp skins"""
    
    # Common Poweramp color keys used in skins
    COMMON_COLOR_KEYS = [
        "colorBg",
        "colorFg",
        "colorAccent",
        "colorAccent2",
        "colorText",
        "colorTextSecondary",
    ]
    
    def __init__(self, skins_directory: Optional[Path] = None):
        """
        Initialize Poweramp skin loader
        
        Args:
            skins_directory: Path to Poweramp skins directory
        """
        if skins_directory is None:
            # Default Poweramp skin paths for different platforms
            if os.name == 'nt':  # Windows
                skins_directory = Path.home() / "AppData/Local/Poweramp/skins"
            else:  # Linux/Mac
                skins_directory = Path.home() / ".local/share/Poweramp/skins"
        
        self.skins_directory = Path(skins_directory)
        self.skins: Dict[str, PowerampSkin] = {}
        self.load_skins()
    
    def load_skins(self) -> None:
        """Load all available Poweramp skins from directory"""
        if not self.skins_directory.exists():
            print(f"Skins directory not found: {self.skins_directory}")
            return
        
        for skin_dir in self.skins_directory.iterdir():
            if skin_dir.is_dir():
                try:
                    skin = self._load_skin_from_directory(skin_dir)
                    if skin:
                        self.skins[skin.name] = skin
                except Exception as e:
                    print(f"Error loading skin from {skin_dir}: {e}")
            
            elif skin_dir.suffix == '.zip':
                try:
                    skin = self._load_skin_from_zip(skin_dir)
                    if skin:
                        self.skins[skin.name] = skin
                except Exception as e:
                    print(f"Error loading skin from {skin_dir}: {e}")
    
    def _load_skin_from_directory(self, skin_path: Path) -> Optional[PowerampSkin]:
        """Load skin from directory"""
        # Look for skin metadata file
        skin_xml = skin_path / "skin.xml"
        if not skin_xml.exists():
            return None
        
        try:
            tree = ET.parse(skin_xml)
            root = tree.getroot()
            
            # Extract metadata
            name = root.get('name', skin_path.name)
            author = root.get('author', 'Unknown')
            version = root.get('version', '1.0')
            
            # Extract colors
            colors = self._extract_colors_from_xml(root)
            
            # Look for icon
            icon_path = None
            for icon_name in ['icon.png', 'preview.png']:
                icon_file = skin_path / icon_name
                if icon_file.exists():
                    icon_path = icon_file
                    break
            
            return PowerampSkin(
                name=name,
                author=author,
                version=version,
                colors=colors,
                path=skin_path,
                icon_path=icon_path
            )
        except Exception as e:
            print(f"Error parsing skin.xml: {e}")
            return None
    
    def _load_skin_from_zip(self, zip_path: Path) -> Optional[PowerampSkin]:
        """Load skin from zip file"""
        try:
            with zipfile.ZipFile(zip_path, 'r') as zip_file:
                # Look for skin.xml in zip
                skin_xml_name = None
                for name in zip_file.namelist():
                    if name.endswith('skin.xml'):
                        skin_xml_name = name
                        break
                
                if not skin_xml_name:
                    return None
                
                # Extract and parse XML
                xml_content = zip_file.read(skin_xml_name)
                root = ET.fromstring(xml_content)
                
                # Extract metadata
                name = root.get('name', zip_path.stem)
                author = root.get('author', 'Unknown')
                version = root.get('version', '1.0')
                
                # Extract colors
                colors = self._extract_colors_from_xml(root)
                
                return PowerampSkin(
                    name=name,
                    author=author,
                    version=version,
                    colors=colors,
                    path=zip_path,
                )
        except Exception as e:
            print(f"Error loading skin from zip: {e}")
            return None
    
    def _extract_colors_from_xml(self, root: ET.Element) -> Dict[str, str]:
        """Extract color definitions from skin XML"""
        colors = {}
        
        # Look for color elements
        for color_elem in root.findall('.//color'):
            color_id = color_elem.get('id')
            color_value = color_elem.get('value') or color_elem.text
            
            if color_id and color_value:
                colors[color_id] = color_value
        
        # Also check for attributes that might contain colors
        for key in self.COMMON_COLOR_KEYS:
            if key in root.attrib:
                colors[key] = root.attrib[key]
        
        return colors
    
    def get_skin(self, name: str) -> Optional[PowerampSkin]:
        """Get skin by name"""
        return self.skins.get(name)
    
    def list_skins(self) -> List[PowerampSkin]:
        """List all available skins"""
        return list(self.skins.values())
    
    def get_skin_colors(self, name: str) -> Dict[str, str]:
        """Get colors for a specific skin"""
        skin = self.get_skin(name)
        if skin:
            return skin.colors
        return {}
    
    def extract_visualizer_colors(self, skin_name: str) -> List[str]:
        """
        Extract visualizer-appropriate colors from skin
        
        Args:
            skin_name: Name of the Poweramp skin
            
        Returns:
            List of hex colors for visualizer
        """
        skin = self.get_skin(skin_name)
        if not skin:
            return []
        
        colors = []
        color_keys = ['colorAccent', 'colorAccent2', 'colorBg', 'colorFg', 'colorText']
        
        for key in color_keys:
            if key in skin.colors:
                color_value = skin.colors[key]
                # Ensure color is in hex format
                if not color_value.startswith('#'):
                    color_value = f"#{color_value}"
                colors.append(color_value)
        
        # Return at least some colors
        if not colors and skin.colors:
            colors = list(skin.colors.values())[:5]
        
        return colors[:5]  # Return up to 5 colors


class PowerampIntegration:
    """Integration with Poweramp for now-playing information"""
    
    def __init__(self, skin_loader: Optional[PowerampSkinLoader] = None):
        """
        Initialize Poweramp integration
        
        Args:
            skin_loader: PowerampSkinLoader instance
        """
        self.skin_loader = skin_loader or PowerampSkinLoader()
        self.current_skin: Optional[PowerampSkin] = None
        self.current_colors: List[str] = []
    
    def set_skin(self, skin_name: str) -> bool:
        """
        Set active Poweramp skin
        
        Args:
            skin_name: Name of skin to activate
            
        Returns:
            True if successful
        """
        skin = self.skin_loader.get_skin(skin_name)
        if skin:
            self.current_skin = skin
            self.current_colors = self.skin_loader.extract_visualizer_colors(skin_name)
            return True
        return False
    
    def get_visualizer_colors(self) -> List[str]:
        """Get colors for visualizer from current skin"""
        return self.current_colors
    
    def get_skin_theme(self) -> Dict[str, str]:
        """Get theme colors from current skin"""
        if self.current_skin:
            return self.current_skin.colors
        return {}
