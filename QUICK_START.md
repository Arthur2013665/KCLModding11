# 🚀 Quick Start Guide

## Local Development

### 1. Setup (One Time)
```bash
./setup.sh
```

### 2. Configure
Edit `.env` with your Discord bot token:
```env
DISCORD_TOKEN=your_actual_bot_token_here
YOUTUBE_API_KEY=your_youtube_api_key_here  # Optional
```

### 3. Start Bot
```bash
./start.sh
```

### 4. Test
In Discord:
```
!ping
/help
```

---

## Deploy to Render.com (24/7 Hosting)

### 1. Push to GitHub
```bash
git init
git add .
git commit -m "Discord bot ready"
git remote add origin https://github.com/YOUR_USERNAME/YOUR_REPO.git
git push -u origin main
```

### 2. Deploy on Render
1. Go to [render.com](https://render.com)
2. Click "New +" → "Web Service"
3. Connect your GitHub repo
4. Render auto-detects `render.yaml`!

### 3. Add Environment Variables
In Render dashboard:
- `DISCORD_TOKEN` = your bot token
- `YOUTUBE_API_KEY` = your YouTube key (optional)

### 4. Deploy!
Click "Create Web Service" - Done! 🎉

---

## Commands

### Moderation
- `/ban @user` - Ban a user
- `/kick @user` - Kick a user
- `/warn @user reason` - Warn a user
- `/purge 10` - Delete 10 messages
- `/timeout @user 1h` - Timeout for 1 hour

### Music
- `/play song name` - Play music
- `/pause` - Pause playback
- `/skip` - Skip song
- `/queue` - View queue

### Economy
- `/balance` - Check balance
- `/daily` - Daily reward
- `/work` - Earn money
- `/leaderboard` - Top users

### Giveaway
- `/giveaway-start prize:Prize duration:1h` - Start giveaway
- `/giveaway-end message_id` - End giveaway
- `/giveaway-reroll message_id` - Reroll winner

### Fun
- `/meme` - Random meme
- `/joke` - Random joke
- `/8ball question` - Magic 8-ball

### Utility
- `/serverinfo` - Server information
- `/userinfo @user` - User information
- `/avatar @user` - User avatar
- `/ping` - Bot latency

---

## Troubleshooting

### Bot won't start
- Check `DISCORD_TOKEN` in `.env`
- Verify token is valid in Discord Developer Portal
- Check logs: `tail -f bot.log`

### Commands not working
- Ensure bot has proper permissions
- Check if commands are synced (wait a few minutes)
- Try `!ping` (prefix command) vs `/ping` (slash command)

### Music not working
- Bot needs "Connect" and "Speak" permissions
- Join a voice channel first
- Check if `YOUTUBE_API_KEY` is set (optional)

---

## Documentation

- `README.md` - Full feature list
- `RENDER_DEPLOYMENT_GUIDE.md` - Detailed Render.com guide
- `DEPLOYMENT_SUMMARY.md` - What was changed
- `TROUBLESHOOTING.md` - Common issues

---

## Support

**Bot Issues:**
- Check logs: `tail -f bot.log`
- Review `TROUBLESHOOTING.md`
- Test locally before deploying

**Render Issues:**
- Check Render dashboard logs
- Verify environment variables
- Review `RENDER_DEPLOYMENT_GUIDE.md`

---

**Your Discord bot is ready! 🤖**
