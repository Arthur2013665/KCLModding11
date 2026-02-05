# Discord Bot Design Document

## Overview

This document outlines the technical design for a comprehensive Discord bot built using Python and the discord.py library. The bot will feature over 100 commands with a focus on moderation, along with utility features like Blox Fruits stock tracking, YouTube notifications, economy systems, music playback, and entertainment commands.

### Technology Stack

- **Python 3.10+**: Core programming language
- **discord.py 2.x**: Discord API wrapper library with slash command support
- **SQLite**: Lightweight database for storing user data, warnings, custom commands, and economy data
- **aiohttp**: Async HTTP client for API requests (Blox Fruits, YouTube, memes)
- **yt-dlp**: YouTube audio extraction for music commands
- **PyNaCl**: Voice support for music playback
- **python-dotenv**: Environment variable management for secure token storage

## Architecture

### Bot Structure

```
discord-bot/
├── bot.py                      # Main bot entry point
├── config.py                   # Configuration and environment variables
├── requirements.txt            # Python dependencies
├── .env                        # Environment variables (token, API keys)
├── database/
│   ├── __init__.py
│   ├── db_manager.py          # Database connection and operations
│   └── models.py              # Data models and schemas
├── cogs/
│   ├── __init__.py
│   ├── moderation.py          # Moderation commands (30+ commands)
│   ├── automod.py             # Auto-moderation features
│   ├── logging.py             # Moderation logging system
│   ├── bloxfruits.py          # Blox Fruits stock tracking
│   ├── youtube.py             # YouTube notification system
│   ├── economy.py             # Economy and leveling system
│   ├── music.py               # Music playback commands
│   ├── utility.py             # Utility commands (userinfo, serverinfo, etc.)
│   ├── fun.py                 # Entertainment commands
│   ├── custom_commands.py     # Custom command system
│   └── events.py              # Event handlers (welcome, goodbye, etc.)
└── utils/
    ├── __init__.py
    ├── checks.py              # Permission checks and decorators
    ├── embeds.py              # Embed templates and builders
    ├── helpers.py             # Helper functions
    └── constants.py           # Constants and enums
```

### Cog-Based Architecture

The bot uses discord.py's Cog system to organize commands into logical modules. Each cog is a separate Python class that groups related commands together, making the codebase maintainable and scalable.

## Components and Interfaces

### 1. Main Bot (bot.py)

**Responsibilities:**
- Initialize the Discord bot client with required intents
- Load all cogs dynamically from the cogs directory
- Handle bot startup and shutdown events
- Manage global error handling

**Key Methods:**
```python
async def setup_hook()  # Load cogs and sync commands
async def on_ready()    # Bot startup confirmation
async def on_error()    # Global error handler
```

### 2. Configuration Manager (config.py)

**Responsibilities:**
- Load environment variables from .env file
- Provide configuration constants
- Validate required settings on startup

**Configuration Values:**
- `DISCORD_TOKEN`: Bot authentication token
- `DATABASE_PATH`: SQLite database file path
- `YOUTUBE_API_KEY`: YouTube Data API key (optional)
- `BLOXFRUITS_API_URL`: Blox Fruits stock API endpoint
- `PREFIX`: Command prefix (for text commands if needed)

### 3. Database Manager (database/db_manager.py)

**Responsibilities:**
- Manage SQLite database connections
- Provide async database operations
- Handle database migrations and schema updates

**Database Schema:**

