#!/bin/bash

echo "========================================"
echo "   Discord Bot Launcher"
echo "========================================"
echo ""
echo "Starting Discord bot..."
echo ""

# Change to the script directory first
cd "$(dirname "$0")"

# Use Windows Python since packages are installed there
/mnt/c/Users/user/AppData/Local/Microsoft/WindowsApps/python.exe bot.py

echo ""
echo "Bot has stopped."
