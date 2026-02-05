#!/bin/bash

# Restart bot script

echo "🔄 Restarting Discord Bot..."
echo ""

# Stop the bot
echo "⏹️  Stopping bot..."
pkill -f "python.*bot.py"
sleep 2

# Check if stopped
if pgrep -f "python.*bot.py" > /dev/null; then
    echo "⚠️  Bot still running, force killing..."
    pkill -9 -f "python.*bot.py"
    sleep 1
fi

echo "✅ Bot stopped"
echo ""

# Start the bot
echo "▶️  Starting bot..."
./start.sh &

echo ""
echo "✅ Bot restarted!"
echo ""
echo "📋 Next steps:"
echo "1. Wait for 'Commands synced' message in logs"
echo "2. Wait 1-2 minutes for Discord to update"
echo "3. Type / in Discord to see commands"
echo ""
echo "📊 Check logs: tail -f bot.log"
echo ""
