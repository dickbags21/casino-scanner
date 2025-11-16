#!/bin/bash
# Simple runner script - no Docker needed!

cd "$(dirname "$0")"

# Run the casino scanner
python3 casino_scanner.py "$@"

