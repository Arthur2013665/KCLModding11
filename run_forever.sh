#!/bin/bash

# Discord Bot - Run Forever Script
# This script keeps your bot running 24/7 with auto-restart

echo "========================================="
echo "   Discord Bot - Forever Runner"
echo "========================================="
echo ""

# Install dependencies if needed
if [ ! -d ".venv" ]; then
    echo "Installing dependencies..."
    python3 -m venv .venv
    source .venv/bin/activate
    pip install -r requirements.txt
else
    source .venv/bin/activate
fi

# Function to run bot with auto-restart
run_bot() {
    while true; do
        echo ""
        echo "========================================="
        echo "Starting bot at $(date)"
        echo "========================================="
        
        # Run the bot
        python3 bot.py
        
        # If bot crashes, wait 5 seconds and restart
        EXIT_CODE=$?
        echo ""
        echo "Bot stopped with exit code: $EXIT_CODE"
        echo "Restarting in 5 seconds..."
        sleep 5
    done
}

# Run in background with nohup (keeps running after terminal closes)
if [ "$1" == "background" ]; then
    echo "Starting bot in background mode..."
    nohup bash -c "$(declare -f run_bot); run_bot" > bot_output.log 2>&1 &
    echo "Bot started! PID: $!"
    echo "Logs: tail -f bot_output.log"
    echo "Stop: kill $!"
else
    # Run in foreground
    run_bot
fi
