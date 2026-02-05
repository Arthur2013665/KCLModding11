# Discord Bot

A comprehensive Discord bot with moderation, economy, giveaways, and logging features built in Python using discord.py.

## Features

### 🛡️ Moderation
- **User Actions**: `/ban`, `/unban`, `/kick`, `/timeout`, `/warn`, `/warnings`, `/clearwarnings`
- **Message Management**: `/purge` with filters (user, bots, embeds, files, contains text)
- **Channel Management**: `/lock`, `/unlock`, `/slowmode`, `/nuke`
- **Role Management**: `/role` (add/remove), `/nickname`
- **Logging**: `/modlogs`, `/case`, `/setmodlog`

### 🤖 Auto-Moderation
- Spam detection (5 messages in 3 seconds)
- Blacklist word filtering
- Excessive caps detection (70% threshold)
- Discord invite link blocking
- Mass mention detection
- Configurable with `/automod` and `/blacklist`

### 💰 Economy System
- `/balance` - Check balance and level
- `/daily` - Daily reward (24h cooldown)
- `/work` - Earn money by working
- `/beg` - Beg for small amounts
- `/rob` - Attempt to rob other users
- `/pay` - Transfer money to others
- `/leaderboard` - View top users by balance or level

### 📊 Leveling System
- Automatic XP gain from messages (60s cooldown)
- Level-up announcements
- `/level` - Check level and XP progress
- Integrated with economy profile

### 🎉 Giveaway System
- `/gstart` - Start a new giveaway with custom duration, winners, requirements, and level filtering
- `/gend` - End a giveaway early
- `/greroll` - Reroll giveaway winners
- `/glist` - List all active giveaways
- Automatic winner selection
- Support for multiple winners
- Level requirement filtering
- Flexible duration (seconds, minutes, hours, days)

### 📝 Comprehensive Logging
- `/setbotlog` - Set up bot activity logging channel
- **Logs everything:**
  - Command usage
  - Member joins/leaves
  - Bans/unbans
  - Message edits/deletes
  - Channel creation/deletion
  - Role creation/deletion/updates
  - Member role changes
  - Bot startup/shutdown
  - Errors and warnings

## 🚀 Deployment

### Local Hosting
```bash
pip install -r requirements.txt
python3 bot.py
```

### Forever Running (Self-Hosted)
```bash
./run_forever.sh background  # Run in background with auto-restart
./kill_bot.sh                # Stop the bot
```

Or as a system service (Linux):
```bash
sudo ./systemd_setup.sh      # Set up as system service
sudo systemctl start discord-bot
```

### Render.com Hosting (Free 24/7)
Deploy to Render.com for free 24/7 hosting:

1. Push code to GitHub
2. Create **Background Worker** on Render (not Web Service!)
3. Add `DISCORD_TOKEN` environment variable
4. Deploy!

See [RENDER_DEPLOYMENT_GUIDE.md](RENDER_DEPLOYMENT_GUIDE.md) for detailed instructions.

### 🎮 Fun Commands
- `/8ball` - Magic 8-ball
- `/coinflip` - Flip a coin
- `/dice` - Roll dice
- `/joke` - Random joke
- `/fact` - Random fact
- `/quote` - Inspirational quote
- `/roast` / `/compliment` - Roast or compliment users
- `/ship` - Ship two users
- `/choose` - Choose between options
- `/reverse` / `/mock` - Text manipulation
- `/rate` - Rate something
- `/howgay`, `/pp`, `/iq`, `/simprate` - Joke calculators
- `/hack` - Fake hack animation

### 🔧 Utility Commands
- `/userinfo` - User information
- `/serverinfo` - Server statistics
- `/avatar` - Display user avatar
- `/poll` - Create polls with reactions
- `/remind` - Set reminders
- `/afk` - Set AFK status
- `/ping` - Bot latency
- `/uptime` - Bot uptime
- `/invite` - Bot invite link
- `/help` - Command list
- `/commands` - List all available commands

