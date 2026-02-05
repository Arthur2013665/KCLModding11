# 🚀 Render.com Deployment Guide

Deploy your Discord bot to Render.com for 24/7 hosting!

## 📋 Prerequisites

- GitHub account
- Render.com account (free tier available)
- Discord bot token
- Your bot code pushed to GitHub

## 🎯 Quick Start

### 1. Push to GitHub

```bash
# Initialize git (if not already done)
git init
git add .
git commit -m "Initial commit"

# Create a new repository on GitHub, then:
git remote add origin https://github.com/YOUR_USERNAME/YOUR_REPO.git
git branch -M main
git push -u origin main
```

### 2. Create Render Service

1. Go to [Render.com](https://render.com)
2. Sign up or log in
3. Click **"New +"** → **"Web Service"**
4. Connect your GitHub repository
5. Configure the service:

**Basic Settings:**
- **Name**: `discord-bot` (or your preferred name)
- **Region**: Choose closest to you
- **Branch**: `main`
- **Root Directory**: Leave blank
- **Environment**: `Python 3`
- **Build Command**: `pip install -r requirements.txt`
- **Start Command**: `python bot.py`

**Plan:**
- Select **Free** tier (or paid for better performance)

### 3. Add Environment Variables

In Render dashboard, go to **Environment** tab and add:

| Key | Value | Notes |
|-----|-------|-------|
| `DISCORD_TOKEN` | Your bot token | Get from Discord Developer Portal |
| `YOUTUBE_API_KEY` | Your YouTube API key | Optional, for music features |
| `DATABASE_PATH` | `./data/bot.db` | Database location |
| `PREFIX` | `!` | Bot command prefix |
| `PYTHON_VERSION` | `3.11.0` | Python version |

**Important:** Keep `DISCORD_TOKEN` secret!

### 4. Deploy

1. Click **"Create Web Service"**
2. Render will automatically:
   - Clone your repository
   - Install dependencies
   - Start your bot
3. Monitor logs in the **Logs** tab

## ✅ Verify Deployment

1. Check Render logs for:
   ```
   ✅ Bot is ready!
   Logged in as: YourBotName#1234
   ```

2. Test in Discord:
   ```
   !ping
   /help
   ```

## 🔧 Configuration Files

Your bot includes these Render-ready files:

### `render.yaml`
Blueprint for automatic deployment configuration.

### `Procfile`
Tells Render how to run your bot (worker process).

### `runtime.txt`
Specifies Python version.

### `requirements.txt`
Lists all Python dependencies.

## 📊 Free Tier Limits

Render.com free tier includes:
- ✅ 750 hours/month (enough for 24/7)
- ✅ Automatic deploys from GitHub
- ✅ Custom domains
- ✅ Free SSL
- ⚠️ Sleeps after 15 min inactivity (use paid tier for 24/7)

**Note:** Discord bots need to stay active. Consider:
- Upgrading to paid tier ($7/month) for true 24/7
- Using a cron job to ping your service
- Using Render's "Background Worker" instead of "Web Service"

## 🔄 Auto-Deploy

Render automatically redeploys when you push to GitHub:

```bash
git add .
git commit -m "Update bot"
git push
```

Render will detect changes and redeploy automatically!

## 🐛 Troubleshooting

### Bot Not Starting

**Check logs for errors:**
1. Go to Render dashboard
2. Click your service
3. View **Logs** tab

**Common issues:**
- Missing `DISCORD_TOKEN` environment variable
- Invalid bot token
- Missing dependencies in `requirements.txt`

### Bot Goes Offline

**Free tier sleeps after inactivity:**
- Upgrade to paid tier for 24/7 uptime
- Or use "Background Worker" service type

### Database Issues

**Render's filesystem is ephemeral:**
- Data resets on each deploy
- For persistent data, use:
  - Render PostgreSQL (free tier available)
  - External database service
  - Or accept data loss on redeploys

**To use persistent storage:**
1. Add Render PostgreSQL database
2. Update `DATABASE_PATH` to use PostgreSQL
3. Modify `database/db_manager.py` to use PostgreSQL

## 🎛️ Alternative: Background Worker

For better Discord bot hosting, use Background Worker instead:

1. Create **"Background Worker"** instead of "Web Service"
2. Use same settings but:
   - **Start Command**: `python bot.py`
   - No need for web server
   - Won't sleep on free tier!

## 📱 Monitoring

**View bot status:**
1. Render dashboard → Your service
2. Check **Logs** for activity
3. Monitor **Metrics** for resource usage

**Discord bot status:**
- Bot appears online in Discord
- Commands respond correctly
- Check logs for errors

## 🔐 Security Best Practices

1. **Never commit `.env` file**
   - Already in `.gitignore`
   - Use Render environment variables

2. **Rotate tokens regularly**
   - Update in Render dashboard
   - Redeploy automatically

3. **Use secret environment variables**
   - Mark sensitive vars as secret in Render

## 💡 Tips

1. **Use render.yaml for easy setup**
   - Commit `render.yaml` to repo
   - Render auto-configures from it

2. **Monitor logs regularly**
   - Check for errors
   - Monitor bot activity

3. **Test locally first**
   - Run `./start.sh` locally
   - Fix issues before deploying

4. **Keep dependencies updated**
   - Update `requirements.txt`
   - Test before pushing

## 🆘 Support

**Render Issues:**
- [Render Documentation](https://render.com/docs)
- [Render Community](https://community.render.com)

**Bot Issues:**
- Check `TROUBLESHOOTING.md`
- Review bot logs
- Test locally first

## 🎉 Success!

Your Discord bot is now hosted 24/7 on Render.com!

**Next steps:**
1. Invite bot to your server
2. Test all commands
3. Monitor logs for issues
4. Enjoy your hosted bot!

---

**Need help?** Check the logs first, then review this guide.
