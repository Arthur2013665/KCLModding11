# Commands Not Showing - Fix Guide

## ✅ Good News

The giveaway commands are loaded correctly! Test results show:
- ✅ `giveaway-start`
- ✅ `giveaway-end`
- ✅ `giveaway-reroll`
- ✅ `giveaway-list`

## Why Commands Don't Show

Discord slash commands need to be **synced** with Discord's servers. This happens when:
1. Bot starts up
2. Bot calls `await bot.tree.sync()`
3. Discord updates the command list (can take 1-5 minutes)

## 🔧 How to Fix

### Step 1: Restart the Bot

```bash
# Stop the bot if running
pkill -f "python.*bot.py"

# Start the bot
./start.sh
```

### Step 2: Wait for Sync Message

Look for this in the logs:
```
INFO - Loaded cog: giveaway
INFO - Syncing commands with Discord...
INFO - Commands synced
INFO - Bot is ready!
```

### Step 3: Wait 1-5 Minutes

Discord needs time to update the command list globally. This can take:
- **Instant to 1 minute**: In your test server
- **Up to 5 minutes**: Globally across all servers

### Step 4: Check in Discord

1. Type `/` in any channel
2. Look for commands starting with `giveaway-`
3. You should see all 4 giveaway commands

## 🚀 Quick Fix Commands

```bash
# One-line restart
pkill -f "python.*bot.py" && sleep 2 && ./start.sh

# Or use the restart script
./start.sh
```

## 🔍 Troubleshooting

### Commands Still Not Showing After 5 Minutes?

#### 1. Check Bot Logs
```bash
tail -f bot.log
```

Look for:
- ✅ "Loaded cog: giveaway"
- ✅ "Commands synced"
- ❌ Any error messages

#### 2. Check Bot Permissions

The bot needs these permissions:
- ✅ Use Application Commands
- ✅ Send Messages
- ✅ Embed Links
- ✅ Add Reactions

#### 3. Force Sync (if needed)

If commands still don't show, you can force a global sync:

Edit `bot.py` temporarily and change:
```python
# Find this line in setup_hook():
await self.tree.sync()

# Change to:
await self.tree.sync()  # Sync to current guild
# await self.tree.sync(guild=discord.Object(id=YOUR_GUILD_ID))  # Force sync to specific guild
```

Then restart the bot.

#### 4. Check Discord Developer Portal

1. Go to https://discord.com/developers/applications
2. Select your bot
3. Go to "OAuth2" → "URL Generator"
4. Make sure "applications.commands" scope is checked
5. If not, re-invite the bot with the new URL

### Commands Show But Don't Work?

#### Check Permissions
- User needs "Manage Server" permission for start/end/reroll
- Bot needs "Manage Messages" and "Add Reactions"

#### Check Database
```bash
sqlite3 data/bot.db "SELECT name FROM sqlite_master WHERE type='table' AND name='giveaways';"
```

Should return: `giveaways`

If not, run:
```bash
python3 migrate_database.py
```

## 📊 Verification Checklist

- [ ] Bot is running (`./start.sh`)
- [ ] "Commands synced" appears in logs
- [ ] Waited at least 2 minutes
- [ ] Typed `/` in Discord
- [ ] Bot has "Use Application Commands" permission
- [ ] Bot was invited with correct scopes

## 🎯 Expected Behavior

When working correctly:

1. **Type `/give`** in Discord
2. **See autocomplete** with:
   - `/giveaway-start`
   - `/giveaway-end`
   - `/giveaway-reroll`
   - `/giveaway-list`

3. **Select a command** and see parameter hints

## 💡 Pro Tips

### Instant Command Updates (Development)

For faster testing, sync to a specific guild:

```python
# In bot.py, setup_hook():
# Add this for instant updates in your test server
guild = discord.Object(id=YOUR_GUILD_ID)
self.tree.copy_global_to(guild=guild)
await self.tree.sync(guild=guild)
await self.tree.sync()  # Also sync globally
```

Replace `YOUR_GUILD_ID` with your server ID.

### Check Command Count

Discord has a limit of 100 global slash commands. Check how many you have:

```python
# In bot.py, after sync:
commands = await self.tree.fetch_commands()
logger.info(f"Total commands: {len(commands)}")
```

## 🔄 Quick Restart Script

Create `restart.sh`:
```bash
#!/bin/bash
echo "🔄 Restarting bot..."
pkill -f "python.*bot.py"
sleep 2
./start.sh
echo "✅ Bot restarted!"
```

```bash
chmod +x restart.sh
./restart.sh
```

## ✅ Summary

**The commands are loaded correctly!** They just need to be synced with Discord.

**Quick Fix:**
1. Restart bot: `./start.sh`
2. Wait for "Commands synced" in logs
3. Wait 1-2 minutes
4. Type `/` in Discord
5. Commands should appear!

If they still don't show after 5 minutes, check the troubleshooting section above.

---

**Need more help?** Check `bot.log` for error messages.