```sql
-- Users table for economy and leveling
CREATE TABLE users (
    user_id INTEGER PRIMARY KEY,
    guild_id INTEGER NOT NULL,
    xp INTEGER DEFAULT 0,
    level INTEGER DEFAULT 1,
    balance INTEGER DEFAULT 0,
    last_daily TIMESTAMP,
    last_message TIMESTAMP
);

-- Warnings table for moderation
CREATE TABLE warnings (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    user_id INTEGER NOT NULL,
    guild_id INTEGER NOT NULL,
    moderator_id INTEGER NOT NULL,
    reason TEXT NOT NULL,
    timestamp TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

-- Moderation logs
CREATE TABLE mod_logs (
    case_id INTEGER PRIMARY KEY AUTOINCREMENT,
    guild_id INTEGER NOT NULL,
    action_type TEXT NOT NULL,
    user_id INTEGER NOT NULL,
    moderator_id INTEGER NOT NULL,
    reason TEXT,
    timestamp TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

-- Custom commands
CREATE TABLE custom_commands (
    guild_id INTEGER NOT NULL,
    trigger TEXT NOT NULL,
    response TEXT NOT NULL,
    created_by INTEGER NOT NULL,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    PRIMARY KEY (guild_id, trigger)
);

-- YouTube subscriptions
CREATE TABLE youtube_subs (
    guild_id INTEGER NOT NULL,
    channel_id TEXT NOT NULL,
    notification_channel INTEGER NOT NULL,
    last_video_id TEXT,
    PRIMARY KEY (guild_id, channel_id)
);

-- Blox Fruits notifications
CREATE TABLE bloxfruits_alerts (
    user_id INTEGER NOT NULL,
    guild_id INTEGER NOT NULL,
    fruit_name TEXT NOT NULL,
    PRIMARY KEY (user_id, guild_id, fruit_name)
);

-- Server settings
CREATE TABLE guild_settings (
    guild_id INTEGER PRIMARY KEY,
    welcome_channel INTEGER,
    welcome_message TEXT,
    goodbye_channel INTEGER,
    goodbye_message TEXT,
    mod_log_channel INTEGER,
    automod_enabled BOOLEAN DEFAULT 1,
    spam_detection BOOLEAN DEFAULT 1,
    blacklist_enabled BOOLEAN DEFAULT 1
);

-- Blacklisted words
CREATE TABLE blacklist (
    guild_id INTEGER NOT NULL,
    word TEXT NOT NULL,
    PRIMARY KEY (guild_id, word)
);

-- Muted users
CREATE TABLE mutes (
    user_id INTEGER NOT NULL,
    guild_id INTEGER NOT NULL,
    unmute_at TIMESTAMP NOT NULL,
    reason TEXT,
    PRIMARY KEY (user_id, guild_id)
);
```

### 4. Moderation Cog (cogs/moderation.py)

**Commands (30+ moderation commands):**

**Basic Moderation:**
- `/ban <user> [reason]` - Ban a user
- `/unban <user_id>` - Unban a user
- `/kick <user> [reason]` - Kick a user
- `/mute <user> <duration> [reason]` - Mute a user temporarily
- `/unmute <user>` - Unmute a user
- `/timeout <user> <duration> [reason]` - Discord native timeout
- `/warn <user> <reason>` - Warn a user
- `/warnings <user>` - View user warnings
- `/clearwarnings <user>` - Clear user warnings
- `/removewarn <case_id>` - Remove specific warning

**Message Management:**
- `/purge <amount>` - Delete messages
- `/purge user <user> <amount>` - Delete user's messages
- `/purge bots <amount>` - Delete bot messages
- `/purge contains <text> <amount>` - Delete messages containing text
- `/purge embeds <amount>` - Delete messages with embeds
- `/purge files <amount>` - Delete messages with attachments

**Channel Management:**
- `/lock [channel]` - Lock a channel
- `/unlock [channel]` - Unlock a channel
- `/slowmode <seconds> [channel]` - Set slowmode
- `/nuke [channel]` - Clone and delete channel (clear all messages)

**Role Management:**
- `/role add <user> <role>` - Add role to user
- `/role remove <user> <role>` - Remove role from user
- `/role create <name> [color]` - Create a new role
- `/role delete <role>` - Delete a role
- `/role info <role>` - Display role information
- `/role members <role>` - List role members

**User Management:**
- `/nickname <user> <nickname>` - Change user nickname
- `/resetnick <user>` - Reset user nickname
- `/userinfo <user>` - Display user information
- `/modlogs <user>` - View moderation history
- `/case <case_id>` - View specific case details

**Server Management:**
- `/serverinfo` - Display server information
- `/setmodlog <channel>` - Set moderation log channel
- `/announce <channel> <message>` - Send announcement

### 5. Auto-Moderation Cog (cogs/automod.py)

**Features:**
- Spam detection (message rate limiting)
- Blacklist word filtering
- Excessive caps detection
- Invite link blocking
- Mass mention detection

**Commands:**
- `/automod config` - Configure auto-mod settings
- `/automod toggle <feature>` - Enable/disable features
- `/blacklist add <word>` - Add word to blacklist
- `/blacklist remove <word>` - Remove word from blacklist
- `/blacklist list` - View blacklisted words

**Event Handlers:**
```python
@commands.Cog.listener()
async def on_message(message)  # Check all auto-mod rules
```

### 6. Blox Fruits Cog (cogs/bloxfruits.py)

