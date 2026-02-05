# Requirements Document

## Introduction

This document outlines the requirements for a comprehensive Discord bot built in Python with over 100 commands. The bot will focus heavily on moderation capabilities while also providing utility features including Blox Fruits stock tracking, YouTube notifications, and various other community management tools.

## Glossary

- **Discord Bot**: An automated application that runs on Discord servers to perform various tasks and respond to commands
- **Command**: A user-invoked action that the Discord Bot executes in response to specific text input
- **Moderation Command**: A command that helps server administrators manage users, messages, and server settings
- **Blox Fruits**: A popular Roblox game for which stock information tracking is desired
- **YouTube Pinging**: Automated notifications when specified YouTube channels upload new content
- **Slash Command**: Discord's native command interface using the "/" prefix
- **Permission Level**: Authorization tier determining which users can execute specific commands
- **Embed**: Rich formatted message display in Discord with colors, fields, and images

## Requirements

### Requirement 1

**User Story:** As a server administrator, I want comprehensive moderation commands, so that I can effectively manage my Discord community

#### Acceptance Criteria

1. WHEN an administrator invokes a ban command with a user mention and reason, THE Discord Bot SHALL permanently remove the user from the server and log the action with timestamp and moderator information
2. WHEN an administrator invokes a kick command with a user mention, THE Discord Bot SHALL remove the user from the server without preventing rejoin
3. WHEN an administrator invokes a mute command with a user mention and duration, THE Discord Bot SHALL prevent the user from sending messages for the specified time period
4. WHEN an administrator invokes a warn command with a user mention and reason, THE Discord Bot SHALL record the warning in the database and notify the user via direct message
5. WHEN an administrator invokes a purge command with a message count, THE Discord Bot SHALL delete the specified number of recent messages from the channel

### Requirement 2

**User Story:** As a server administrator, I want advanced moderation tools, so that I can handle complex moderation scenarios

#### Acceptance Criteria

1. WHEN an administrator invokes a slowmode command with a duration in seconds, THE Discord Bot SHALL set the channel message rate limit to the specified interval
2. WHEN an administrator invokes a lock command on a channel, THE Discord Bot SHALL remove send message permissions for all non-moderator roles
3. WHEN an administrator invokes an unlock command on a channel, THE Discord Bot SHALL restore send message permissions to their previous state
4. WHEN an administrator invokes a role command with a user mention and role name, THE Discord Bot SHALL add or remove the specified role from the user
5. WHEN an administrator invokes a nickname command with a user mention and new name, THE Discord Bot SHALL change the user's server nickname to the specified value

### Requirement 3

**User Story:** As a server administrator, I want moderation logging and history, so that I can track all moderation actions and user infractions

#### Acceptance Criteria

1. WHEN any moderation action is executed, THE Discord Bot SHALL create a log entry in a designated moderation log channel with action type, target user, moderator, reason, and timestamp
2. WHEN an administrator invokes a warnings command with a user mention, THE Discord Bot SHALL display all recorded warnings for that user with dates and reasons
3. WHEN an administrator invokes a modlogs command with a user mention, THE Discord Bot SHALL display all moderation actions taken against that user
4. WHEN an administrator invokes a case command with a case number, THE Discord Bot SHALL display detailed information about that specific moderation action
5. WHEN an administrator invokes a clearwarnings command with a user mention, THE Discord Bot SHALL remove all warnings for the specified user and log the action

### Requirement 4

**User Story:** As a Blox Fruits player, I want to check current stock information, so that I can know which fruits are available in the game

#### Acceptance Criteria

1. WHEN a user invokes a bloxfruits stock command, THE Discord Bot SHALL fetch current stock data from a Blox Fruits API or data source
2. WHEN stock data is retrieved successfully, THE Discord Bot SHALL display available fruits in an organized embed with fruit names and availability status
3. WHEN the stock data source is unavailable, THE Discord Bot SHALL display an error message indicating the service is temporarily unavailable
4. WHEN a user invokes a bloxfruits notify command with a fruit name, THE Discord Bot SHALL add the user to a notification list for that specific fruit
5. WHEN a specified fruit becomes available in stock, THE Discord Bot SHALL send notifications to all users who requested alerts for that fruit

### Requirement 5

**User Story:** As a content creator, I want YouTube upload notifications, so that my community is immediately informed when I post new videos

#### Acceptance Criteria

1. WHEN an administrator invokes a youtube add command with a channel URL and notification channel, THE Discord Bot SHALL subscribe to that YouTube channel for upload notifications
2. WHEN a subscribed YouTube channel uploads a new video, THE Discord Bot SHALL post a notification in the designated Discord channel within 5 minutes
3. WHEN a YouTube notification is posted, THE Discord Bot SHALL include the video title, thumbnail, channel name, and direct link in an embed
4. WHEN an administrator invokes a youtube remove command with a channel URL, THE Discord Bot SHALL unsubscribe from that YouTube channel
5. WHEN an administrator invokes a youtube list command, THE Discord Bot SHALL display all currently subscribed YouTube channels and their notification destinations

### Requirement 6

**User Story:** As a server member, I want fun and utility commands, so that I can interact with the bot for entertainment and helpful information

