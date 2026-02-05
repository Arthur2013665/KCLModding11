# 🛡️ KCLAntivirus Setup Guide

## Overview
KCLAntivirus is a comprehensive server protection system that automatically scans files and URLs for malicious content using the VirusTotal API, detects potential raids, and provides emergency server lockdown capabilities.

## 🚀 Features

### Automatic Protection
- **File Scanning** - Automatically scans all uploaded files using VirusTotal
- **URL Scanning** - Scans links posted in messages for malicious content
- **Raid Detection** - Monitors for suspicious activity patterns
- **Auto-Lockdown** - Automatically kicks non-protected users during detected raids
- **Smart Filtering** - Bypasses scans for trusted roles and safe file types

### Manual Controls
- **Server Scan** - Comprehensive server security audit
- **Force Lockdown** - Emergency manual server lockdown
- **Protected Roles** - Configure which roles are immune to antivirus actions
- **Detailed Logging** - Complete audit trail of all security events

## 📋 Prerequisites

### 1. VirusTotal API Key
1. Go to [VirusTotal](https://www.virustotal.com/)
2. Create a free account
3. Go to your profile → API Key
4. Copy your API key

### 2. Bot Permissions
Ensure your bot has these permissions:
- Manage Messages (delete malicious content)
- Moderate Members (timeout users)
- Kick Members (for lockdowns)
- Send Messages (alerts and logs)
- Embed Links (rich embeds)

## ⚙️ Setup Instructions

### Step 1: Configure API Key
Add your VirusTotal API key to the `.env` file:
```env
VIRUSTOTAL_API_KEY=your_virustotal_api_key_here
```

### Step 2: Enable KCLAntivirus
```
/antivirus-setup enabled:True
```

### Step 3: Configure Logging Channel
```
/antivirus-setup mod_log_channel:#security-logs
```

### Step 4: Set Up Protected Roles
```
/antivirus-protected-roles action:add role:@Staff
/antivirus-protected-roles action:add role:@Moderators
/antivirus-protected-roles action:add role:@Admins
```

### Step 5: Configure Auto-Lockdown (Optional)
```
/antivirus-setup auto_lockdown:True
```

### Step 6: Test the System
Upload a test file or post a URL to verify scanning works.

## 🎛️ Commands Reference

### Setup Commands
| Command | Description | Permission |
|---------|-------------|------------|
| `/antivirus-setup` | Configure main settings | Manage Messages |
| `/antivirus-status` | View current configuration | Manage Messages |
| `/antivirus-protected-roles` | Manage protected roles | Manage Messages |

### Security Commands
| Command | Description | Permission |
|---------|-------------|------------|
| `/server-scan` | Scan server for threats | Manage Messages |
| `/server-lockdown` | Force emergency lockdown | Manage Messages |

## 🔧 Configuration Options

### Main Settings
- **enabled** - Enable/disable the entire system
- **auto_lockdown** - Automatically lockdown on raid detection
- **mod_log_channel** - Channel for security logs
- **scan_attachments** - Scan uploaded files
- **scan_urls** - Scan posted URLs

### Detection Thresholds
- **Malicious Threshold**: 1 engine detection = immediate action
- **Suspicious Threshold**: 3 engine detections = action taken
- **Raid Detection**: 10 users joining or 20 messages in 60 seconds

### Protection Levels
1. **Automatic Protection** - Users with Admin, Manage Server, or Manage Messages
2. **Custom Protected Roles** - Roles you specifically whitelist
3. **Regular Users** - Subject to all antivirus actions

## 🚨 How It Works

### File/URL Scanning Process
1. User uploads file or posts URL
2. System checks if user is protected (skip if yes)
3. File/URL sent to VirusTotal for analysis
4. If threat detected:
   - Message deleted immediately
   - User timed out for 1 day
   - Warning added to user record
   - Incident logged to security channel
   - User receives DM explanation

### Raid Detection Process
1. System monitors user joins and message activity
2. If thresholds exceeded:
   - Alert sent to moderators
   - If auto-lockdown enabled: emergency lockdown triggered
3. During lockdown:
   - All non-protected users kicked
   - Users receive DM explanation
   - Server announcement posted
   - Full incident logged

### Server Scan Process
1. Analyzes recent user activity patterns
2. Identifies high-activity users
3. Checks for raid indicators
4. Provides security recommendations
5. Generates comprehensive report

## 📊 Monitoring & Logs

### Security Events Logged
- ✅ Malicious file/URL detections
- ✅ User timeouts and warnings
- ✅ Raid detection alerts
- ✅ Server lockdown events
- ✅ System configuration changes

### Log Information Includes
- Timestamp and user details
- Threat type and severity
- VirusTotal detection counts
- Actions taken
- Message content (if applicable)

## 🛠️ Troubleshooting

### System Not Working
1. Check if enabled: `/antivirus-status`
2. Verify API key is set in `.env` file
3. Ensure bot has required permissions
4. Check if user has protected role

### False Positives
- Add user's role to protected roles temporarily
- Check VirusTotal results manually
- Adjust detection thresholds if needed

### API Limits
- Free VirusTotal API: 4 requests/minute, 500/day
- Consider upgrading for high-traffic servers
- System automatically handles rate limits

### Lockdown Issues
- Ensure bot has "Kick Members" permission
- Verify protected roles are configured correctly
- Check that bot's role is high enough in hierarchy

## ⚡ Advanced Features

### File Type Handling
- **Safe Extensions**: .txt, .md, .json, .yml, .yaml, .log (skipped)
- **Dangerous Extensions**: .exe, .scr, .bat, .cmd, .com, .pif, .vbs, .js (auto-flagged)
- **Other Files**: Scanned via VirusTotal

### Raid Detection Patterns
- Mass user joins (10+ in 60 seconds)
- Message spam (20+ messages in 60 seconds)
- Coordinated activity from new accounts
- Suspicious username patterns

### Emergency Procedures
1. **Immediate Threat**: Use `/server-lockdown` instantly
2. **Suspected Raid**: Run `/server-scan` first for analysis
3. **False Alarm**: Protected users remain unaffected
4. **Recovery**: Users can rejoin after threat cleared

## 🔐 Security Best Practices

### Role Configuration
- Keep protected roles minimal
- Regularly audit protected role list
- Use hierarchy: Owner > Admin > Moderator > Staff
- Don't protect roles that don't need immunity

### Monitoring
- Check security logs daily
- Review scan results weekly
- Monitor for false positive patterns
- Update protected roles as staff changes

### Emergency Preparedness
- Train moderators on lockdown procedures
- Have communication plan for lockdown events
- Keep backup invite links ready
- Document incident response procedures

## 📈 Performance Impact

### Resource Usage
- Minimal CPU impact during normal operation
- Network usage depends on file/URL volume
- Database storage for logs and settings
- Memory usage scales with server activity

### API Considerations
- Free tier sufficient for most servers
- Paid tier recommended for 1000+ member servers
- Automatic rate limit handling
- Graceful degradation if API unavailable

## 🆘 Support & Maintenance

### Regular Maintenance
- Monitor API usage monthly
- Clean old scan logs quarterly
- Review and update protected roles
- Test lockdown procedures periodically

### Getting Help
- Check `/antivirus-status` for configuration issues
- Review security logs for patterns
- Test with small files first
- Contact support with specific error messages

---

**KCLAntivirus provides enterprise-grade security for your Discord server. Configure it properly and monitor regularly for best results!**