# 🐳 Dev Container Setup

This project is configured to run in a Cursor/VS Code dev container for maximum reproducibility and simplicity.

## 🚀 Quick Start

1. **Open in Cursor**: When you open this project, Cursor will detect the `.devcontainer` folder and prompt you to "Reopen in Container"
2. **Click "Reopen in Container"**: Cursor will build and start the container automatically
3. **Wait for setup**: The post-create script will install all dependencies and verify everything works
4. **Start scanning**: Everything is ready to go!

## ✅ What's Included

### Pre-installed Tools

- **Python 3.11** with pip
- **Playwright** with Chromium browser
- **All Python dependencies** from requirements.txt
- **Development tools**: git, vim, nano, htop, jq, yamllint
- **Python dev tools**: ipython, pytest, black, flake8, mypy

### Pre-configured

- **Python path** set correctly
- **Workspace** mounted at `/workspace`
- **Persistent volumes** for results, logs, and config
- **Port forwarding** for tools (ZAP: 8080, Burp: 1337)
- **VS Code extensions** auto-installed

## 📁 Directory Structure

```
/workspace/                    # Project root (mounted from host)
├── tools/                     # Scanner modules
├── config/                    # Configuration files
├── results/                   # Scan results (persistent volume)
├── logs/                      # Application logs (persistent volume)
├── targets/                   # Target definitions
└── ...
```

## 🔧 Configuration

### Environment Variables

- `PYTHONUNBUFFERED=1` - Python output not buffered
- `PYTHONPATH=/workspace:/workspace/tools` - Python can find modules
- `DISPLAY=:99` - For headless browser operations

### Persistent Volumes

- `casino-scanner-results` - Scan results persist between container restarts
- `casino-scanner-logs` - Logs persist between container restarts
- `casino-scanner-config` - Config files persist

## 🎯 Usage

Once the container is running, you can use all commands normally:

```bash
# Run discovery cycle
python3 automated_scanner.py scan

# Check status
python3 automated_scanner.py status

# Start continuous mode
python3 automated_scanner.py start
```

## 🔄 Rebuilding Container

If you need to rebuild the container (after changing Dockerfile or requirements.txt):

1. **Command Palette** (Ctrl+Shift+P / Cmd+Shift+P)
2. Type: "Dev Containers: Rebuild Container"
3. Select it and wait for rebuild

## 🐛 Troubleshooting

### Container won't start

- Check Docker is running: `docker ps`
- Check logs: View container logs in Cursor

### Dependencies missing

- Rebuild container: Command Palette → "Dev Containers: Rebuild Container"
- Or run manually: `pip install -r requirements.txt`

### Playwright browsers not working

- Run: `playwright install chromium`
- Or rebuild container

### Port forwarding issues

- Check ports 8080, 1337, 8081 are available
- Modify `devcontainer.json` to change ports

## 💡 Benefits

✅ **Reproducibility** - Same environment every time  
✅ **Isolation** - Doesn't pollute your host system  
✅ **Simplicity** - Everything pre-configured  
✅ **Team Collaboration** - Same environment for everyone  
✅ **Easy Setup** - Just open and go  

## 📝 Notes

- The container runs as `root` user for simplicity
- All project files are mounted from host (changes persist)
- Results/logs use Docker volumes (persist between rebuilds)
- Network mode is `host` for better connectivity