### 🎨 Custom Commands
- `/customcmd-add` - Create custom commands
- `/customcmd-remove` - Delete custom commands
- `/customcmd-list` - List all custom commands
- `/customcmd-info` - View command details
- Variable support: `{user}`, `{server}`, `{members}`, `{channel}`

### 👋 Welcome/Goodbye System
- `/setwelcome` - Configure welcome messages
- `/setgoodbye` - Configure goodbye messages
- `/testwelcome` / `/testgoodbye` - Test messages
- Variable support for personalized messages



## Setup

### Prerequisites

- Python 3.11 or higher
- Discord bot token (from [Discord Developer Portal](https://discord.com/developers/applications))
- **Required Discord Intents:** Server Members Intent, Message Content Intent

### Installation

1. **Install Python dependencies:**
```bash
pip install -r requirements.txt
```

2. **Configure the bot:**
   - Copy `.env.example` to `.env`
   - Add your Discord bot token to `.env`

3. **Enable Discord Intents:**
   - Go to [Discord Developer Portal](https://discord.com/developers/applications)
   - Select your bot → Bot section
   - Enable **Server Members Intent** and **Message Content Intent**

4. **Run the bot:**
```bash
python3 bot.py
```

### First Time Setup

After the bot starts:

1. **Invite the bot to your server** using the invite link from `/invite`
2. **Set up bot logging:** `/setbotlog #log-channel`
3. **Set up moderation logging:** `/setmodlog #mod-log-channel`
4. **Configure auto-moderation:** `/automod all true`
5. **Add blacklisted words:** `/blacklist add word`

## Configuration

The `.env` file contains:

- `DISCORD_TOKEN`: Your Discord bot token (required)
- `DATABASE_PATH`: SQLite database location (default: ./data/bot.db)
- `PREFIX`: Text command prefix (default: -)

## Bot Permissions

Required Discord permissions:
- ✅ Administrator (recommended) OR:
  - Manage Messages
  - Manage Roles
  - Manage Channels
  - Kick Members
  - Ban Members
  - Moderate Members (timeouts)
  - Send Messages
  - Embed Links
  - Attach Files
  - Read Message History
  - Add Reactions
  - Connect (voice)
  - Speak (voice)

## Command Categories

### 🛡️ Moderation
Ban, kick, timeout, warn, purge, lock, unlock, slowmode, nuke, role management, moderation logs

### 💰 Economy
Balance, daily, work, beg, rob, pay, leaderboard, level

### 🎉 Giveaways
Start, end, reroll, list - with level requirements and custom requirements

### 📝 Logging
Bot activity logging, moderation logging - tracks everything from commands to role changes

### 🎮 Fun
8ball, coinflip, dice, joke, fact, quote, roast, compliment, ship, choose, and more

### 🔧 Utility
Userinfo, serverinfo, avatar, poll, remind, afk, ping, uptime, invite, help, commands

### 🎨 Custom Commands
Add, remove, list, info

### 👋 Events
Set welcome, set goodbye, test messages

### 🤖 Auto-Moderation
Configure automod, manage blacklist

## Troubleshooting

**Bot not responding to commands:**
- Make sure the bot has proper permissions
- Check that the bot is online (green status)
- Verify slash commands are synced (happens automatically on startup)

**Commands not showing:**
- Wait up to 1 hour for Discord to sync commands globally
- Restart Discord (Ctrl+R)
- Make sure bot was invited with `applications.commands` scope

**Database errors:**
- The `data/` folder is created automatically
- Delete `data/bot.db` to reset the database

## Support

This bot includes:
- ✅ Slash commands
- ✅ Auto-moderation system
- ✅ Economy & leveling
- ✅ Giveaway system with requirements
- ✅ Custom commands
- ✅ Welcome/goodbye messages
- ✅ Comprehensive activity logging
- ✅ Error handling
- ✅ Forever-running scripts for self-hosting

## Notes

- All commands use Discord's slash command system (`/command`)
- Custom commands use the text prefix (default: `!`)
- The bot automatically creates necessary database tables
- Logs are saved to `bot.log`

## Bugs 
** Prefix ('>') dont work like: >kill, >help, etc

Enjoy your fully-featured Discord bot! 🎉