#### Acceptance Criteria

1. WHEN a user invokes a poll command with a question and options, THE Discord Bot SHALL create an interactive poll with reaction-based voting
2. WHEN a user invokes a userinfo command with an optional user mention, THE Discord Bot SHALL display account creation date, join date, roles, and status information
3. WHEN a user invokes a serverinfo command, THE Discord Bot SHALL display server creation date, member count, role count, and channel count
4. WHEN a user invokes an avatar command with an optional user mention, THE Discord Bot SHALL display the user's profile picture in full resolution
5. WHEN a user invokes a remind command with a time duration and message, THE Discord Bot SHALL send a direct message reminder to the user after the specified time

### Requirement 7

**User Story:** As a server administrator, I want auto-moderation features, so that the bot can automatically handle common moderation scenarios

#### Acceptance Criteria

1. WHEN a user posts a message containing words from the configured blacklist, THE Discord Bot SHALL delete the message and issue an automatic warning
2. WHEN a user posts more than 5 messages within 3 seconds, THE Discord Bot SHALL automatically mute the user for spam and notify moderators
3. WHEN a user posts a message with excessive caps (over 70% uppercase), THE Discord Bot SHALL delete the message and send a warning
4. WHEN a user posts a Discord invite link without permission, THE Discord Bot SHALL delete the message and log the attempt
5. WHEN an administrator invokes an automod config command, THE Discord Bot SHALL allow enabling or disabling specific auto-moderation rules

### Requirement 8

**User Story:** As a server administrator, I want economy and leveling commands, so that I can gamify user engagement in my server

#### Acceptance Criteria

1. WHEN a user sends messages in the server, THE Discord Bot SHALL award experience points based on message activity with a cooldown of 60 seconds between awards
2. WHEN a user accumulates sufficient experience points, THE Discord Bot SHALL automatically increase their level and announce the level-up in the channel
3. WHEN a user invokes a balance command, THE Discord Bot SHALL display their current virtual currency balance
4. WHEN a user invokes a daily command, THE Discord Bot SHALL award a daily currency bonus with a 24-hour cooldown
5. WHEN a user invokes a leaderboard command, THE Discord Bot SHALL display the top 10 users by level or currency balance

### Requirement 9

**User Story:** As a server administrator, I want music playback commands, so that users can listen to music together in voice channels

#### Acceptance Criteria

1. WHEN a user invokes a play command with a YouTube URL or search query while in a voice channel, THE Discord Bot SHALL join the voice channel and begin playing the requested audio
2. WHEN a user invokes a pause command while music is playing, THE Discord Bot SHALL pause the current track
3. WHEN a user invokes a skip command while music is playing, THE Discord Bot SHALL skip to the next track in the queue
4. WHEN a user invokes a queue command, THE Discord Bot SHALL display all tracks currently in the playback queue
5. WHEN a user invokes a leave command, THE Discord Bot SHALL disconnect from the voice channel and clear the queue

### Requirement 10

**User Story:** As a server administrator, I want custom command creation, so that I can add server-specific commands without coding

#### Acceptance Criteria

1. WHEN an administrator invokes a customcmd add command with a trigger and response, THE Discord Bot SHALL store the custom command in the database
2. WHEN a user invokes a custom command trigger, THE Discord Bot SHALL respond with the configured response text
3. WHEN an administrator invokes a customcmd remove command with a trigger name, THE Discord Bot SHALL delete the custom command from the database
4. WHEN an administrator invokes a customcmd list command, THE Discord Bot SHALL display all custom commands configured for the server
5. WHERE a custom command includes variable placeholders, THE Discord Bot SHALL replace them with dynamic values like user mentions or server information

### Requirement 11

**User Story:** As a server administrator, I want welcome and goodbye messages, so that I can automatically greet new members and acknowledge departures

#### Acceptance Criteria

1. WHEN a new user joins the server, THE Discord Bot SHALL send a customizable welcome message in the designated welcome channel
2. WHEN a user leaves the server, THE Discord Bot SHALL send a customizable goodbye message in the designated goodbye channel
3. WHEN an administrator invokes a setwelcome command with a channel and message template, THE Discord Bot SHALL configure the welcome message settings
4. WHEN an administrator invokes a setgoodbye command with a channel and message template, THE Discord Bot SHALL configure the goodbye message settings
5. WHERE welcome or goodbye messages include placeholders, THE Discord Bot SHALL replace them with user-specific information like username and member count

### Requirement 12

**User Story:** As a server member, I want game and entertainment commands, so that I can have fun interactions with the bot

#### Acceptance Criteria

1. WHEN a user invokes an 8ball command with a question, THE Discord Bot SHALL respond with a random fortune-teller style answer
2. WHEN a user invokes a coinflip command, THE Discord Bot SHALL randomly return either heads or tails
3. WHEN a user invokes a dice command with an optional number of sides, THE Discord Bot SHALL return a random number within the specified range
4. WHEN a user invokes a meme command, THE Discord Bot SHALL fetch and display a random meme from a meme API
5. WHEN a user invokes a joke command, THE Discord Bot SHALL fetch and display a random joke from a joke API
