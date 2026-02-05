# Anti-Ping System Setup Guide

## Overview
The anti-ping system prevents regular members from using @everyone and @here mentions, automatically deleting such messages and warning the users. You can configure which roles are allowed to bypass this protection.

## Features
- 🚫 Blocks @everyone and @here pings from unauthorized users
- 👥 Role-based whitelist system for trusted roles
- ⚠️ Automatically adds warnings to users who attempt to ping everyone
- 📝 Logs all blocked attempts to the moderation log channel
- ⚙️ Configurable on/off toggle per server

## Setup Instructions

### 1. Enable the Feature
Use the `/automod` command to enable everyone ping protection:
```
/automod feature:everyone-ping enabled:True
```

### 2. Configure Whitelisted Roles (Optional)
Add roles that should be allowed to ping @everyone/@here:
```
/everyone-whitelist action:add role:@Staff
/everyone-whitelist action:add role:@Moderators
/everyone-whitelist action:add role:@Admins
```

### 3. Configure Moderation Log Channel (Optional)
To see logs of blocked pings, set up a mod log channel:
```
/setup mod-log channel:#mod-logs
```

### 4. Check Status
View current automod settings and whitelist:
```
/automod-status
/everyone-whitelist action:list
```

## How It Works

### Permission Hierarchy (in order of priority)
1. **Users with "Manage Messages" permission** - Always allowed
2. **Users with whitelisted roles** - Allowed to ping @everyone/@here
3. **Regular members** - Blocked and warned

### For Regular Members
- Any message containing @everyone or @here will be automatically deleted
- User receives a warning message (deleted after 10 seconds)
- A warning is added to their record
- The attempt is logged to the mod log channel

### For Whitelisted Roles
- Can use @everyone/@here freely
- No warnings or deletions
- Useful for staff, event organizers, announcement roles, etc.

### Example Blocked Message
```
User: "Hey @everyone check this out!"
Bot: "🚫 @User, you don't have permission to ping @everyone or @here."
```

## Commands

### Main Commands
| Command | Description | Permission Required |
|---------|-------------|-------------------|
| `/automod feature:everyone-ping enabled:True/False` | Enable/disable everyone ping protection | Manage Messages |
| `/automod-status` | View current automod settings | Manage Messages |

### Whitelist Management
| Command | Description | Permission Required |
|---------|-------------|-------------------|
| `/everyone-whitelist action:add role:@RoleName` | Add role to whitelist | Manage Messages |
| `/everyone-whitelist action:remove role:@RoleName` | Remove role from whitelist | Manage Messages |
| `/everyone-whitelist action:list` | View all whitelisted roles | Manage Messages |
| `/everyone-whitelist action:clear` | Remove all roles from whitelist | Manage Messages |

## Configuration Examples

### Basic Setup (Staff Only)
```
/automod feature:everyone-ping enabled:True
/everyone-whitelist action:add role:@Staff
```

### Advanced Setup (Multiple Roles)
```
/automod feature:everyone-ping enabled:True
/everyone-whitelist action:add role:@Admins
/everyone-whitelist action:add role:@Moderators
/everyone-whitelist action:add role:@Event-Organizers
/everyone-whitelist action:add role:@News-Team
```

### Event-Specific Setup
```
# Temporarily add event role
/everyone-whitelist action:add role:@Event-Host

# Remove after event
/everyone-whitelist action:remove role:@Event-Host
```

## Troubleshooting

### The system isn't working
1. Check if automod is enabled: `/automod-status`
2. Ensure the bot has "Manage Messages" permission
3. Verify the feature is enabled: `/automod feature:everyone-ping enabled:True`

### A role can't ping everyone
1. Check if the role is whitelisted: `/everyone-whitelist action:list`
2. Add the role: `/everyone-whitelist action:add role:@RoleName`
3. Verify users have the role assigned

### Too many roles can ping everyone
1. View current whitelist: `/everyone-whitelist action:list`
2. Remove specific roles: `/everyone-whitelist action:remove role:@RoleName`
3. Or clear all: `/everyone-whitelist action:clear`

### No logs appearing
- Ensure a mod log channel is set up: `/setup mod-log channel:#your-channel`
- Check that the bot has permission to send messages in the log channel

## Best Practices

### Recommended Whitelisted Roles
- 👑 **Admin/Owner roles** - Full server management
- 🛡️ **Moderator roles** - Community management
- 📢 **Announcement roles** - Official server news
- 🎉 **Event organizer roles** - Special events
- 📰 **News team roles** - Updates and information

### Security Tips
- 🔒 Keep the whitelist minimal - only trusted roles
- 🔄 Regularly review whitelisted roles
- 📋 Use `/everyone-whitelist action:list` to audit permissions
- 🗑️ Remove roles that are no longer needed

## Integration with Existing Systems

This feature works alongside:
- ✅ Existing warning system
- ✅ Moderation logging
- ✅ Other automod features (spam, blacklist)
- ✅ Discord's built-in permission system
- ✅ Role hierarchy and management

The enhanced anti-ping system gives you granular control over who can ping @everyone while maintaining security!