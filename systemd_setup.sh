#!/bin/bash

# Setup Discord Bot as a System Service (Linux only)
# This makes your bot start automatically on server boot and run forever

echo "========================================="
echo "   Discord Bot - System Service Setup"
echo "========================================="
echo ""

# Check if running as root
if [ "$EUID" -ne 0 ]; then 
    echo "Please run as root (use sudo)"
    exit 1
fi

# Get current directory and user
BOT_DIR=$(pwd)
BOT_USER=$(logname)

echo "Bot directory: $BOT_DIR"
echo "Running as user: $BOT_USER"
echo ""

# Create systemd service file
cat > /etc/systemd/system/discord-bot.service << EOF
[Unit]
Description=Discord Bot
After=network.target

[Service]
Type=simple
User=$BOT_USER
WorkingDirectory=$BOT_DIR
ExecStart=/usr/bin/python3 $BOT_DIR/bot.py
Restart=always
RestartSec=10
StandardOutput=append:$BOT_DIR/bot.log
StandardError=append:$BOT_DIR/bot.log

[Install]
WantedBy=multi-user.target
EOF

echo "✅ Service file created"
echo ""

# Reload systemd
systemctl daemon-reload
echo "✅ Systemd reloaded"
echo ""

# Enable service (start on boot)
systemctl enable discord-bot.service
echo "✅ Service enabled (will start on boot)"
echo ""

# Start service
systemctl start discord-bot.service
echo "✅ Service started"
echo ""

echo "========================================="
echo "   Setup Complete!"
echo "========================================="
echo ""
echo "Commands:"
echo "  Start:   sudo systemctl start discord-bot"
echo "  Stop:    sudo systemctl stop discord-bot"
echo "  Restart: sudo systemctl restart discord-bot"
echo "  Status:  sudo systemctl status discord-bot"
echo "  Logs:    sudo journalctl -u discord-bot -f"
echo ""
echo "Your bot will now:"
echo "  ✅ Start automatically on server boot"
echo "  ✅ Restart automatically if it crashes"
echo "  ✅ Run forever in the background"
echo ""
