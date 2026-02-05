# Quick Start Guide

## Getting Your Bot Running in 3 Steps

### Step 1: Install Dependencies
```bash
pip install -r requirements.txt
```

### Step 2: Run the Bot
```bash
python bot.py
```

That's it! Your bot token is already configured in the `.env` file.

## What Happens Next?

1. The bot will start and connect to Discord
2. All commands will be automatically synced
3. The database will be created in `data/bot.db`
4. You'll see "Bot is ready!" in the console

## First Commands to Try

Once the bot is online in your server:

### Test Basic Commands
```
/ping          - Check if bot is responding
/help          - See all available commands
/serverinfo    - View server information
```

### Set Up Moderation
```
/setmodlog #mod-logs     - Set moderation log channel
/automod all true        - Enable auto-moderation
/blacklist add badword   - Add words to filter
```

### Set Up Welcome Messages
```
/setwelcome #welcome Welcome {user} to {server}!
/testwelcome             - Test the welcome message
```

### Try Fun Commands
```
/8ball Will this bot be awesome?
/coinflip
/joke
/ship @user1 @user2
```

### Try Economy
```
/balance     - Check your balance
/daily       - Claim daily reward
/work        - Earn money
/leaderboard - See top users
```

### Try Music (in a voice channel)
```
/play never gonna give you up
/queue
/skip
```

## Common Issues

**"Application did not respond"**
- Wait a few seconds and try again
- The bot might be syncing commands (happens on first startup)

**Commands not showing up**
- Wait 1-2 minutes after bot starts
- Try kicking and re-inviting the bot
- Make sure bot has "applications.commands" scope

**Music not working**
- Install FFmpeg: https://ffmpeg.org/download.html
- Make sure you're in a voice channel
- Bot needs Connect and Speak permissions

## Need Help?

Check the full README.md for:
- Complete command list (100+ commands)
- Detailed feature descriptions
- Configuration options
- Troubleshooting guide

## Pro Tips

1. **Use `/help`** to see all command categories
2. **Set up moderation logging** first for better server management
3. **Configure auto-mod** to automatically handle spam and bad words
4. **Create custom commands** with `/customcmd-add` for server-specific needs
5. **Check `/leaderboard`** to see most active members

Enjoy your bot! 🚀
