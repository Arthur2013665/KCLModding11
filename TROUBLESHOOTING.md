# Troubleshooting Guide

## Common Issues and Solutions

### ModuleNotFoundError: No module named 'config'

**Problem:** Python can't find the config module when running the web dashboard.

**Solutions:**

1. **Run from project root directory:**
   ```bash
   cd /path/to/your/bot
   ./start_web.sh
   ```

2. **Check Python path:**
   ```bash
   python3 test_imports.py
   ```

3. **Verify .env file exists:**
   ```bash
   ls -la .env
   ```
   If missing, copy from example:
   ```bash
   cp .env.example .env
   ```

4. **Install dependencies:**
   ```bash
   source .venv/bin/activate
   pip install -r requirements.txt
   pip install -r web/requirements.txt
   ```

### ModuleNotFoundError: No module named 'discord'

**Problem:** Discord.py not installed.

**Solution:**
```bash
source .venv/bin/activate
pip install -r requirements.txt
```

### ModuleNotFoundError: No module named 'flask'

**Problem:** Flask not installed.

**Solution:**
```bash
source .venv/bin/activate
pip install -r web/requirements.txt
```

### Database Errors

**Problem:** Can't access database.

**Solutions:**

1. **Create data directory:**
   ```bash
   mkdir -p data
   ```

2. **Check permissions:**
   ```bash
   chmod 755 data
   ```

3. **Reset database:**
   ```bash
   rm data/bot.db
   python bot.py  # Will recreate tables
   ```

### Web Dashboard Won't Start

**Problem:** Flask server fails to start.

**Solutions:**

1. **Check port 5001 is free:**
   ```bash
   lsof -i :5001
   ```
   If in use, kill the process or use a different port:
   ```bash
   kill -9 <PID>
   # Or set FLASK_PORT=8080 in .env
   ```
   
   **Note:** Port 5000 is used by macOS AirPlay Receiver. We use 5001 instead.

2. **Check environment variables:**
   ```bash
   cat .env | grep DISCORD_CLIENT
   ```

3. **Run manually to see errors:**
   ```bash
   source .venv/bin/activate
   cd web
   python app.py
   ```

### Bot Won't Start

**Problem:** Bot fails to connect.

**Solutions:**

1. **Check token:**
   ```bash
   cat .env | grep DISCORD_TOKEN
   ```

2. **Verify token is valid:**
   - Go to Discord Developer Portal
   - Check bot token hasn't been regenerated

3. **Check intents:**
   - Enable "Message Content Intent" in Developer Portal

### FFmpeg Not Found

**Problem:** Music commands fail with FFmpeg error.

**Solutions:**

**macOS:**
```bash
brew install ffmpeg
```

**Ubuntu/Debian:**
```bash
sudo apt update
sudo apt install ffmpeg
```

**Verify installation:**
```bash
ffmpeg -version
```

### OAuth2 Login Fails

**Problem:** Can't login to web dashboard.

**Solutions:**

1. **Check redirect URI:**
   - Discord Developer Portal → OAuth2
   - Must be exactly: `http://localhost:5001/callback`

2. **Check credentials in .env:**
   ```bash
   cat .env | grep DISCORD_CLIENT
   ```

3. **Verify CLIENT_ID and CLIENT_SECRET:**
   - Copy from Discord Developer Portal
   - No extra spaces or quotes

### Library Items Not Playing

**Problem:** `/play ggg` doesn't work.

**Solutions:**

1. **Check file was uploaded:**
   - Open web dashboard
   - Go to Media Library
   - Verify "ggg" exists

2. **Check database:**
   ```bash
   sqlite3 data/bot.db "SELECT * FROM custom_media;"
   ```

3. **Check file path:**
   ```bash
   ls -la web/uploads/
   ```

4. **Re-upload file:**
   - Delete from library
   - Upload again

### Permission Errors

**Problem:** Bot can't perform actions.

**Solutions:**

1. **Check bot permissions:**
   - Server Settings → Roles
   - Verify bot role has required permissions

2. **Required permissions:**
   - Send Messages
   - Embed Links
   - Attach Files
   - Connect (voice)
   - Speak (voice)
   - Manage Messages (for moderation)

### Import Errors

**Problem:** Various import errors.

**Solution - Run test script:**
```bash
python3 test_imports.py
```

This will show which imports are failing.

### Virtual Environment Issues

**Problem:** Commands not found or wrong Python version.

**Solutions:**

1. **Activate virtual environment:**
   ```bash
   source .venv/bin/activate
   ```

2. **Verify activation:**
   ```bash
   which python
   # Should show: /path/to/project/.venv/bin/python
   ```

3. **Recreate virtual environment:**
   ```bash
   rm -rf .venv
   python3 -m venv .venv
   source .venv/bin/activate
   pip install -r requirements.txt
   pip install -r web/requirements.txt
   ```

## Diagnostic Commands

### Check Python Version
```bash
python3 --version
# Should be 3.10 or higher
```

### Check Installed Packages
```bash
source .venv/bin/activate
pip list
```

### Check Bot Status
```bash
tail -f bot.log
```

### Check Database Tables
```bash
sqlite3 data/bot.db ".tables"
```

### Check Environment Variables
```bash
cat .env
```

### Test Database Connection
```bash
sqlite3 data/bot.db "SELECT COUNT(*) FROM custom_media;"
```

## Getting Help

If issues persist:

1. **Check logs:**
   ```bash
   cat bot.log
   ```

2. **Run test imports:**
   ```bash
   python3 test_imports.py
   ```

3. **Verify all files exist:**
   ```bash
   ls -la config.py bot.py web/app.py
   ```

4. **Check file permissions:**
   ```bash
   ls -la start.sh start_web.sh
   ```

## Quick Fixes

### Reset Everything
```bash
# Stop all processes
pkill -f "python.*bot.py"
pkill -f "python.*app.py"

# Clean up
rm -rf .venv
rm data/bot.db

# Reinstall
./install_web.sh

# Restart
./start.sh
./start_web.sh
```

### Fresh Start
```bash
# Backup .env
cp .env .env.backup

# Clean install
rm -rf .venv data
./install_web.sh

# Restore .env
cp .env.backup .env

# Start
./start.sh
./start_web.sh
```

## Error Messages

### "PrivilegedIntentsRequired"
**Fix:** Enable intents in Discord Developer Portal → Bot → Privileged Gateway Intents

### "Forbidden: 403"
**Fix:** Check bot has required permissions in server

### "Connection refused"
**Fix:** Check bot token is valid and bot is invited to server

### "File not found"
**Fix:** Check file paths are correct and files exist

### "Database is locked"
**Fix:** Close other connections to database, restart bot

## Prevention

### Best Practices

1. **Always run from project root:**
   ```bash
   cd /path/to/bot
   ./start.sh
   ```

2. **Use virtual environment:**
   ```bash
   source .venv/bin/activate
   ```

3. **Keep dependencies updated:**
   ```bash
   pip install --upgrade -r requirements.txt
   ```

4. **Backup database regularly:**
   ```bash
   cp data/bot.db data/bot.db.backup
   ```

5. **Check logs regularly:**
   ```bash
   tail -f bot.log
   ```

## Still Having Issues?

1. Run the test script: `python3 test_imports.py`
2. Check the logs: `cat bot.log`
3. Verify configuration: `cat .env`
4. Try fresh install: `./install_web.sh`

---

**Most issues are solved by running from the correct directory and having all dependencies installed!**
