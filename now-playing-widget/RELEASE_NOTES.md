# Nova Now Playing Widget - Feature Complete Release

## What's Included

### 🎨 User Interface
- **Nova Themed Design**: Beautiful dark theme with cyan, mint, and orange accents
- **Scrolling Text Display**: Animated title and artist names with multiple effects
  - Glow Effect
  - Pulse Effect
  - Shadow Effect
  - Rainbow Effect
  - Wave Effect
- **Multi-Tab Interface**: Switch between different visualization modes
- **Responsive Controls**: Skin selection, effect control, streaming toggles

### 🎵 Audio Processing
- **Real-time FFT Spectrum Analysis**: 32+ frequency bands
- **Audio Input Support**: Microphone and system audio
- **Demo Mode**: Built-in demo tracks for testing
- **Smooth Frequency Mapping**: Logarithmic scaling with smoothing

### 🎨 Visualizers
- **Built-in Visualizers**:
  - Bar Equalizer (Classic spectrum bars)
  - Waveform Display (Oscilloscope mode)
  - Radial/Circular (Frequency wheel)
- **MilkDrop Integration**: Advanced visualization engine with presets
  - Support for .milk and .milkpre preset files
  - Automatic preset detection
  - Hardware acceleration (if available)
  - Software rendering fallback

### 🎵 Poweramp Integration
- **Skin Loading**: Automatic detection of Poweramp skins
- **Color Extraction**: Extract color palettes from skins
- **Cross-Platform Support**: Windows, macOS, Linux
- **Color Palette Application**: Apply skin colors to visualizers

### 📡 Streaming Features
- **OBS Studio**
  - WebSocket connection
  - Now-playing data streaming
  - Spectrum synchronization
  - Custom source support
- **Camo Virtual Camera**
  - Stream to video apps (Zoom, Teams, etc.)
  - Multiple resolution support (720p, 1080p)
  - Overlay rendering
- **HTTP Web Server**
  - REST API endpoints
  - Browser-based preview
  - JSON data streaming
  - Port 8080 by default

### ⚙️ Configuration
- **Persistent Settings**: Saved configuration in ~/.now_playing_widget/
- **Customizable**:
  - Default theme
  - Audio device selection
  - Visualizer sensitivity
  - Streaming preferences
  - Resolution and framerate

### 📦 Project Structure

```
now-playing-widget/
├── src/
│   ├── app/
│   │   ├── main.py                    # Main application (COMPLETE)
│   │   ├── visualizer.py              # Audio visualization engine
│   │   └── milkdrop_integration.py    # MilkDrop SDK wrapper
│   ├── ui/
│   │   ├── themes.py                  # Nova theme definitions
│   │   └── scrolling_text.py          # Animated text widget
│   ├── audio/
│   │   ├── poweramp_skins.py          # Poweramp skin loader
│   │   └── analyzer.py                # Audio analysis utilities
│   ├── streaming/
│   │   ├── obs_plugin.py              # OBS integration
│   │   ├── camo_plugin.py             # Camo virtual camera
│   │   └── http_server.py             # HTTP web server
│   └── config/
│       └── settings.py                # Configuration management
├── requirements.txt                   # Python dependencies
├── setup.py                           # Package setup
├── INSTALL.md                         # Installation guide
├── QUICKSTART.md                      # Quick start guide
├── README.md                          # Full documentation
└── LICENSE                            # MIT License
```

## Installation & Usage

### Quick Start (5 minutes)
```bash
git clone https://github.com/UrkelTech-Incorp/pg_nova_bot_project.git
cd pg_nova_bot_project/now-playing-widget
python -m venv venv
source venv/bin/activate  # Windows: venv\Scripts\activate
pip install -r requirements.txt
python src/app/main.py
```

### Full Documentation
See **README.md** for comprehensive setup and usage instructions.

## Features Demonstrated

✅ **Scrolling Text with Effects**
- Dynamic animation with multiple effect types
- Color-coded display (title in blue, artist in mint)
- Responsive to track changes
- Smooth transitions

✅ **Audio Visualization**
- Real-time spectrum analysis
- Multiple visualization modes
- Color extraction from Poweramp skins
- Software and hardware rendering

✅ **Streaming Integration**
- OBS Studio WebSocket support
- Camo virtual camera streaming
- HTTP web server API
- Multi-format data export

✅ **MilkDrop SDK**
- Preset loading and management
- Advanced visualization effects
- Fallback rendering
- Category-based preset organization

✅ **Configuration Management**
- Persistent settings storage
- Per-component configuration
- Theme customization
- Easy backup and restoration

## System Requirements

- **Python**: 3.9+
- **OS**: Windows, macOS, or Linux
- **RAM**: 2GB minimum
- **Audio**: Working audio input device
- **Optional**: MilkDrop 2 SDK for advanced visualizations

## Dependencies

- PyQt6 (GUI framework)
- NumPy & SciPy (Audio processing)
- PyAudio (Audio input)
- Pillow (Image processing)
- websocket-client (OBS connection)

See **requirements.txt** for exact versions.

## Streaming Destinations

### OBS Studio
1. Enable WebSocket in OBS Tools → obs-websocket
2. Create Text source named "NowPlaying"
3. Enable "Stream to OBS" in widget
4. Data appears in real-time

### Camo Virtual Camera
1. Install Camo on your system
2. Enable "Stream to Camo" in widget
3. Select "Camo" in video application camera menu
4. Widget appears as virtual camera

### HTTP Web Server
1. Enable "HTTP Server" in widget
2. Open browser to http://localhost:8080
3. See live preview and visualizer
4. API endpoints available at /api/

## Customization

### Change Theme
Edit `config.json`:
```json
"theme": "nova"  // or "nova_light", "nova_dark"
```

### Select Poweramp Skin
Dropdown in main window, or edit:
```json
"poweramp_skin": "skin_name"
```

### Configure Streaming
Edit `config.json` for OBS host, Camo resolution, etc.

### Adjust Visualizer
Settings in config for bar count, smoothing, sensitivity

## Troubleshooting

**MilkDrop not loading?**
- Windows: Install from official MilkDrop website
- Linux: `sudo apt install milkdrop`
- macOS: Brew install or manual installation

**No audio input?**
- Check system audio settings
- Verify device in `config.json`
- Run in demo mode to test UI

**OBS not connecting?**
- Verify OBS is running
- Check WebSocket is enabled
- Look for firewall blocking port 4444

**Camo not detecting?**
- Ensure Camo is installed
- Verify Camo is running
- Check port 1313 is accessible

## Performance Tips

- Use "Low" quality for MilkDrop on older systems
- Reduce bar count for lower CPU usage
- Disable streaming when not needed
- Close other applications for better performance

## Next Steps

- **Spotify Integration**: Real now-playing data
- **YouTube Music Support**: Stream metadata
- **Discord Rich Presence**: Show status in Discord
- **Recording**: Save visualizations to file
- **Themes Editor**: Build custom themes with UI
- **Plugin System**: Create custom visualizers

## License

MIT License - See LICENSE file

## Support & Contribution

- Report bugs: [GitHub Issues](https://github.com/UrkelTech-Incorp/pg_nova_bot_project/issues)
- Discuss features: [GitHub Discussions](https://github.com/UrkelTech-Incorp/pg_nova_bot_project/discussions)
- Contribute: Fork, modify, submit Pull Request

---

**✨ Made with ❤️ by UrkelTech-Incorp**

**Version**: 1.0.0  
**Release Date**: July 2026  
**Status**: Production Ready
