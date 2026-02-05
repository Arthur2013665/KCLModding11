#!/bin/bash

echo "🔍 Checking Bot Status"
echo "=" | head -c 40
echo ""

# Check if bot is running locally
echo "1. Checking local bot processes..."
BOT_PROCESSES=$(ps aux | grep "python.*bot.py" | grep -v grep | wc -l)

if [ $BOT_PROCESSES -eq 0 ]; then
    echo "   ✅ No bot running locally"
elif [ $BOT_PROCESSES -eq 1 ]; then
    echo "   ⚠️  1 bot instance running"
    ps aux | grep "python.*bot.py" | grep -v grep
else
    echo "   ❌ Multiple bot instances running: $BOT_PROCESSES"
    ps aux | grep "python.*bot.py" | grep -v grep
    echo ""
    echo "   Fix: Kill all instances"
    echo "   Command: pkill -9 -f 'python.*bot.py'"
fi

echo ""
echo "2. Checking bot configuration..."
if [ -f ".env" ]; then
    echo "   ✅ .env file exists"
    CLIENT_ID=$(grep "DISCORD_CLIENT_ID" .env | cut -d'=' -f2)
    echo "   Bot Client ID: $CLIENT_ID"
else
    echo "   ❌ .env file not found"
fi

echo ""
echo "3. Common issues with duplicate bots in Discord:"
echo "   • Bot invited to server multiple times"
echo "   • Discord cache showing duplicates"
echo "   • Bot running on another machine"
echo ""
echo "📋 How to fix:"
echo "   1. Server Settings → Members → Check for duplicate bots"
echo "   2. Kick any duplicate bot entries"
echo "   3. Restart Discord to clear cache"
echo "   4. Make sure only ONE bot instance is running"
echo ""
