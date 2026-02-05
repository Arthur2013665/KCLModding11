# Bot Cleanup Guide

## Problem
You recreated your bot in Discord Developer Portal, but the old bot is still in your servers.

## Understanding the Situation

- **Old Bot**: Still in servers, different Application ID
- **New Bot**: New token in .env, not in servers yet
- **Both exist**: They are separate Discord applications

## Solution Options

### Option 1: Remove Old Bot (Recommended)

**Step 1: Identify the old bot**
- Look at the bot in your server
- Note its username and discriminator

**Step 2: Remove from each server**
1. Go to Server Settings → Members
2. Find the old bot
3. Right-click → Kick
4. Repeat for all servers

**Step 3: Delete old application (optional)**
1. Discord Developer Portal
2. Select old application
3. General Information → Delete Application

### Option 2: Switch Back to Old Bot (Easier)

**Step 1: Get old bot credentials**
1. Discord Developer Portal
2. Select the bot that's IN your servers
3. Bot → Reset Token → Copy
4. General Information → Copy Application ID
5. OAuth2 → General → Copy Client Secret

**Step 2: Update .env**
```env
DISCORD_TOKEN=old_bot_token_here
DISCORD_CLIENT_ID=old_bot_application_id
DISCORD_CLIENT_SECRET=old_bot_client_secret
```

**Step 3: Restart bot**
```bash
./restart.sh
```

### Option 3: Use New Bot, Keep Old Bot

If you want both:
- Old bot stays in servers (inactive)
- New bot joins servers (active)
- Eventually remove old bot when ready

## Recommended Approach

**Use Option 2** (switch back to old bot) because:
- ✅ Bot already in all servers
- ✅ No need to re-invite
- ✅ No need to kick old bot
- ✅ Keeps server integrations
- ✅ Keeps command history

## How to Check Which Bot is Which

### Method 1: Check in Discord
1. Right-click bot in server
2. Copy ID
3. Compare with Application ID in Developer Portal

### Method 2: Decode Token
```bash
# First part of token is base64 encoded bot ID
echo "MTQ0MTUyMTMxNTE1NTU0NjIwMw" | base64 -d
# Output: bot user ID
```

### Method 3: Check Developer Portal
1. Go to each application
2. General Information → Application ID
3. Match with DISCORD_CLIENT_ID in .env

## Current Configuration

Your .env shows:
- **Bot Token**: YOUR_BOT_TOKEN_HERE
- **Client ID**: YOUR_CLIENT_ID_HERE

This is your **NEW bot** (not in servers yet).

## Action Plan

### If you want to use the NEW bot:

1. **Invite new bot**:
   - Get invite URL from Developer Portal
   - Add to all your servers

2. **Remove old bot**:
   - Kick from each server

### If you want to use the OLD bot:

1. **Get old bot credentials** from Developer Portal
2. **Update .env** with old bot token and IDs
3. **Restart bot**: `./restart.sh`
4. **Delete new bot application** (optional)

## Quick Commands

### Restart bot after .env changes
```bash
./restart.sh
```

### Check if bot is running
```bash
ps aux | grep "python.*bot.py"
```

### View bot logs
```bash
tail -f bot.log
```

## Tips

- **One bot per purpose**: Don't run multiple bots with same code
- **Keep credentials safe**: Never share bot tokens
- **Use descriptive names**: Name bots clearly in Developer Portal
- **Document which is which**: Keep notes on which bot is for what

## Need Help?

If you're unsure which bot to use:
1. Check which bot is in your servers (the one users see)
2. Use that bot's credentials
3. This avoids having to re-invite and reconfigure

---

**Recommendation: Use the bot that's already in your servers to avoid complications!**
