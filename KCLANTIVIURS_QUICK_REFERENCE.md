# 🛡️ KCLAntivirus Quick Reference

## 🚀 Quick Setup (5 Minutes)

```bash
# 1. Add API key to .env file
VIRUSTOTAL_API_KEY=your_key_here

# 2. Enable system
/antivirus-setup enabled:True

# 3. Set log channel
/antivirus-setup mod_log_channel:#security-logs

# 4. Add protected roles
/antivirus-protected-roles action:add role:@Staff

# 5. Check status
/antivirus-status
```

## 🎯 Essential Commands

| Command | What It Does | When To Use |
|---------|--------------|-------------|
| `/antivirus-setup` | Configure main settings | Initial setup |
| `/antivirus-status` | View current config | Check if working |
| `/server-scan` | Scan for threats | Suspicious activity |
| `/server-lockdown` | Emergency lockdown | Under attack |
| `/antivirus-protected-roles` | Manage immune roles | Add/remove staff |

## ⚡ Emergency Procedures

### 🚨 Under Raid Attack
```bash
# Quick response
/server-lockdown reason:"Raid detected"

# Or scan first
/server-scan
# Then decide on lockdown
```

### 🔍 Suspicious Activity
```bash
# Investigate first
/server-scan

# Check recent logs
/antivirus-status

# Add temporary protection if needed
/antivirus-protected-roles action:add role:@TrustedMembers
```

## 🛡️ Protection Levels

| Level | Who | Protected From |
|-------|-----|----------------|
| **Auto** | Admin/Manage Server/Manage Messages | Everything |
| **Custom** | Your protected roles | Everything |
| **Regular** | Everyone else | Scans, timeouts, lockdowns |

## 🎛️ Key Settings

### Detection Thresholds
- **Malicious**: 1+ engines = instant action
- **Suspicious**: 3+ engines = action taken
- **Raid**: 10 joins OR 20 messages in 60s

### Actions Taken
- **Malicious File/URL**: Delete + 1 day timeout + warning + DM
- **Raid Detected**: Alert mods (+ auto-lockdown if enabled)
- **Server Lockdown**: Kick all non-protected users + DM them

## 📊 What Gets Scanned

### ✅ Always Scanned
- All uploaded files (except safe extensions)
- All URLs in messages
- User activity patterns

### ❌ Never Scanned
- Messages from protected users
- Safe file types (.txt, .md, .json, etc.)
- Bot messages

### ⚠️ Auto-Flagged
- Dangerous extensions (.exe, .bat, .scr, etc.)
- Files too large for VirusTotal (32MB+)

## 🔧 Troubleshooting

| Problem | Solution |
|---------|----------|
| Not scanning files | Check `/antivirus-status` - ensure enabled |
| False positives | Add user's role to protected roles |
| API errors | Verify VirusTotal API key in `.env` |
| Can't kick users | Check bot permissions and role hierarchy |
| No logs appearing | Set mod log channel in setup |

## 📈 Monitoring Checklist

### Daily
- [ ] Check security logs for threats
- [ ] Review any lockdown events
- [ ] Monitor false positive reports

### Weekly  
- [ ] Run `/server-scan` for health check
- [ ] Review protected roles list
- [ ] Check API usage (if high traffic)

### Monthly
- [ ] Audit security logs
- [ ] Update protected roles as needed
- [ ] Test lockdown procedures

## 🚨 Red Flags (Take Action)

- Multiple malicious files from same user
- Coordinated posting of suspicious links
- Mass user joins with similar names
- High message volume from new accounts
- Multiple VirusTotal detections in short time

## 💡 Pro Tips

### Setup
- Start with auto-lockdown OFF until you trust the system
- Add your most trusted roles to protection first
- Set up a dedicated security log channel
- Test with harmless files first

### Management
- Protected roles should be minimal but comprehensive
- Monitor logs regularly for patterns
- Keep emergency contact info handy
- Document your incident response procedures

### Performance
- Free VirusTotal API handles most servers fine
- Consider paid tier for 1000+ member servers
- System auto-handles rate limits gracefully
- Minimal impact on server performance

---

**🛡️ KCLAntivirus: Your server's digital immune system!**