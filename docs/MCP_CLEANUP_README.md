# MCP Process Cleanup System

This system automatically prevents MCP (Model Context Protocol) server processes from piling up when you close Cursor.

## 🎯 What It Does

- **Automatic Cleanup**: Runs every 30 minutes to clean up orphaned MCP processes
- **Logout Cleanup**: Kills all MCP processes when you log out
- **Manual Cleanup**: Command-line tool for on-demand cleanup

## 📁 Files

- `cleanup_mcp_processes.sh` - Main cleanup script
- `setup_mcp_cleanup.sh` - Setup script (already run)
- `~/.config/systemd/user/cursor-mcp-cleanup.service` - Systemd service for logout cleanup
- `~/.config/systemd/user/cursor-mcp-cleanup.timer` - Systemd timer for periodic cleanup
- `~/.cursor/mcp-cleanup.log` - Cleanup activity log

## 🚀 Usage

### Manual Cleanup

```bash
# Clean orphaned processes (safe - only kills processes not linked to Cursor)
/home/d/casino/cleanup_mcp_processes.sh

# Force kill ALL MCP processes (use when Cursor is closed)
/home/d/casino/cleanup_mcp_processes.sh --force

# If you added the alias during setup:
cleanup-mcp
cleanup-mcp --force
```

### Check Status

```bash
# Check if timer is running
systemctl --user status cursor-mcp-cleanup.timer

# View cleanup logs
tail -f ~/.cursor/mcp-cleanup.log

# Check how many MCP processes are running
ps aux | grep -E "jailbreak-mcp|mcp-server" | grep -v grep | wc -l
```

### Enable/Disable

```bash
# Disable automatic cleanup
systemctl --user stop cursor-mcp-cleanup.timer
systemctl --user disable cursor-mcp-cleanup.timer

# Re-enable automatic cleanup
systemctl --user enable cursor-mcp-cleanup.timer
systemctl --user start cursor-mcp-cleanup.timer

# Disable logout cleanup
systemctl --user disable cursor-mcp-cleanup.service

# Re-enable logout cleanup
systemctl --user enable cursor-mcp-cleanup.service
```

## 🔧 How It Works

1. **Periodic Cleanup (Timer)**: Every 30 minutes, checks for orphaned MCP processes (processes not linked to a running Cursor instance) and kills them.

2. **Logout Cleanup (Service)**: When you log out, kills all MCP processes to ensure a clean shutdown.

3. **Smart Detection**: The script checks if processes are children of Cursor processes. Only orphaned processes are killed when Cursor is running.

## 📊 Monitoring

View the cleanup log:
```bash
tail -f ~/.cursor/mcp-cleanup.log
```

Example log output:
```
[2025-11-16 16:53:00] Starting MCP cleanup (force=false)
[2025-11-16 16:53:00] Cursor is running, checking for orphaned processes only...
[2025-11-16 16:53:01] Killing orphaned process: PID 12345 - node /home/d/casino/jailbreak-mcp/dist/index.js
[2025-11-16 16:53:01] Cleanup complete. Killed 1 process(es)
```

## ⚙️ Configuration

### Change Cleanup Frequency

Edit `~/.config/systemd/user/cursor-mcp-cleanup.timer`:

```ini
[Timer]
OnUnitActiveSec=30min  # Change to 15min, 1h, etc.
```

Then reload:
```bash
systemctl --user daemon-reload
systemctl --user restart cursor-mcp-cleanup.timer
```

### Disable Automatic Cleanup

If you want to disable automatic cleanup but keep manual cleanup:

```bash
systemctl --user stop cursor-mcp-cleanup.timer
systemctl --user disable cursor-mcp-cleanup.timer
```

## 🐛 Troubleshooting

### Processes Still Piling Up

1. Check if the timer is running:
   ```bash
   systemctl --user status cursor-mcp-cleanup.timer
   ```

2. Check the log for errors:
   ```bash
   tail -20 ~/.cursor/mcp-cleanup.log
   ```

3. Manually run cleanup:
   ```bash
   /home/d/casino/cleanup_mcp_processes.sh --force
   ```

### Timer Not Starting

Make sure systemd user services are enabled:
```bash
# Check if systemd user session is running
systemctl --user status

# If not, you may need to enable lingering (for services to run without login)
loginctl enable-linger $USER
```

## 📝 Notes

- The cleanup script is safe to run while Cursor is open - it only kills orphaned processes
- Use `--force` only when Cursor is closed, as it kills ALL MCP processes
- The timer runs in the background and doesn't require any user interaction
- Logout cleanup ensures a clean state when you log back in

