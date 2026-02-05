#!/bin/bash

# Discord Bot Setup Script
# One-time setup for bot and web dashboard

echo "🤖 Discord Bot Setup"
echo "===================="
echo ""

# Check if .env exists
if [ ! -f ".env" ]; then
    echo "📝 Creating .env file..."
    cp .env.example .env
    echo "✅ .env file created"
    echo ""
    echo "⚠️  IMPORTANT: Edit .env with your Discord credentials!"
    echo "   Required: DISCORD_TOKEN, DISCORD_CLIENT_ID, DISCORD_CLIENT_SECRET"
    echo ""
fi

# Create virtual environment if needed
if [ ! -d ".venv" ]; then
    echo "📦 Creating virtual environment..."
    python3 -m venv .venv
    echo "✅ Virtual environment created"
fi

# Activate virtual environment
echo "🔧 Activating virtual environment..."
source .venv/bin/activate

# Install dependencies
echo "📥 Installing dependencies..."
pip install -q -r requirements.txt
pip install -q -r web/requirements.txt
echo "✅ Dependencies installed"

# Create directories
mkdir -p data web/uploads
echo "✅ Directories created"

# Migrate database if exists
if [ -f "data/bot.db" ]; then
    echo "🔄 Migrating database..."
    python3 migrate_database.py
fi

# Check FFmpeg
if command -v ffmpeg &> /dev/null; then
    echo "✅ FFmpeg is installed"
else
    echo "⚠️  FFmpeg not found (needed for music)"
    echo "   Install: brew install ffmpeg (macOS)"
fi

echo ""
echo "🎉 Setup complete!"
echo ""
echo "Next steps:"
echo "1. Edit .env with your Discord credentials"
echo "2. Start bot: ./start.sh"
echo "3. Bot is ready to use!"
echo ""
