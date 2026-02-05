# Implementation Plan

- [x] 1. Set up project structure and core bot framework


  - Create directory structure with cogs, database, and utils folders
  - Initialize bot.py with Discord client and intents configuration
  - Create config.py for environment variable management
  - Set up .env file template with secure token storage
  - Create requirements.txt with all necessary dependencies
  - _Requirements: 1.1, 2.1, 3.1, 4.1, 5.1, 6.1, 7.1, 8.1, 9.1, 10.1, 11.1, 12.1_



- [ ] 2. Implement database layer and models
  - Create database manager with SQLite connection handling
  - Implement database schema with all required tables (users, warnings, mod_logs, custom_commands, youtube_subs, bloxfruits_alerts, guild_settings, blacklist, mutes)
  - Create data models for User, Warning, ModLog, and other entities
  - Implement CRUD operations for each table

  - Add database initialization and migration logic
  - _Requirements: 1.4, 3.1, 3.2, 3.3, 8.1, 10.1_

- [x] 3. Create utility modules and helper functions

  - Implement permission check decorators for admin/moderator commands
  - Create embed builder templates for consistent message formatting
  - Implement helper functions for time parsing and formatting
  - Create constants file with colors, emojis, and configuration values
  - _Requirements: 1.1, 2.1, 3.1, 6.2, 6.3_

- [x] 4. Implement core moderation commands (Part 1: User Actions)



  - Implement /ban command with reason logging
  - Implement /unban command with user ID lookup
  - Implement /kick command with reason logging
  - Implement /mute command with duration parsing and temporary mute storage
  - Implement /unmute command with mute removal
  - Implement /timeout command using Discord's native timeout feature
  - Implement /warn command with database storage and DM notification
  - Implement /warnings command to display user warning history
  - Implement /clearwarnings command to remove all warnings for a user
  - Implement /removewarn command to delete specific warning by case ID
  - _Requirements: 1.1, 1.2, 1.3, 1.4, 3.4_

- [x] 5. Implement core moderation commands (Part 2: Message Management)


  - Implement /purge command with amount parameter for bulk message deletion
  - Implement /purge user subcommand to delete specific user's messages
  - Implement /purge bots subcommand to delete bot messages
  - Implement /purge contains subcommand to delete messages with specific text
  - Implement /purge embeds subcommand to delete messages with embeds
  - Implement /purge files subcommand to delete messages with attachments
  - _Requirements: 1.5, 2.1_


- [x] 6. Implement core moderation commands (Part 3: Channel & Role Management)

  - Implement /lock command to remove send permissions from channels
  - Implement /unlock command to restore channel permissions
  - Implement /slowmode command with duration in seconds
  - Implement /nuke command to clone and delete channel
  - Implement /role add command to assign roles to users
  - Implement /role remove command to remove roles from users
  - Implement /role create command with name and color parameters
  - Implement /role delete command with confirmation
  - Implement /role info command to display role details
  - Implement /role members command to list users with specific role
  - Implement /nickname command to change user nicknames
  - Implement /resetnick command to reset nicknames
  - _Requirements: 2.2, 2.3, 2.4, 2.5_


- [x] 7. Implement moderation logging system

  - Create logging cog with event handlers for all moderation actions
  - Implement log entry creation for bans, kicks, mutes, warnings
  - Create rich embed format for moderation logs with color coding
  - Implement /modlogs command to view user's moderation history
  - Implement /case command to view specific case details
  - Implement /setmodlog command to configure log channel
  - _Requirements: 3.1, 3.2, 3.3, 3.4_


- [x] 8. Implement auto-moderation system

  - Create automod cog with message event listener
  - Implement spam detection with message rate limiting (5 messages in 3 seconds)
  - Implement blacklist word filtering with automatic message deletion
  - Implement excessive caps detection (70% threshold)
  - Implement Discord invite link blocking
  - Implement mass mention detection
  - Create /automod config command for settings management
  - Create /automod toggle command to enable/disable features
  - Implement /blacklist add, /blacklist remove, and /blacklist list commands
  - _Requirements: 7.1, 7.2, 7.3, 7.4, 7.5_


- [x] 9. Implement Blox Fruits stock tracking system

  - Create bloxfruits cog with API integration using aiohttp
  - Implement /bloxfruits stock command to fetch and display current stock
  - Implement /bloxfruits notify command to subscribe to fruit alerts
  - Implement /bloxfruits unnotify command to unsubscribe from alerts
  - Implement /bloxfruits list command to show all available fruits
  - Implement /bloxfruits info command for detailed fruit information
  - Create background task to check stock every 15 minutes
  - Implement notification system to alert subscribed users when fruits are in stock
  - _Requirements: 4.1, 4.2, 4.3, 4.4, 4.5_


- [x] 10. Implement YouTube notification system

  - Create youtube cog with YouTube Data API v3 integration
  - Implement /youtube add command to subscribe to channels
  - Implement /youtube remove command to unsubscribe from channels
  - Implement /youtube list command to display all subscriptions
  - Implement /youtube check command for manual update check
  - Create background task to check for new uploads every 5 minutes
  - Implement notification posting with rich embeds including thumbnail and link
  - _Requirements: 5.1, 5.2, 5.3, 5.4, 5.5_


