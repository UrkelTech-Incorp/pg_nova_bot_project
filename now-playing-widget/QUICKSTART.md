# Quick Start Guide

## 5-Minute Setup

### Windows Users

1. **Download & Install Python 3.11**
   - Visit: https://www.python.org/downloads/
   - Run installer with "Add Python to PATH" checked

2. **Open Command Prompt & Run:**
   ```cmd
   git clone https://github.com/UrkelTech-Incorp/pg_nova_bot_project.git
   cd pg_nova_bot_project\now-playing-widget
   python -m venv venv
   venv\Scripts\activate
   pip install -r requirements.txt
   python src/app/main.py
   ```

### macOS Users

```bash
python3 -m venv venv
source venv/bin/activate
pip install -r requirements.txt
python3 src/app/main.py
```

### Linux Users

```bash
sudo apt install python3.11 python3.11-venv portaudio19-dev
python3.11 -m venv venv
source venv/bin/activate
pip install -r requirements.txt
python3 src/app/main.py
```

## What You Get

✅ Beautiful Nova-themed UI  
✅ Real-time audio visualizer  
✅ Poweramp skin support  
✅ OBS Studio streaming  
✅ Camo virtual camera integration  

## Next Steps

1. Select a Poweramp skin from the dropdown
2. Toggle OBS/Camo streaming as needed
3. Adjust settings in config.json

See **README.md** for full documentation!
