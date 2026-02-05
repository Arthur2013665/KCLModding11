# 🚀 Super Simple Render.com Setup

Your bot will run `start.sh` 24/7 on Render!

## Step 1: Push to GitHub

```bash
git init
git add .
git commit -m "Discord bot"
git remote add origin https://github.com/YOUR_USERNAME/YOUR_REPO.git
git push -u origin main
```

## Step 2: Deploy on Render

1. Go to [render.com](https://render.com)
2. Sign up with GitHub
3. Click **"New +"** → **"Web Service"**
4. Select your repository
5. Render auto-detects everything from `render.yaml`!

## Step 3: Add Your Bot Token

In Render dashboard, add environment variable:
- **Key**: `DISCORD_TOKEN`
- **Value**: Your bot token from [Discord Developer Portal](https://discord.com/developers/applications)

## Step 4: Deploy!

Click **"Create Web Service"**

That's it! Your bot runs `./start.sh` automatically and stays online 24/7! 🎉

---

## What Happens

Render will:
1. Clone your GitHub repo
2. Install dependencies: `pip install -r requirements.txt`
3. Run your bot: `./start.sh` (which runs `python3 bot.py`)
4. Keep it running 24/7!

---

## Check if It's Working

**In Render:**
- Go to **Logs** tab
- Look for: `✅ Bot is ready!`

**In Discord:**
- Bot shows as online
- Test: `!ping` or `/help`

---

## Update Your Bot

Just push to GitHub:
```bash
git add .
git commit -m "Update"
git push
```

Render automatically redeploys! 🔄

---

## Free Tier

- ✅ 750 hours/month (enough for 24/7)
- ✅ Auto-deploy from GitHub
- ⚠️ May sleep after 15 min inactivity
- 💰 Upgrade to $7/month for true 24/7

---

## That's It!

Your `start.sh` runs 24/7 on Render. No complicated setup needed! 🚀