**Commands:**
- `/bloxfruits stock` - Check current stock
- `/bloxfruits notify <fruit>` - Subscribe to fruit alerts
- `/bloxfruits unnotify <fruit>` - Unsubscribe from alerts
- `/bloxfruits list` - List all fruits
- `/bloxfruits info <fruit>` - Get fruit information

**Background Task:**
```python
@tasks.loop(minutes=15)
async def check_stock()  # Periodically check stock and send notifications
```

**API Integration:**
- Use aiohttp to fetch stock data from Blox Fruits API
- Parse JSON response and format into Discord embeds
- Cache results to avoid rate limiting

### 7. YouTube Notification Cog (cogs/youtube.py)

**Commands:**
- `/youtube add <channel_url> <notification_channel>` - Subscribe to channel
- `/youtube remove <channel_url>` - Unsubscribe from channel
- `/youtube list` - List all subscriptions
- `/youtube check` - Manually check for new videos

**Background Task:**
```python
@tasks.loop(minutes=5)
async def check_uploads()  # Check for new videos from subscribed channels
```

**API Integration:**
- Use YouTube Data API v3 to fetch latest videos
- Store last video ID to detect new uploads
- Send rich embeds with video details

### 8. Economy Cog (cogs/economy.py)

**Commands:**
- `/balance [user]` - Check balance
- `/daily` - Claim daily reward
- `/weekly` - Claim weekly reward
- `/work` - Earn money by working
- `/beg` - Beg for money
- `/rob <user>` - Attempt to rob another user
- `/pay <user> <amount>` - Transfer money
- `/leaderboard [type]` - View leaderboards (balance/level)
- `/level [user]` - Check level and XP
- `/shop` - View purchasable items
- `/buy <item>` - Purchase an item
- `/inventory [user]` - View inventory

**XP System:**
- Award 15-25 XP per message (60-second cooldown)
- Level formula: `level = floor(0.1 * sqrt(xp))`
- Level-up announcements in channel

### 9. Music Cog (cogs/music.py)

**Commands:**
- `/play <query>` - Play a song
- `/pause` - Pause playback
- `/resume` - Resume playback
- `/skip` - Skip current song
- `/stop` - Stop and clear queue
- `/queue` - View queue
- `/nowplaying` - Current song info
- `/volume <0-100>` - Adjust volume
- `/loop` - Toggle loop mode
- `/shuffle` - Shuffle queue
- `/remove <position>` - Remove song from queue
- `/leave` - Disconnect from voice

**Implementation:**
- Use yt-dlp for audio extraction
- Implement queue system with asyncio
- Handle voice state updates

### 10. Utility Cog (cogs/utility.py)

**Commands:**
- `/userinfo [user]` - User information
- `/serverinfo` - Server information
- `/avatar [user]` - Display avatar
- `/banner [user]` - Display banner
- `/roleinfo <role>` - Role information
- `/channelinfo [channel]` - Channel information
- `/emojis` - List server emojis
- `/poll <question> <options>` - Create poll
- `/remind <time> <message>` - Set reminder
- `/afk [reason]` - Set AFK status
- `/ping` - Bot latency
- `/uptime` - Bot uptime
- `/invite` - Bot invite link
- `/support` - Support server link

### 11. Fun Cog (cogs/fun.py)

**Commands (20+ fun commands):**
- `/8ball <question>` - Magic 8-ball
- `/coinflip` - Flip a coin
- `/dice [sides]` - Roll dice
- `/meme` - Random meme
- `/joke` - Random joke
- `/fact` - Random fact
- `/quote` - Inspirational quote
- `/roast [user]` - Roast someone
- `/compliment [user]` - Compliment someone
- `/ship <user1> <user2>` - Ship two users
- `/choose <options>` - Choose between options
- `/reverse <text>` - Reverse text
- `/mock <text>` - mOcKiNg SpOnGeBoB text
- `/ascii <text>` - ASCII art text
- `/rate <thing>` - Rate something
- `/howgay [user]` - Gay percentage (joke)
- `/pp [user]` - PP size (joke)
- `/iq [user]` - IQ test (joke)
- `/simprate [user]` - Simp rating (joke)
- `/hack <user>` - Fake hack (joke)

### 12. Custom Commands Cog (cogs/custom_commands.py)

**Commands:**
- `/customcmd add <trigger> <response>` - Create custom command
- `/customcmd remove <trigger>` - Delete custom command
- `/customcmd edit <trigger> <new_response>` - Edit custom command
- `/customcmd list` - List all custom commands
- `/customcmd info <trigger>` - View custom command details

