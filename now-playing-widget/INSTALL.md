# Nova Now Playing Widget - Installation Guide

## Complete Installation Instructions

### Prerequisites Checklist

- [ ] Python 3.9+ installed
- [ ] Git installed (for cloning)
- [ ] 2GB RAM available
- [ ] Working internet connection
- [ ] Audio input device (microphone or system audio)

---

## Method 1: Standard Installation (Recommended)

### Step 1: Clone the Repository

**Windows (Command Prompt):**
```cmd
git clone https://github.com/UrkelTech-Incorp/pg_nova_bot_project.git
cd pg_nova_bot_project\now-playing-widget
```

**macOS/Linux (Terminal):**
```bash
git clone https://github.com/UrkelTech-Incorp/pg_nova_bot_project.git
cd pg_nova_bot_project/now-playing-widget
```

### Step 2: Create Virtual Environment

**Windows:**
```cmd
python -m venv venv
venv\Scripts\activate
```

**macOS/Linux:**
```bash
python3 -m venv venv
source venv/bin/activate
```

### Step 3: Install Dependencies

```bash
pip install --upgrade pip
pip install -r requirements.txt
```

### Step 4: Run Application

```bash
python src/app/main.py
```

---

## Method 2: Docker Installation

**Coming Soon!**

Dockerfile and docker-compose files will be available for containerized deployment.

---

## Method 3: Executable Build

### Download Pre-built Binaries

Visit the [Releases Page](https://github.com/UrkelTech-Incorp/pg_nova_bot_project/releases) and download:

- `now-playing-widget-1.0.0-windows.exe` (Windows)
- `now-playing-widget-1.0.0-macos.dmg` (macOS)
- `now-playing-widget-1.0.0-linux.AppImage` (Linux)

Simply extract and run!

---

## Troubleshooting Installation

### Python Not Found

**Error:** `'python' is not recognized as an internal or external command`

**Solution:**
1. Reinstall Python with "Add Python to PATH" checked
2. Or use full path: `C:\Python311\python.exe` (Windows)

### Permission Denied (Linux/macOS)

**Error:** `Permission denied: './venv/bin/activate'`

**Solution:**
```bash
chmod +x venv/bin/activate
source venv/bin/activate
```

### PyAudio Installation Failed

**Windows:**
```bash
pip install pipwin
pipwin install pyaudio
```

**macOS:**
```bash
brew install portaudio
pip install pyaudio
```

**Linux:**
```bash
sudo apt install portaudio19-dev
pip install pyaudio
```

### PyQt6 Issues

**Windows/macOS:**
```bash
pip install --upgrade PyQt6
```

**Linux:**
```bash
sudo apt install libqt6gui6 libqt6widgets6
pip install --upgrade PyQt6
```

---

## Verify Installation

Run this to check all dependencies are installed:

```bash
python -c "import PyQt6, numpy, scipy, pyaudio; print('✓ All dependencies OK!')"
```

Expected output:
```
✓ All dependencies OK!
```

---

## First Run

1. Launch the application:
   ```bash
   python src/app/main.py
   ```

2. You should see the Nova Now Playing Widget window

3. Select a Poweramp skin from the dropdown

4. Enable streaming if desired:
   - OBS: Check "Stream to OBS"
   - Camo: Check "Stream to Camo"

5. Play audio and watch the visualizer respond!

---

## Next Steps

- Read the full [README.md](README.md)
- Configure [settings](#configuration)
- Setup [OBS Integration](#obs-integration)
- Setup [Camo Streaming](#camo-streaming)

---

## Need Help?

1. Check the [Troubleshooting](README.md#troubleshooting) section
2. Search [Existing Issues](https://github.com/UrkelTech-Incorp/pg_nova_bot_project/issues)
3. Open a [New Issue](https://github.com/UrkelTech-Incorp/pg_nova_bot_project/issues/new)
4. Join [Discussions](https://github.com/UrkelTech-Incorp/pg_nova_bot_project/discussions)

---

**Last Updated:** 2026-07-19
