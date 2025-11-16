#!/bin/bash
# Cleanup script for orphaned MCP server processes
# This script kills MCP processes that are no longer associated with a running Cursor instance

set -euo pipefail

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
LOG_FILE="${HOME}/.cursor/mcp-cleanup.log"

# Function to log messages
log() {
    echo "[$(date '+%Y-%m-%d %H:%M:%S')] $*" | tee -a "$LOG_FILE"
}

# Function to check if Cursor is running
is_cursor_running() {
    pgrep -f "/usr/share/cursor/cursor" > /dev/null 2>&1
}

# Function to get Cursor process PIDs
get_cursor_pids() {
    pgrep -f "/usr/share/cursor/cursor" 2>/dev/null || echo ""
}

# Function to get MCP processes
get_mcp_processes() {
    ps aux | grep -E "jailbreak-mcp|mcp-server|ref-tools-mcp" | grep -v grep | grep -v "$0" || true
}

# Function to check if a process is a child of Cursor
is_cursor_child() {
    local pid=$1
    local cursor_pids=$2
    
    if [ -z "$cursor_pids" ]; then
        return 1
    fi
    
    # Check if process is a direct child or descendant of any Cursor process
    local ppid=$(ps -o ppid= -p "$pid" 2>/dev/null | tr -d ' ')
    
    while [ -n "$ppid" ] && [ "$ppid" != "1" ]; do
        for cursor_pid in $cursor_pids; do
            if [ "$ppid" = "$cursor_pid" ]; then
                return 0
            fi
        done
        ppid=$(ps -o ppid= -p "$ppid" 2>/dev/null | tr -d ' ')
    done
    
    return 1
}

# Main cleanup function
cleanup_orphaned_mcp() {
    local force=${1:-false}
    local killed_count=0
    
    log "Starting MCP cleanup (force=$force)"
    
    if [ "$force" = "false" ] && is_cursor_running; then
        log "Cursor is running, checking for orphaned processes only..."
        local cursor_pids=$(get_cursor_pids)
        
        while IFS= read -r line; do
            if [ -z "$line" ]; then
                continue
            fi
            
            local pid=$(echo "$line" | awk '{print $2}')
            local cmd=$(echo "$line" | awk '{for(i=11;i<=NF;i++) printf "%s ", $i; print ""}')
            
            if ! is_cursor_child "$pid" "$cursor_pids"; then
                log "Killing orphaned process: PID $pid - $cmd"
                kill "$pid" 2>/dev/null && ((killed_count++)) || true
            fi
        done <<< "$(get_mcp_processes)"
    else
        if [ "$force" = "true" ]; then
            log "Force mode: Killing all MCP processes"
        else
            log "Cursor is not running, cleaning up all MCP processes"
        fi
        
        while IFS= read -r line; do
            if [ -z "$line" ]; then
                continue
            fi
            
            local pid=$(echo "$line" | awk '{print $2}')
            local cmd=$(echo "$line" | awk '{for(i=11;i<=NF;i++) printf "%s ", $i; print ""}')
            
            log "Killing process: PID $pid - $cmd"
            kill "$pid" 2>/dev/null && ((killed_count++)) || true
        done <<< "$(get_mcp_processes)"
    fi
    
    # Wait a bit and force kill any that didn't die
    sleep 1
    while IFS= read -r line; do
        if [ -z "$line" ]; then
            continue
        fi
        local pid=$(echo "$line" | awk '{print $2}')
        if kill -0 "$pid" 2>/dev/null; then
            log "Force killing stuck process: PID $pid"
            kill -9 "$pid" 2>/dev/null && ((killed_count++)) || true
        fi
    done <<< "$(get_mcp_processes)"
    
    log "Cleanup complete. Killed $killed_count process(es)"
    echo "$killed_count"
}

# Handle command line arguments
case "${1:-}" in
    --force|-f)
        cleanup_orphaned_mcp true
        ;;
    --help|-h)
        echo "Usage: $0 [OPTIONS]"
        echo ""
        echo "Options:"
        echo "  --force, -f    Kill all MCP processes regardless of Cursor state"
        echo "  --help, -h     Show this help message"
        echo ""
        echo "Without options, only orphaned processes are killed."
        exit 0
        ;;
    *)
        cleanup_orphaned_mcp false
        ;;
esac

