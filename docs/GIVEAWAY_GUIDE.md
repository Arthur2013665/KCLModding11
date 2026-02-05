# 🎉 Giveaway System Guide

## Overview

The giveaway system allows you to create, manage, and end giveaways in your Discord server with automatic winner selection.

## Commands

### `/giveaway-start` - Start a Giveaway

Start a new giveaway with customizable settings.

**Usage:**
```
/giveaway-start prize:<prize> duration:<time> [winners:<number>] [channel:<channel>]
```

**Parameters:**
- `prize` (required): What you're giving away
- `duration` (required): How long the giveaway lasts
  - Format: `30s`, `5m`, `2h`, `1d`
  - Examples: `30s` (30 seconds), `5m` (5 minutes), `2h` (2 hours), `1d` (1 day)
- `winners` (optional): Number of winners (1-20, default: 1)
- `channel` (optional): Channel to post giveaway (default: current channel)

**Examples:**
```
/giveaway-start prize:Discord Nitro duration:1d winners:1
/giveaway-start prize:$50 Steam Gift Card duration:12h winners:2
/giveaway-start prize:Custom Role duration:30m winners:3 channel:#giveaways
```

**Permissions Required:** Manage Server

---

### `/giveaway-end` - End a Giveaway Early

End an active giveaway before its scheduled end time.

**Usage:**
```
/giveaway-end message_id:<message_id>
```

**Parameters:**
- `message_id` (required): The message ID of the giveaway

**How to get Message ID:**
1. Enable Developer Mode (User Settings → Advanced → Developer Mode)
2. Right-click the giveaway message
3. Click "Copy Message ID"

**Example:**
```
/giveaway-end message_id:1234567890123456789
```

**Permissions Required:** Manage Server

---

### `/giveaway-reroll` - Reroll Winners

Pick new winner(s) for an ended giveaway.

**Usage:**
```
/giveaway-reroll message_id:<message_id>
```

**Parameters:**
- `message_id` (required): The message ID of the giveaway

**Example:**
```
/giveaway-reroll message_id:1234567890123456789
```

**Use Cases:**
- Original winner didn't respond
- Winner was disqualified
- Want to give another chance

**Permissions Required:** Manage Server

---

### `/giveaway-list` - List Active Giveaways

View all currently active giveaways in the server.

**Usage:**
```
/giveaway-list
```

**Shows:**
- Prize
- Channel
- Number of winners
- Time remaining
- Message ID (for ending/rerolling)

**Permissions Required:** None (everyone can use)

---

## How It Works

### 1. Starting a Giveaway

When you start a giveaway:
1. Bot creates an embed with giveaway details
2. Adds 🎉 reaction automatically
3. Stores giveaway in database
4. Monitors for end time

### 2. Entering a Giveaway

Users enter by:
1. Clicking the 🎉 reaction on the giveaway message
2. Bot tracks all participants (excluding bots)

### 3. Ending a Giveaway

Giveaways end automatically when:
- Time expires (checked every 30 seconds)
- Manually ended with `/giveaway-end`

When ending:
1. Bot collects all 🎉 reactions
2. Filters out bots
3. Randomly selects winner(s)
4. Updates embed with winners
5. Mentions winners in channel

### 4. No Participants

If no one enters:
- Giveaway ends with "No valid participants" message
- No winners selected

## Duration Format

### Supported Units
- `s` - Seconds
- `m` - Minutes
- `h` - Hours
- `d` - Days

### Examples
| Input | Duration |
|-------|----------|
| `30s` | 30 seconds |
| `5m` | 5 minutes |
| `1h` | 1 hour |
| `12h` | 12 hours |
| `1d` | 1 day |
| `7d` | 7 days |

### Common Durations
- Quick giveaway: `30m` or `1h`
- Standard giveaway: `12h` or `1d`
- Long giveaway: `3d` or `7d`

## Giveaway Embed

The giveaway message shows:

```
🎉 GIVEAWAY 🎉

Prize: Discord Nitro
Winners: 1
Ends: in 12 hours

React with 🎉 to enter!

Hosted by: @Username
```

After ending:

```
🎉 Giveaway Ended!

Prize: Discord Nitro
Winner: @WinnerName

Giveaway ended
```

## Best Practices

### 1. Clear Prize Description
✅ Good: "Discord Nitro (1 month)"
✅ Good: "$50 Steam Gift Card"
❌ Bad: "Something cool"
❌ Bad: "Prize"

