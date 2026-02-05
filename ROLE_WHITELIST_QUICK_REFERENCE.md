# 🎭 Role Whitelist Quick Reference

## Quick Setup Commands

### Enable Anti-Ping System
```
/automod feature:everyone-ping enabled:True
```

### Add Trusted Roles
```
/everyone-whitelist action:add role:@Staff
/everyone-whitelist action:add role:@Moderators
/everyone-whitelist action:add role:@Admins
```

### View Current Setup
```
/automod-status
/everyone-whitelist action:list
```

## Permission Hierarchy

| Priority | User Type | Can Ping @everyone? | Notes |
|----------|-----------|-------------------|-------|
| 1 | Users with "Manage Messages" | ✅ Always | Discord permission |
| 2 | Users with whitelisted roles | ✅ Yes | Custom whitelist |
| 3 | Regular members | ❌ Blocked | Gets warning + logged |

## Common Role Setups

### Basic Server
```
/everyone-whitelist action:add role:@Staff
```

### Gaming Community
```
/everyone-whitelist action:add role:@Admins
/everyone-whitelist action:add role:@Moderators
/everyone-whitelist action:add role:@Event-Host
```

### Business/Organization
```
/everyone-whitelist action:add role:@Management
/everyone-whitelist action:add role:@HR
/everyone-whitelist action:add role:@Announcements
```

### Content Creator Server
```
/everyone-whitelist action:add role:@Creator
/everyone-whitelist action:add role:@Editors
/everyone-whitelist action:add role:@Stream-Team
```

## Management Commands

| Action | Command | Example |
|--------|---------|---------|
| Add role | `/everyone-whitelist action:add role:@RoleName` | Add @Staff to whitelist |
| Remove role | `/everyone-whitelist action:remove role:@RoleName` | Remove @Staff from whitelist |
| List roles | `/everyone-whitelist action:list` | Show all whitelisted roles |
| Clear all | `/everyone-whitelist action:clear` | Remove all roles from whitelist |

## What Happens When...

### ✅ Whitelisted User Pings @everyone
- Message goes through normally
- No warnings or deletions
- Works just like having "Manage Messages" permission

### ❌ Regular User Pings @everyone
- Message gets deleted instantly
- User sees: "🚫 You don't have permission to ping @everyone or @here"
- Warning added to their record
- Incident logged to mod channel

### 🔧 Role Gets Removed from Server
- Automatically cleaned from whitelist
- No manual cleanup needed
- System handles deleted roles gracefully

## Pro Tips

- 🎯 **Keep it minimal** - Only whitelist roles that truly need @everyone access
- 🔄 **Regular audits** - Use `/everyone-whitelist action:list` monthly
- 📋 **Document your choices** - Keep track of why each role is whitelisted
- 🧪 **Test thoroughly** - Verify with different user accounts before going live
- 🚨 **Monitor logs** - Check mod logs to see if the system is working as expected

## Troubleshooting

**Role can't ping @everyone despite being whitelisted?**
- Check if user actually has the role assigned
- Verify role is still in whitelist: `/everyone-whitelist action:list`
- Ensure bot has "Manage Messages" permission

**Too many false positives?**
- Add more roles to whitelist as needed
- Consider if users need temporary @everyone access for events

**System not working at all?**
- Check: `/automod-status`
- Ensure feature is enabled: `/automod feature:everyone-ping enabled:True`
- Verify bot permissions in server settings