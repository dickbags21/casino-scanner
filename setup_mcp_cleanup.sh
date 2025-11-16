#!/bin/bash
# Setup script for automatic MCP process cleanup

set -e

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
CLEANUP_SCRIPT="$SCRIPT_DIR/cleanup_mcp_processes.sh"
SYSTEMD_USER_DIR="$HOME/.config/systemd/user"
SERVICE_FILE="$SYSTEMD_USER_DIR/cursor-mcp-cleanup.service"
TIMER_FILE="$SYSTEMD_USER_DIR/cursor-mcp-cleanup.timer"

echo "🔧 Setting up MCP process cleanup..."

# Ensure cleanup script is executable
chmod +x "$CLEANUP_SCRIPT"
echo "✅ Cleanup script is ready: $CLEANUP_SCRIPT"

# Create systemd user directory if it doesn't exist
mkdir -p "$SYSTEMD_USER_DIR"

# Reload systemd user daemon
if command -v systemctl >/dev/null 2>&1; then
    systemctl --user daemon-reload
    echo "✅ Systemd user daemon reloaded"
    
    # Enable the timer (periodic cleanup every 30 minutes)
    if [ -f "$TIMER_FILE" ]; then
        systemctl --user enable cursor-mcp-cleanup.timer
        systemctl --user start cursor-mcp-cleanup.timer
        echo "✅ Periodic cleanup timer enabled (runs every 30 minutes)"
    fi
    
    # Enable the service (cleanup on logout)
    if [ -f "$SERVICE_FILE" ]; then
        systemctl --user enable cursor-mcp-cleanup.service
        echo "✅ Logout cleanup service enabled"
    fi
else
    echo "⚠️  systemctl not found, skipping systemd setup"
fi

# Add to bashrc/zshrc for manual cleanup on shell exit (optional)
SHELL_RC=""
if [ -f "$HOME/.bashrc" ]; then
    SHELL_RC="$HOME/.bashrc"
elif [ -f "$HOME/.zshrc" ]; then
    SHELL_RC="$HOME/.zshrc"
fi

if [ -n "$SHELL_RC" ] && ! grep -q "cleanup_mcp_processes" "$SHELL_RC"; then
    echo ""
    echo "📝 Add this to your $SHELL_RC for manual cleanup:"
    echo "   alias cleanup-mcp='$CLEANUP_SCRIPT'"
    echo ""
    read -p "Add alias to $SHELL_RC? (y/n) " -n 1 -r
    echo
    if [[ $REPLY =~ ^[Yy]$ ]]; then
        echo "" >> "$SHELL_RC"
        echo "# Cursor MCP cleanup alias" >> "$SHELL_RC"
        echo "alias cleanup-mcp='$CLEANUP_SCRIPT'" >> "$SHELL_RC"
        echo "✅ Alias added to $SHELL_RC"
        echo "   Run 'source $SHELL_RC' or restart your shell to use 'cleanup-mcp'"
    fi
fi

echo ""
echo "✅ Setup complete!"
echo ""
echo "📋 Available commands:"
echo "   $CLEANUP_SCRIPT          - Clean orphaned MCP processes"
echo "   $CLEANUP_SCRIPT --force  - Kill all MCP processes"
echo "   cleanup-mcp              - If alias was added"
echo ""
echo "📊 Check cleanup logs:"
echo "   tail -f ~/.cursor/mcp-cleanup.log"
echo ""
echo "🔄 Check timer status:"
echo "   systemctl --user status cursor-mcp-cleanup.timer"
echo ""