- [x] 11. Implement economy system

  - Create economy cog with database integration
  - Implement /balance command to display user currency
  - Implement /daily command with 24-hour cooldown
  - Implement /weekly command with 7-day cooldown
  - Implement /work command with random earnings
  - Implement /beg command with random small earnings
  - Implement /rob command with success/failure mechanics
  - Implement /pay command for user-to-user transfers
  - Implement /leaderboard command with balance and level sorting
  - Implement /shop command to display purchasable items
  - Implement /buy command for item purchases
  - Implement /inventory command to view owned items
  - _Requirements: 8.3, 8.4, 8.5_



- [ ] 12. Implement leveling system
  - Create XP award system in message event handler with 60-second cooldown
  - Implement level calculation formula based on XP
  - Create level-up detection and announcement system
  - Implement /level command to display user level and XP progress
  - Add level-based role rewards (optional configuration)
  - Integrate leveling with leaderboard command
  - _Requirements: 8.1, 8.2, 8.5_


- [x] 13. Implement music playback system

  - Create music cog with voice client management
  - Implement /play command with YouTube search and URL support using yt-dlp
  - Implement queue system with asyncio for track management
  - Implement /pause and /resume commands for playback control
  - Implement /skip command to move to next track
  - Implement /stop command to clear queue and stop playback
  - Implement /queue command to display current queue
  - Implement /nowplaying command to show current track info
  - Implement /volume command with 0-100 range
  - Implement /loop command to toggle repeat mode
  - Implement /shuffle command to randomize queue
  - Implement /remove command to delete specific queue position
  - Implement /leave command to disconnect from voice channel
  - _Requirements: 9.1, 9.2, 9.3, 9.4, 9.5_


- [x] 14. Implement utility commands

  - Create utility cog for informational commands
  - Implement /userinfo command with account details, join date, roles
  - Implement /serverinfo command with server statistics
  - Implement /avatar command to display user profile pictures
  - Implement /banner command to display user banners
  - Implement /roleinfo command with role details
  - Implement /channelinfo command with channel information
  - Implement /emojis command to list server emojis
  - Implement /poll command with reaction-based voting
  - Implement /remind command with time parsing and scheduled DM
  - Implement /afk command with status tracking
  - Implement /ping command to show bot latency
  - Implement /uptime command to display bot runtime
  - Implement /invite command with bot invite link
  - Implement /support command with support server link
  - _Requirements: 6.2, 6.3, 6.4, 6.5_


- [x] 15. Implement fun and entertainment commands

  - Create fun cog for entertainment commands
  - Implement /8ball command with random fortune responses
  - Implement /coinflip command with heads/tails result
  - Implement /dice command with configurable sides
  - Implement /meme command with meme API integration
  - Implement /joke command with joke API integration
  - Implement /fact command with random fact API
  - Implement /quote command with inspirational quotes
  - Implement /roast command with humorous roasts
  - Implement /compliment command with positive messages
  - Implement /ship command with compatibility percentage
  - Implement /choose command to select from options
  - Implement /reverse command to reverse text
  - Implement /mock command for mocking text format
  - Implement /ascii command for ASCII art conversion
  - Implement /rate command with random rating
  - Implement /howgay, /pp, /iq, /simprate commands as joke commands
  - Implement /hack command as fake hacking joke
  - _Requirements: 12.1, 12.2, 12.3, 12.4, 12.5_



- [ ] 16. Implement custom command system
  - Create custom_commands cog with database integration
  - Implement /customcmd add command to create custom commands
  - Implement /customcmd remove command to delete custom commands
  - Implement /customcmd edit command to modify existing commands
  - Implement /customcmd list command to display all custom commands
  - Implement /customcmd info command for command details
  - Create variable replacement system for {user}, {server}, {members}, {channel}
  - Add custom command invocation handler in message event
  - _Requirements: 10.1, 10.2, 10.3, 10.4, 10.5_


- [x] 17. Implement welcome and goodbye system

  - Create events cog for member join/leave handlers
  - Implement on_member_join event with welcome message posting
  - Implement on_member_remove event with goodbye message posting
  - Implement /setwelcome command to configure welcome channel and message
  - Implement /setgoodbye command to configure goodbye channel and message
  - Implement /testwelcome command to preview welcome message
  - Implement /testgoodbye command to preview goodbye message
  - Add variable replacement for username, mention, member count
  - _Requirements: 11.1, 11.2, 11.3, 11.4, 11.5_


- [x] 18. Implement additional utility commands and features

  - Implement /announce command for server announcements
  - Add command usage statistics tracking
  - Create help command with categorized command list
  - Implement error handling for all commands
  - Add command cooldowns to prevent spam
  - Create admin-only configuration commands
  - _Requirements: 2.5, 6.1, 6.2_


- [x] 19. Implement global error handling and logging

  - Create global error handler for command errors
  - Implement specific handlers for MissingPermissions, MissingRequiredArgument, CommandOnCooldown
  - Add error logging to file for debugging
  - Create user-friendly error messages with embeds
  - Implement error reporting to bot owner via DM
  - _Requirements: 1.1, 2.1, 3.1_


- [x] 20. Final integration and testing


  - Test all moderation commands with various permission levels
  - Verify auto-moderation triggers work correctly
  - Test Blox Fruits stock checking and notifications
  - Test YouTube notification system with real channels
  - Verify economy system calculations and cooldowns
  - Test music playback in voice channels
  - Verify all utility and fun commands work as expected
  - Test custom command creation and invocation
  - Verify welcome/goodbye messages trigger correctly
  - Test database persistence across bot restarts
  - Verify all error handlers work properly
  - Create comprehensive README with setup instructions
  - _Requirements: All requirements_