### 2. Appropriate Duration
- Short giveaways (30m-2h): Quick engagement
- Medium giveaways (12h-1d): Standard
- Long giveaways (3d-7d): Maximum participation

### 3. Dedicated Channel
- Create a #giveaways channel
- Keep giveaways organized
- Easy for users to find

### 4. Winner Count
- 1 winner: Most common
- 2-3 winners: Medium prizes
- 5+ winners: Small prizes or high participation

### 5. Announcement
- Announce giveaway in other channels
- Pin the giveaway message
- Remind users before it ends

## Examples

### Example 1: Simple Giveaway
```
/giveaway-start prize:Discord Nitro duration:1d
```
- 1 winner
- Lasts 1 day
- Posted in current channel

### Example 2: Multiple Winners
```
/giveaway-start prize:Custom Role duration:12h winners:3
```
- 3 winners
- Lasts 12 hours
- Posted in current channel

### Example 3: Specific Channel
```
/giveaway-start prize:$100 Gift Card duration:3d winners:2 channel:#giveaways
```
- 2 winners
- Lasts 3 days
- Posted in #giveaways

### Example 4: Quick Giveaway
```
/giveaway-start prize:Shoutout duration:30m winners:1
```
- 1 winner
- Lasts 30 minutes
- Quick engagement boost

## Managing Giveaways

### Check Active Giveaways
```
/giveaway-list
```
Shows all active giveaways with message IDs

### End Early
```
/giveaway-end message_id:1234567890123456789
```
Immediately ends and picks winners

### Reroll Winner
```
/giveaway-reroll message_id:1234567890123456789
```
Picks new winner from same participants

## Troubleshooting

### "No valid participants"
**Cause:** No one reacted with 🎉
**Solution:** 
- Announce the giveaway
- Make prize more appealing
- Increase duration

### "Giveaway not found"
**Cause:** Wrong message ID or giveaway deleted
**Solution:**
- Check message ID is correct
- Use `/giveaway-list` to find active giveaways

### "Invalid duration format"
**Cause:** Wrong duration format
**Solution:** Use format like `1h`, `30m`, `1d`

### Winners didn't get notified
**Cause:** Winners have DMs disabled or left server
**Solution:**
- Winners are mentioned in channel
- Use `/giveaway-reroll` if needed

## Database

Giveaways are stored in the database with:
- Message ID
- Channel ID
- Guild ID
- Prize
- Number of winners
- End time
- Host
- Active status

This allows:
- Automatic ending
- Persistence across bot restarts
- History tracking

## Permissions

### Required Permissions
- **Start/End/Reroll**: Manage Server
- **List**: Everyone

### Bot Permissions Needed
- Send Messages
- Embed Links
- Add Reactions
- Read Message History
- Mention Everyone (for winner announcements)

## Tips & Tricks

### 1. Boost Engagement
- Host regular giveaways
- Vary prize types
- Use different durations

### 2. Fair Selection
- Bot randomly selects from all participants
- Each reaction counts as one entry
- Bots are automatically excluded

### 3. Multiple Giveaways
- Run multiple giveaways simultaneously
- Use different channels
- Track with `/giveaway-list`

### 4. Reroll Strategy
- Wait 5-10 minutes for winner response
- Announce reroll before doing it
- Can reroll multiple times

### 5. Prize Ideas
- Discord Nitro
- Server boosts
- Custom roles
- Gift cards
- Game keys
- Exclusive access
- Shoutouts

## Advanced Usage

### Scheduled Giveaways
1. Plan giveaway schedule
2. Start at specific times
3. Use consistent durations

### Themed Giveaways
- Holiday giveaways
- Milestone celebrations
- Event-based prizes

### Multi-Server
- Each server has separate giveaways
- Same commands work everywhere
- Independent tracking

## Quick Reference

| Command | Purpose | Permission |
|---------|---------|------------|
| `/giveaway-start` | Start giveaway | Manage Server |
| `/giveaway-end` | End early | Manage Server |
| `/giveaway-reroll` | Pick new winner | Manage Server |
| `/giveaway-list` | List active | Everyone |

**Duration Format:** `30s`, `5m`, `2h`, `1d`
**Entry Method:** React with 🎉
**Winner Selection:** Random from participants

---

**Happy giveaway hosting! 🎉**
