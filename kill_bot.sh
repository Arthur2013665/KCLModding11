#!/bin/bash

# Kill Discord Bot Script

echo "========================================="
echo "   Discord Bot - Kill Script"
echo "========================================="
echo ""

# Check if running as systemd service
if systemctl is-active --quiet discord-bot 2>/dev/null; then
    echo "Bot is running as a system service"
    echo "Stopping service..."
    sudo systemctl stop discord-bot
    echo "✅ Service stopped"
    echo ""
    echo "To disable auto-start on boot:"
    echo "  sudo systemctl disable discord-bot"
    exit 0
fi

# Find bot processes
PIDS=$(pgrep -f "python.*bot.py")

if [ -z "$PIDS" ]; then
    echo "❌ No bot processes found"
    echo ""
    echo "Bot is not running!"
    exit 1
fi

echo "Found bot process(es):"
ps aux | grep "bot.py" | grep -v grep
echo ""

# Kill processes
echo "Killing bot processes..."
pkill -f "python.*bot.py"

sleep 2

# Verify
REMAINING=$(pgrep -f "python.*bot.py")
if [ -z "$REMAINING" ]; then
    echo "✅ Bot killed successfully"
else
    echo "⚠️  Some processes still running, force killing..."
    pkill -9 -f "python.*bot.py"
    echo "✅ Bot force killed"
fi

echo ""
echo "Bot stopped!"