**Variable Support:**
- `{user}` - Command invoker mention
- `{server}` - Server name
- `{members}` - Member count
- `{channel}` - Channel mention

### 13. Events Cog (cogs/events.py)

**Event Handlers:**
- `on_member_join` - Welcome messages
- `on_member_remove` - Goodbye messages
- `on_message` - XP tracking, AFK detection
- `on_command_error` - Error handling
- `on_guild_join` - Initialize server settings
- `on_guild_remove` - Cleanup server data

**Commands:**
- `/setwelcome <channel> <message>` - Configure welcome
- `/setgoodbye <channel> <message>` - Configure goodbye
- `/testwelcome` - Test welcome message
- `/testgoodbye` - Test goodbye message

## Data Models

### User Model
```python
@dataclass
class User:
    user_id: int
    guild_id: int
    xp: int = 0
    level: int = 1
    balance: int = 0
    last_daily: Optional[datetime] = None
    last_message: Optional[datetime] = None
```

### Warning Model
```python
@dataclass
class Warning:
    id: int
    user_id: int
    guild_id: int
    moderator_id: int
    reason: str
    timestamp: datetime
```

### ModLog Model
```python
@dataclass
class ModLog:
    case_id: int
    guild_id: int
    action_type: str
    user_id: int
    moderator_id: int
    reason: Optional[str]
    timestamp: datetime
```

## Error Handling

### Global Error Handler
```python
@bot.event
async def on_command_error(ctx, error):
    if isinstance(error, commands.MissingPermissions):
        # Send permission error embed
    elif isinstance(error, commands.MissingRequiredArgument):
        # Send usage help
    elif isinstance(error, commands.CommandOnCooldown):
        # Send cooldown message
    else:
        # Log unexpected errors
```

### Cog-Specific Error Handlers
Each cog implements its own error handler for command-specific errors.

## Testing Strategy

### Unit Tests
- Database operations (CRUD operations)
- Helper functions (permission checks, embed builders)
- XP calculation and leveling logic
- Custom command variable replacement

### Integration Tests
- Command execution flow
- Database persistence
- API integrations (mocked)
- Event handler triggers

### Manual Testing
- Test all commands in a development Discord server
- Verify permission checks work correctly
- Test auto-moderation triggers
- Verify YouTube and Blox Fruits notifications
- Test music playback in voice channels
- Verify economy system calculations

### Test Server Setup
Create a dedicated test Discord server with:
- Multiple channels for different command categories
- Test users with various permission levels
- Voice channels for music testing
- Configured moderation log channel

## Security Considerations

### Token Security
- Store bot token in `.env` file (never commit to git)
- Add `.env` to `.gitignore`
- Use environment variables for all sensitive data

### Permission Checks
- Implement decorator-based permission checks
- Verify user permissions before executing moderation commands
- Validate bot has required permissions before actions

### Input Validation
- Sanitize user input to prevent injection attacks
- Validate URLs before making API requests
- Limit message lengths and command arguments

### Rate Limiting
- Implement cooldowns on economy commands
- Rate limit API requests to external services
- Prevent spam through auto-moderation

## Performance Optimization

### Database Optimization
- Use indexes on frequently queried columns (user_id, guild_id)
- Implement connection pooling
- Cache frequently accessed data (guild settings)

### API Caching
- Cache Blox Fruits stock data (15-minute TTL)
- Cache YouTube video data (5-minute TTL)
- Cache meme/joke API responses

### Async Operations
- Use async/await for all I/O operations
- Implement background tasks for periodic checks
- Use asyncio.gather for concurrent operations

## Deployment

### Requirements
- Python 3.10 or higher
- Discord bot token with required intents:
  - Message Content Intent
  - Server Members Intent
  - Presence Intent (optional)
- YouTube Data API key (for YouTube notifications)

### Environment Variables
```
DISCORD_TOKEN=your_bot_token_here
YOUTUBE_API_KEY=your_youtube_api_key
DATABASE_PATH=./data/bot.db
BLOXFRUITS_API_URL=https://api.example.com/bloxfruits
```

### Running the Bot
```bash
python bot.py
```

### Hosting Options
- VPS (DigitalOcean, Linode, AWS EC2)
- Heroku (with worker dyno)
- Railway.app
- Replit (for development/testing)

## Future Enhancements

- Web dashboard for server configuration
- Advanced analytics and statistics
- Ticket system for support
- Reaction roles
- Giveaway system
- Starboard feature
- Suggestion system with voting
- Twitch notification integration
- Multi-language support
