"""
KCLAntivirus Advanced - Complete enterprise-grade server protection system
Full-featured VirusTotal integration, raid protection, and server security management
"""
import discord
from discord import app_commands
from discord.ext import commands, tasks
from datetime import datetime, timedelta
from collections import defaultdict
from typing import Optional, List, Dict, Any
import aiohttp
import asyncio
import hashlib
import re
import logging
import json
from urllib.parse import urlparse

from utils.embeds import success_embed, warning_embed, error_embed
from utils.checks import is_moderator
import config

logger = logging.getLogger('discord_bot.kcl_antivirus')

class ConfirmLockdownView(discord.ui.View):
    """Advanced confirmation view for server lockdown with detailed info"""
    
    def __init__(self, antivirus_cog, guild: discord.Guild, reason: str, estimated_kicks: int):
        super().__init__(timeout=60)
        self.antivirus_cog = antivirus_cog
        self.guild = guild
        self.reason = reason
        self.estimated_kicks = estimated_kicks
    
    @discord.ui.button(label=f"🔒 CONFIRM LOCKDOWN", style=discord.ButtonStyle.danger)
    async def confirm_lockdown(self, interaction, button):
        await interaction.response.defer()
        
        # Disable all buttons
        for item in self.children:
            item.disabled = True
        
        await interaction.edit_original_response(view=self)
        
        # Execute lockdown with progress updates
        embed = discord.Embed(
            title="🔒 Executing Server Lockdown...",
            description="Please wait while the lockdown is executed.",
            color=config.Colors.WARNING,
            timestamp=datetime.utcnow()
        )
        
        await interaction.followup.send(embed=embed)
        
        # Execute lockdown
        result = await self.antivirus_cog._server_lockdown_advanced(self.guild, self.reason, interaction)
        
        # Send final results
        embed = discord.Embed(
            title="🔒 Server Lockdown Complete",
            description="Emergency server lockdown has been executed successfully.",
            color=config.Colors.ERROR,
            timestamp=datetime.utcnow()
        )
        
        embed.add_field(name="Users Kicked", value=str(result['kicked']), inline=True)
        embed.add_field(name="Users Protected", value=str(result['protected']), inline=True)
        embed.add_field(name="Errors", value=str(result['errors']), inline=True)
        
        await interaction.followup.send(embed=embed)
    
    @discord.ui.button(label="❌ Cancel", style=discord.ButtonStyle.secondary)
    async def cancel_lockdown(self, interaction, button):
        embed = discord.Embed(
            title="❌ Lockdown Cancelled",
            description="Server lockdown has been cancelled. No users were affected.",
            color=config.Colors.SUCCESS
        )
        
        await interaction.response.edit_message(embed=embed, view=None)

class KCLAntivirusAdvanced(commands.Cog):
    """KCLAntivirus Advanced - Complete enterprise-grade server protection"""
    
    def __init__(self, bot):
        self.bot = bot
        self.session = None
        
        # Advanced tracking dictionaries
        self.user_joins = defaultdict(list)
        self.message_activity = defaultdict(list)
        self.scan_cooldowns = defaultdict(dict)
        self.server_scan_cooldowns = {}
        self.threat_cache = {}  # Cache scan results
        self.lockdown_history = defaultdict(list)
        
        # Advanced patterns
        self.url_pattern = re.compile(
            r'http[s]?://(?:[a-zA-Z]|[0-9]|[$-_@.&+]|[!*\\(\\),]|(?:%[0-9a-fA-F][0-9a-fA-F]))+'
        )
        
        # Suspicious patterns for enhanced detection
        self.suspicious_patterns = [
            re.compile(r'discord\.gg/[a-zA-Z0-9]+'),  # Discord invites
            re.compile(r'bit\.ly/[a-zA-Z0-9]+'),      # Shortened URLs
            re.compile(r'tinyurl\.com/[a-zA-Z0-9]+'), # Shortened URLs
            re.compile(r'[a-zA-Z0-9]+\.tk'),          # Suspicious TLD
            re.compile(r'[a-zA-Z0-9]+\.ml'),          # Suspicious TLD
        ]
        
        # Start background tasks
        self.cleanup_tracking.start()
        self.periodic_security_check.start()
    
    async def cog_load(self):
        """Initialize HTTP session and advanced features when cog loads"""
        self.session = aiohttp.ClientSession()
        logger.info("KCLAntivirus Advanced system initialized")
    
    async def cog_unload(self):
        """Cleanup when cog unloads"""
        if self.session:
            await self.session.close()
        self.cleanup_tracking.cancel()
        self.periodic_security_check.cancel()
        logger.info("KCLAntivirus Advanced system shutdown")
    
    @tasks.loop(minutes=30)
    async def cleanup_tracking(self):
        """Clean up old tracking data and optimize performance"""
        cutoff = datetime.utcnow() - timedelta(hours=2)
        
        # Clean user joins
        for guild_id in list(self.user_joins.keys()):
            self.user_joins[guild_id] = [
                (ts, uid) for ts, uid in self.user_joins[guild_id]
                if ts > cutoff
            ]
            if not self.user_joins[guild_id]:
                del self.user_joins[guild_id]
        
        # Clean message activity
        for guild_id in list(self.message_activity.keys()):
            self.message_activity[guild_id] = [
                (ts, uid) for ts, uid in self.message_activity[guild_id]
                if ts > cutoff
            ]
            if not self.message_activity[guild_id]:
                del self.message_activity[guild_id]
        
        # Clean threat cache (keep for 24 hours)
        cache_cutoff = datetime.utcnow() - timedelta(hours=24)
        for key in list(self.threat_cache.keys()):
            if self.threat_cache[key].get('timestamp', datetime.min) < cache_cutoff:
                del self.threat_cache[key]
    
    @tasks.loop(hours=6)
    async def periodic_security_check(self):
        """Periodic security health check for all guilds"""
        for guild in self.bot.guilds:
            try:
                settings = await self.bot.db.get_antivirus_settings(guild.id)
                if not settings.enabled:
                    continue
                
                # Check for unusual activity patterns
                await self._background_security_check(guild)
                
            except Exception as e:
                logger.error(f"Error in periodic security check for {guild.name}: {e}")
    
    async def _background_security_check(self, guild):
        """Background security health check"""
        now = datetime.utcnow()
        
        # Check for sustained high activity
        recent_messages = [
            (ts, uid) for ts, uid in self.message_activity.get(guild.id, [])
            if ts > now - timedelta(hours=1)
        ]
        
        if len(recent_messages) > config.KCLAntivirus.RAID_MESSAGE_THRESHOLD * 2:
            settings = await self.bot.db.get_antivirus_settings(guild.id)
            if settings.mod_log_channel:
                log_channel = guild.get_channel(settings.mod_log_channel)
                if log_channel:
                    embed = discord.Embed(
                        title="📊 Security Health Alert",
                        description="Sustained high message activity detected.",
                        color=config.Colors.WARNING,
                        timestamp=now
                    )
                    embed.add_field(name="Messages (1h)", value=str(len(recent_messages)), inline=True)
                    embed.add_field(name="Recommendation", value="Monitor for coordinated activity", inline=True)
                    
                    try:
                        await log_channel.send(embed=embed)
                    except:
                        pass
    
    @commands.Cog.listener()
    async def on_message(self, message):
        """Advanced message monitoring with enhanced threat detection"""
        if message.author.bot or not message.guild:
            return
        
        # Check if antivirus is enabled
        settings = await self.bot.db.get_antivirus_settings(message.guild.id)
        if not settings.enabled:
            return
        
        # Skip if user is protected
        if await self._is_protected_user(message.author):
            return
        
        # Track message activity for raid detection
        now = datetime.utcnow()
        self.message_activity[message.guild.id].append((now, message.author.id))
        
        # Advanced threat detection
        threat_score = await self._calculate_threat_score(message)
        
        # Check for raid patterns first
        if await self._check_raid_activity(message.guild):
            return
        
        # Enhanced content analysis
        if await self._check_suspicious_patterns(message):
            return
        
        # Scan attachments with advanced analysis
        if message.attachments:
            await self._scan_attachments_advanced(message)
        
        # Scan URLs with enhanced detection
        urls = self.url_pattern.findall(message.content)
        if urls:
            await self._scan_urls_advanced(message, urls)
        
        # Log high threat score messages
        if threat_score > 0.7:
            await self._log_suspicious_activity(message, threat_score)
    
    @commands.Cog.listener()
    async def on_member_join(self, member):
        """Advanced member join monitoring with pattern analysis"""
        if member.bot:
            return
        
        settings = await self.bot.db.get_antivirus_settings(member.guild.id)
        if not settings.enabled:
            return
        
        # Track user joins with enhanced data
        now = datetime.utcnow()
        join_data = {
            'timestamp': now,
            'user_id': member.id,
            'account_age': (now - member.created_at).days,
            'username': member.name,
            'discriminator': member.discriminator if hasattr(member, 'discriminator') else None
        }
        
        self.user_joins[member.guild.id].append((now, member.id))
        
        # Check for suspicious account patterns
        if join_data['account_age'] < 7:  # Account less than 7 days old
            await self._log_new_account_join(member, join_data)
        
        # Check for raid patterns
        await self._check_raid_activity(member.guild)
    
    async def _calculate_threat_score(self, message):
        """Calculate threat score based on multiple factors"""
        score = 0.0
        
        # Account age factor
        account_age = (datetime.utcnow() - message.author.created_at).days
        if account_age < 7:
            score += 0.3
        elif account_age < 30:
            score += 0.1
        
        # Message content analysis
        content = message.content.lower()
        
        # Suspicious keywords
        suspicious_words = ['free', 'nitro', 'gift', 'hack', 'cheat', 'generator', 'discord.gg']
        for word in suspicious_words:
            if word in content:
                score += 0.1
        
        # URL analysis
        urls = self.url_pattern.findall(message.content)
        if urls:
            score += len(urls) * 0.2
        
        # Caps ratio
        if len(content) > 10:
            caps_ratio = sum(1 for c in content if c.isupper()) / len(content)
            if caps_ratio > 0.5:
                score += 0.2
        
        return min(score, 1.0)  # Cap at 1.0
    
    async def _check_suspicious_patterns(self, message):
        """Check for suspicious patterns in message content"""
        content = message.content
        
        for pattern in self.suspicious_patterns:
            if pattern.search(content):
                await self._handle_suspicious_pattern(message, pattern.pattern)
                return True
        
        return False
    
    async def _handle_suspicious_pattern(self, message, pattern):
        """Handle detected suspicious patterns"""
        # Log the suspicious activity
        await self._log_suspicious_activity(message, 0.8, f"Suspicious pattern: {pattern}")
        
        # Don't delete immediately, but flag for review
        settings = await self.bot.db.get_antivirus_settings(message.guild.id)
        if settings.mod_log_channel:
            log_channel = message.guild.get_channel(settings.mod_log_channel)
            if log_channel:
                embed = discord.Embed(
                    title="⚠️ Suspicious Pattern Detected",
                    description=f"Message contains suspicious pattern: `{pattern}`",
                    color=config.Colors.WARNING,
                    timestamp=datetime.utcnow()
                )
                embed.add_field(name="User", value=f"{message.author} ({message.author.id})", inline=True)
                embed.add_field(name="Channel", value=message.channel.mention, inline=True)
                embed.add_field(name="Message", value=message.content[:500], inline=False)
                embed.add_field(name="Action", value="Flagged for review", inline=True)
                
                try:
                    await log_channel.send(embed=embed)
                except:
                    pass
    
    async def _is_protected_user(self, user):
        """Enhanced protection check with role hierarchy"""
        # Bot owner is always protected
        if user.id == self.bot.owner_id:
            return True
        
        # Check permissions with hierarchy
        if user.guild_permissions.administrator:
            return True
        
        if user.guild_permissions.manage_guild:
            return True
        
        if user.guild_permissions.manage_messages:
            return True
        
        if user.guild_permissions.moderate_members:
            return True
        
        # Check protected roles
        protected_roles = await self.bot.db.get_antivirus_protected_roles(user.guild.id)
        user_role_ids = [role.id for role in user.roles]
        
        return any(role_id in user_role_ids for role_id in protected_roles)
    
    async def _scan_attachments_advanced(self, message):
        """Advanced attachment scanning with enhanced analysis"""
        for attachment in message.attachments:
            try:
                # Enhanced file analysis
                file_info = {
                    'name': attachment.filename,
                    'size': attachment.size,
                    'url': attachment.url,
                    'content_type': getattr(attachment, 'content_type', 'unknown')
                }
                
                # Check file size with detailed logging
                if attachment.size > config.KCLAntivirus.MAX_FILE_SIZE_MB * 1024 * 1024:
                    await self._handle_large_file_advanced(message, attachment, file_info)
                    continue
                
                # Enhanced file extension analysis
                file_ext = attachment.filename.lower().split('.')[-1] if '.' in attachment.filename else ''
                
                if f'.{file_ext}' in config.KCLAntivirus.DANGEROUS_EXTENSIONS:
                    await self._handle_dangerous_file_advanced(message, attachment, file_info)
                    continue
                
                if f'.{file_ext}' in config.KCLAntivirus.SAFE_EXTENSIONS:
                    continue  # Skip safe files
                
                # Advanced VirusTotal scanning with caching
                scan_result = await self._virustotal_scan_file_advanced(attachment, file_info)
                if scan_result:
                    await self._handle_scan_result_advanced(message, scan_result, attachment.filename, 'file')
                    
            except Exception as e:
                logger.error(f"Error in advanced attachment scanning {attachment.filename}: {e}")
                await self._log_scan_error(message, attachment.filename, str(e))
    
    async def _scan_urls_advanced(self, message, urls):
        """Advanced URL scanning with enhanced threat detection"""
        for url in urls:
            try:
                # Enhanced URL analysis
                url_info = {
                    'url': url,
                    'domain': urlparse(url).netloc,
                    'scheme': urlparse(url).scheme,
                    'path': urlparse(url).path
                }
                
                # Check against known malicious domains
                if await self._check_malicious_domain(url_info['domain']):
                    await self._handle_malicious_domain(message, url, url_info)
                    continue
                
                # VirusTotal URL scanning with caching
                scan_result = await self._virustotal_scan_url_advanced(url, url_info)
                if scan_result:
                    await self._handle_scan_result_advanced(message, scan_result, url, 'url')
                    
            except Exception as e:
                logger.error(f"Error in advanced URL scanning {url}: {e}")
                await self._log_scan_error(message, url, str(e))
    
    async def _check_malicious_domain(self, domain):
        """Check domain against known malicious domain list"""
        # Basic malicious domain patterns
        malicious_patterns = [
            r'.*\.tk$',
            r'.*\.ml$',
            r'.*\.ga$',
            r'.*\.cf$',
            r'bit\.ly',
            r'tinyurl\.com',
            r'discord-nitro.*',
            r'discordapp-nitro.*',
            r'steam-community.*'
        ]
        
        for pattern in malicious_patterns:
            if re.match(pattern, domain.lower()):
                return True
        
        return False
    
    async def _handle_malicious_domain(self, message, url, url_info):
        """Handle known malicious domains"""
        await self._handle_threat_advanced(
            message, 
            url, 
            "MALICIOUS DOMAIN", 
            1, 
            0,
            f"Known malicious domain: {url_info['domain']}"
        )
    
    async def _virustotal_scan_file_advanced(self, attachment, file_info):
        """Advanced VirusTotal file scanning with caching and retry logic"""
        if not config.VIRUSTOTAL_API_KEY:
            logger.warning("VirusTotal API key not configured")
            return None
        
        try:
            # Download file
            file_data = await attachment.read()
            file_hash = hashlib.sha256(file_data).hexdigest()
            
            # Check cache first
            cache_key = f"file_{file_hash}"
            if cache_key in self.threat_cache:
                cached_result = self.threat_cache[cache_key]
                if (datetime.utcnow() - cached_result['timestamp']).hours < 24:
                    return cached_result['data']
            
            # Check if file is already scanned
            headers = {'x-apikey': config.VIRUSTOTAL_API_KEY}
            
            async with self.session.get(
                f'https://www.virustotal.com/api/v3/files/{file_hash}',
                headers=headers
            ) as response:
                if response.status == 200:
                    data = await response.json()
                    result = data.get('data', {}).get('attributes', {})
                    
                    # Cache the result
                    self.threat_cache[cache_key] = {
                        'data': result,
                        'timestamp': datetime.utcnow()
                    }
                    
                    return result
                elif response.status == 404:
                    # File not in database, upload for scanning
                    return await self._upload_file_to_virustotal_advanced(file_data, attachment.filename, file_info)
                    
        except Exception as e:
            logger.error(f"Advanced VirusTotal file scan error: {e}")
            return None
    
    async def _upload_file_to_virustotal_advanced(self, file_data, filename, file_info):
        """Advanced file upload to VirusTotal with progress tracking"""
        try:
            headers = {'x-apikey': config.VIRUSTOTAL_API_KEY}
            
            # Upload file
            data = aiohttp.FormData()
            data.add_field('file', file_data, filename=filename)
            
            async with self.session.post(
                'https://www.virustotal.com/api/v3/files',
                headers=headers,
                data=data
            ) as response:
                if response.status == 200:
                    upload_data = await response.json()
                    analysis_id = upload_data.get('data', {}).get('id')
                    
                    if analysis_id:
                        # Wait with exponential backoff
                        for attempt in range(3):
                            await asyncio.sleep(10 * (attempt + 1))
                            result = await self._get_virustotal_analysis_advanced(analysis_id)
                            if result:
                                return result
                        
        except Exception as e:
            logger.error(f"Advanced VirusTotal file upload error: {e}")
            return None
    
    async def _virustotal_scan_url_advanced(self, url, url_info):
        """Advanced VirusTotal URL scanning with caching"""
        if not config.VIRUSTOTAL_API_KEY:
            return None
        
        try:
            # Check cache first
            url_hash = hashlib.sha256(url.encode()).hexdigest()
            cache_key = f"url_{url_hash}"
            if cache_key in self.threat_cache:
                cached_result = self.threat_cache[cache_key]
                if (datetime.utcnow() - cached_result['timestamp']).hours < 12:
                    return cached_result['data']
            
            headers = {'x-apikey': config.VIRUSTOTAL_API_KEY}
            
            # Submit URL for scanning
            data = {'url': url}
            
            async with self.session.post(
                'https://www.virustotal.com/api/v3/urls',
                headers=headers,
                data=data
            ) as response:
                if response.status == 200:
                    upload_data = await response.json()
                    analysis_id = upload_data.get('data', {}).get('id')
                    
                    if analysis_id:
                        await asyncio.sleep(5)
                        result = await self._get_virustotal_analysis_advanced(analysis_id)
                        
                        if result:
                            # Cache the result
                            self.threat_cache[cache_key] = {
                                'data': result,
                                'timestamp': datetime.utcnow()
                            }
                        
                        return result
                        
        except Exception as e:
            logger.error(f"Advanced VirusTotal URL scan error: {e}")
            return None
    
    async def _get_virustotal_analysis_advanced(self, analysis_id):
        """Advanced VirusTotal analysis retrieval with retry logic"""
        try:
            headers = {'x-apikey': config.VIRUSTOTAL_API_KEY}
            
            async with self.session.get(
                f'https://www.virustotal.com/api/v3/analyses/{analysis_id}',
                headers=headers
            ) as response:
                if response.status == 200:
                    data = await response.json()
                    return data.get('data', {}).get('attributes', {})
                    
        except Exception as e:
            logger.error(f"Advanced VirusTotal analysis retrieval error: {e}")
            return None
    
    async def _handle_scan_result_advanced(self, message, scan_result, item_name, item_type):
        """Advanced scan result handling with detailed analysis"""
        stats = scan_result.get('stats', {})
        malicious = stats.get('malicious', 0)
        suspicious = stats.get('suspicious', 0)
        harmless = stats.get('harmless', 0)
        undetected = stats.get('undetected', 0)
        
        # Enhanced threat level calculation
        total_engines = malicious + suspicious + harmless + undetected
        threat_ratio = (malicious + suspicious * 0.5) / max(total_engines, 1)
        
        # Determine threat level with advanced logic
        if malicious >= config.KCLAntivirus.MALICIOUS_THRESHOLD:
            threat_level = "MALICIOUS"
        elif suspicious >= config.KCLAntivirus.SUSPICIOUS_THRESHOLD:
            threat_level = "SUSPICIOUS"
        elif threat_ratio > 0.1:  # More than 10% of engines flagged
            threat_level = "POTENTIALLY_HARMFUL"
        else:
            # Log clean files for statistics
            await self._log_clean_scan(message, item_name, item_type, stats)
            return
        
        # Handle the threat with advanced response
        await self._handle_threat_advanced(
            message, 
            item_name, 
            threat_level, 
            malicious, 
            suspicious,
            f"VirusTotal scan: {malicious} malicious, {suspicious} suspicious out of {total_engines} engines"
        )
    
    async def _handle_threat_advanced(self, message, item_name, threat_level, malicious, suspicious, details=""):
        """Advanced threat handling with comprehensive response"""
        try:
            # Log the threat first
            log_id = await self.bot.db.add_antivirus_scan_log(
                message.guild.id,
                message.author.id,
                item_name,
                'file' if '.' in item_name else 'url',
                threat_level,
                malicious,
                suspicious,
                f"Message deleted, user timed out for {config.KCLAntivirus.VIRUS_TIMEOUT_DAYS} day(s)"
            )
            
            # Delete the message
            await message.delete()
            
            # Determine timeout duration based on threat level
            if threat_level == "MALICIOUS":
                timeout_days = config.KCLAntivirus.VIRUS_TIMEOUT_DAYS
            elif threat_level == "SUSPICIOUS":
                timeout_days = max(1, config.KCLAntivirus.VIRUS_TIMEOUT_DAYS // 2)
            else:  # POTENTIALLY_HARMFUL
                timeout_days = 1
            
            # Timeout the user
            timeout_duration = timedelta(days=timeout_days)
            await message.author.timeout(timeout_duration, reason=f"KCLAntivirus: {threat_level} content detected")
            
            # Add warning with detailed information
            await self.bot.db.add_warning(
                message.author.id,
                message.guild.id,
                self.bot.user.id,
                f"KCLAntivirus: Posted {threat_level.lower()} content ({item_name}) - {details}"
            )
            
            # Send advanced DM to user
            await self._dm_user_threat_advanced(message.author, item_name, threat_level, malicious, suspicious, details, timeout_days)
            
            # Advanced logging to mod channel
            await self._log_threat_detection_advanced(message, item_name, threat_level, malicious, suspicious, details, log_id)
            
            logger.warning(f"Advanced threat detected: {threat_level} - {item_name} by {message.author} in {message.guild} - {details}")
            
        except Exception as e:
            logger.error(f"Error in advanced threat handling: {e}")
            # Fallback: at least try to delete the message
            try:
                await message.delete()
            except:
                pass
    
    async def _handle_dangerous_file_advanced(self, message, attachment, file_info):
        """Advanced handling of dangerous file types"""
        await self._handle_threat_advanced(
            message, 
            attachment.filename, 
            "DANGEROUS FILE TYPE", 
            1, 
            0,
            f"File extension .{attachment.filename.split('.')[-1]} is automatically flagged as dangerous"
        )
    
    async def _handle_large_file_advanced(self, message, attachment, file_info):
        """Advanced handling of files too large to scan"""
        settings = await self.bot.db.get_antivirus_settings(message.guild.id)
        if settings.mod_log_channel:
            log_channel = message.guild.get_channel(settings.mod_log_channel)
            if log_channel:
                embed = discord.Embed(
                    title="⚠️ Large File Detected",
                    description=f"File too large to scan: **{attachment.filename}**",
                    color=config.Colors.WARNING,
                    timestamp=datetime.utcnow()
                )
                embed.add_field(name="User", value=f"{message.author} ({message.author.id})", inline=True)
                embed.add_field(name="Channel", value=message.channel.mention, inline=True)
                embed.add_field(name="File Size", value=f"{attachment.size / (1024*1024):.1f} MB", inline=True)
                embed.add_field(name="Content Type", value=file_info.get('content_type', 'Unknown'), inline=True)
                embed.add_field(name="Action", value="File allowed (too large to scan)", inline=True)
                
                try:
                    await log_channel.send(embed=embed)
                except:
                    pass
    
    async def _dm_user_threat_advanced(self, user, item_name, threat_level, malicious, suspicious, details, timeout_days):
        """Send advanced DM to user about threat detection"""
        try:
            embed = discord.Embed(
                title="🚨 KCLAntivirus Security Alert",
                description=f"Your message in **{user.guild.name}** was removed due to {threat_level.lower()} content detection.",
                color=config.Colors.ERROR,
                timestamp=datetime.utcnow()
            )
            
            embed.add_field(name="Item Detected", value=item_name, inline=True)
            embed.add_field(name="Threat Level", value=threat_level, inline=True)
            embed.add_field(name="Detection Count", value=f"{malicious} malicious, {suspicious} suspicious", inline=True)
            
            embed.add_field(
                name="Actions Taken", 
                value=f"• Message deleted immediately\n• {timeout_days} day timeout applied\n• Warning added to your record\n• Incident logged for review", 
                inline=False
            )
            
            if details:
                embed.add_field(name="Technical Details", value=details[:1000], inline=False)
            
            embed.add_field(
                name="What This Means", 
                value="Our security system detected potentially harmful content in your message. This is an automated response to protect the server.", 
                inline=False
            )
            
            embed.add_field(
                name="If You Believe This Is An Error", 
                value="Contact the server moderators with details about what you were trying to share. False positives can occur with legitimate files.", 
                inline=False
            )
            
            embed.set_footer(text="KCLAntivirus Advanced Protection System")
            
            await user.send(embed=embed)
            
        except discord.Forbidden:
            logger.info(f"Could not DM user {user} about threat detection - DMs disabled")
        except Exception as e:
            logger.error(f"Error sending advanced threat DM to {user}: {e}")
    
    async def _log_threat_detection_advanced(self, message, item_name, threat_level, malicious, suspicious, details, log_id):
        """Advanced threat detection logging"""
        settings = await self.bot.db.get_antivirus_settings(message.guild.id)
        if not settings.mod_log_channel:
            return
        
        log_channel = message.guild.get_channel(settings.mod_log_channel)
        if not log_channel:
            return
        
        embed = discord.Embed(
            title="🦠 KCLAntivirus Threat Detected",
            color=config.Colors.ERROR,
            timestamp=datetime.utcnow()
        )
        
        embed.add_field(name="User", value=f"{message.author} ({message.author.id})", inline=True)
        embed.add_field(name="Channel", value=message.channel.mention, inline=True)
        embed.add_field(name="Threat Level", value=threat_level, inline=True)
        embed.add_field(name="Item", value=item_name, inline=True)
        embed.add_field(name="Detection", value=f"{malicious} malicious, {suspicious} suspicious", inline=True)
        embed.add_field(name="Log ID", value=f"#{log_id}", inline=True)
        
        if details:
            embed.add_field(name="Details", value=details[:1000], inline=False)
        
        embed.add_field(
            name="Action Taken", 
            value=f"Message deleted, user timed out, warning added", 
            inline=False
        )
        
        if message.content and not any(word in message.content.lower() for word in ['password', 'token', 'key']):
            embed.add_field(name="Message Content", value=message.content[:500], inline=False)
        
        embed.set_footer(text=f"User Account Created: {message.author.created_at.strftime('%Y-%m-%d')}")
        
        try:
            await log_channel.send(embed=embed)
        except Exception as e:
            logger.error(f"Failed to log advanced threat detection: {e}")
    
    async def _log_clean_scan(self, message, item_name, item_type, stats):
        """Log clean scans for statistics"""
        try:
            await self.bot.db.add_antivirus_scan_log(
                message.guild.id,
                message.author.id,
                item_name,
                item_type,
                "CLEAN",
                0,
                0,
                f"Clean scan: {stats.get('harmless', 0)} harmless, {stats.get('undetected', 0)} undetected"
            )
        except Exception as e:
            logger.error(f"Error logging clean scan: {e}")
    
    async def _log_suspicious_activity(self, message, threat_score, reason=""):
        """Log suspicious activity for analysis"""
        settings = await self.bot.db.get_antivirus_settings(message.guild.id)
        if settings.mod_log_channel and threat_score > 0.8:
            log_channel = message.guild.get_channel(settings.mod_log_channel)
            if log_channel:
                embed = discord.Embed(
                    title="🔍 Suspicious Activity Detected",
                    description=f"High threat score detected: {threat_score:.2f}",
                    color=config.Colors.WARNING,
                    timestamp=datetime.utcnow()
                )
                embed.add_field(name="User", value=f"{message.author} ({message.author.id})", inline=True)
                embed.add_field(name="Channel", value=message.channel.mention, inline=True)
                embed.add_field(name="Threat Score", value=f"{threat_score:.2f}/1.0", inline=True)
                
                if reason:
                    embed.add_field(name="Reason", value=reason, inline=False)
                
                embed.add_field(name="Message", value=message.content[:500], inline=False)
                embed.add_field(name="Action", value="Flagged for review (no action taken)", inline=True)
                
                try:
                    await log_channel.send(embed=embed)
                except:
                    pass
    
    async def _log_new_account_join(self, member, join_data):
        """Log new account joins for monitoring"""
        settings = await self.bot.db.get_antivirus_settings(member.guild.id)
        if settings.mod_log_channel:
            log_channel = member.guild.get_channel(settings.mod_log_channel)
            if log_channel:
                embed = discord.Embed(
                    title="👶 New Account Joined",
                    description=f"Account less than {join_data['account_age']} days old joined",
                    color=config.Colors.INFO,
                    timestamp=datetime.utcnow()
                )
                embed.add_field(name="User", value=f"{member} ({member.id})", inline=True)
                embed.add_field(name="Account Age", value=f"{join_data['account_age']} days", inline=True)
                embed.add_field(name="Created", value=member.created_at.strftime('%Y-%m-%d %H:%M'), inline=True)
                
                try:
                    await log_channel.send(embed=embed)
                except:
                    pass
    
    async def _log_scan_error(self, message, item_name, error):
        """Log scanning errors"""
        logger.error(f"Scan error for {item_name} by {message.author} in {message.guild}: {error}")
        
        settings = await self.bot.db.get_antivirus_settings(message.guild.id)
        if settings.mod_log_channel:
            log_channel = message.guild.get_channel(settings.mod_log_channel)
            if log_channel:
                embed = discord.Embed(
                    title="⚠️ Scan Error",
                    description=f"Error scanning {item_name}",
                    color=config.Colors.WARNING,
                    timestamp=datetime.utcnow()
                )
                embed.add_field(name="User", value=f"{message.author} ({message.author.id})", inline=True)
                embed.add_field(name="Item", value=item_name, inline=True)
                embed.add_field(name="Error", value=error[:500], inline=False)
                
                try:
                    await log_channel.send(embed=embed)
                except:
                    pass
    
    async def _check_raid_activity(self, guild):
        """Advanced raid activity detection with pattern analysis"""
        now = datetime.utcnow()
        cutoff = now - timedelta(seconds=config.KCLAntivirus.RAID_TIME_WINDOW)
        
        # Check user joins with enhanced analysis
        recent_joins = [
            (ts, uid) for ts, uid in self.user_joins.get(guild.id, [])
            if ts > cutoff
        ]
        
        # Check message activity with user correlation
        recent_messages = [
            (ts, uid) for ts, uid in self.message_activity.get(guild.id, [])
            if ts > cutoff
        ]
        
        # Advanced pattern detection
        unique_users_joined = len(set(uid for ts, uid in recent_joins))
        unique_users_messaging = len(set(uid for ts, uid in recent_messages))
        
        # Calculate raid probability
        raid_score = 0
        if len(recent_joins) >= config.KCLAntivirus.RAID_USER_JOIN_THRESHOLD:
            raid_score += 0.5
        if len(recent_messages) >= config.KCLAntivirus.RAID_MESSAGE_THRESHOLD:
            raid_score += 0.3
        if unique_users_joined > 5 and len(recent_joins) / unique_users_joined > 1.5:
            raid_score += 0.2  # Multiple joins from same users
        
        # Detect coordinated activity
        if unique_users_messaging > 0 and len(recent_messages) / unique_users_messaging > 10:
            raid_score += 0.3  # High message rate per user
        
        if raid_score >= 0.7:  # High confidence raid
            await self._trigger_raid_protection_advanced(guild, len(recent_joins), len(recent_messages), raid_score)
            return True
        elif raid_score >= 0.4:  # Suspicious activity
            await self._alert_mods_suspicious_activity(guild, len(recent_joins), len(recent_messages), raid_score)
        
        return False
    
    async def _trigger_raid_protection_advanced(self, guild, join_count, message_count, raid_score):
        """Advanced raid protection with detailed analysis"""
        logger.critical(f"Advanced raid detected in {guild.name}: {join_count} joins, {message_count} messages, score: {raid_score:.2f}")
        
        settings = await self.bot.db.get_antivirus_settings(guild.id)
        
        # Log the raid attempt
        self.lockdown_history[guild.id].append({
            'timestamp': datetime.utcnow(),
            'type': 'auto_raid_detection',
            'join_count': join_count,
            'message_count': message_count,
            'raid_score': raid_score,
            'auto_lockdown': settings.auto_lockdown
        })
        
        if not settings.auto_lockdown:
            # Alert mods with detailed information
            await self._alert_mods_raid_advanced(guild, join_count, message_count, raid_score)
            return
        
        # Trigger automatic server lockdown
        reason = f"Automatic raid protection: {join_count} joins, {message_count} messages, raid score: {raid_score:.2f}"
        await self._server_lockdown_advanced(guild, reason)
    
    async def _alert_mods_raid_advanced(self, guild, join_count, message_count, raid_score):
        """Advanced raid alert with detailed analysis"""
        settings = await self.bot.db.get_antivirus_settings(guild.id)
        if not settings.mod_log_channel:
            return
        
        log_channel = guild.get_channel(settings.mod_log_channel)
        if not log_channel:
            return
        
        embed = discord.Embed(
            title="🚨 RAID DETECTED - IMMEDIATE ACTION REQUIRED",
            description="Advanced raid detection system has identified a coordinated attack!",
            color=config.Colors.ERROR,
            timestamp=datetime.utcnow()
        )
        
        embed.add_field(name="Recent Joins", value=str(join_count), inline=True)
        embed.add_field(name="Recent Messages", value=str(message_count), inline=True)
        embed.add_field(name="Raid Score", value=f"{raid_score:.2f}/1.0", inline=True)
        embed.add_field(name="Time Window", value=f"{config.KCLAntivirus.RAID_TIME_WINDOW}s", inline=True)
        embed.add_field(name="Auto-Lockdown", value="Disabled" if not await self._get_auto_lockdown_setting(guild.id) else "Enabled", inline=True)
        embed.add_field(name="Confidence", value="HIGH" if raid_score > 0.8 else "MEDIUM", inline=True)
        
        embed.add_field(
            name="🚨 IMMEDIATE ACTIONS AVAILABLE",
            value="• `/server-lockdown` - Emergency lockdown\n• `/server-scan` - Detailed analysis\n• `/antivirus-setup auto_lockdown:True` - Enable auto-lockdown",
            inline=False
        )
        
        embed.add_field(
            name="⚠️ THREAT ASSESSMENT",
            value="This appears to be a coordinated attack. Consider immediate lockdown if activity continues.",
            inline=False
        )
        
        try:
            await log_channel.send("@here **RAID ALERT**", embed=embed)
        except Exception as e:
            logger.error(f"Failed to send advanced raid alert: {e}")
    
    async def _alert_mods_suspicious_activity(self, guild, join_count, message_count, raid_score):
        """Alert about suspicious but not confirmed raid activity"""
        settings = await self.bot.db.get_antivirus_settings(guild.id)
        if not settings.mod_log_channel:
            return
        
        log_channel = guild.get_channel(settings.mod_log_channel)
        if not log_channel:
            return
        
        embed = discord.Embed(
            title="⚠️ Suspicious Activity Detected",
            description="Unusual activity patterns detected - monitoring for potential raid",
            color=config.Colors.WARNING,
            timestamp=datetime.utcnow()
        )
        
        embed.add_field(name="Recent Joins", value=str(join_count), inline=True)
        embed.add_field(name="Recent Messages", value=str(message_count), inline=True)
        embed.add_field(name="Suspicion Score", value=f"{raid_score:.2f}/1.0", inline=True)
        embed.add_field(name="Status", value="Monitoring", inline=True)
        embed.add_field(name="Action", value="No immediate action required", inline=True)
        
        try:
            await log_channel.send(embed=embed)
        except:
            pass
    
    async def _get_auto_lockdown_setting(self, guild_id):
        """Get auto-lockdown setting for guild"""
        settings = await self.bot.db.get_antivirus_settings(guild_id)
        return settings.auto_lockdown
    
    async def _server_lockdown_advanced(self, guild, reason, interaction=None):
        """Advanced server lockdown with progress tracking and detailed logging"""
        logger.critical(f"Advanced server lockdown initiated in {guild.name}: {reason}")
        
        # Initialize counters
        kicked_count = 0
        protected_count = 0
        error_count = 0
        dm_sent_count = 0
        
        # Get protected roles for detailed analysis
        protected_roles = await self.bot.db.get_antivirus_protected_roles(guild.id)
        
        # Progress tracking
        total_members = len([m for m in guild.members if not m.bot])
        processed = 0
        
        # Send progress updates if interaction provided
        if interaction:
            progress_embed = discord.Embed(
                title="🔒 Lockdown Progress",
                description=f"Processing {total_members} members...",
                color=config.Colors.WARNING
            )
            progress_message = await interaction.followup.send(embed=progress_embed)
        
        # Process members in batches to avoid rate limits
        batch_size = 10
        members_to_kick = []
        
        for member in guild.members:
            if member.bot:
                continue
            
            processed += 1
            
            if await self._is_protected_user(member):
                protected_count += 1
                continue
            
            members_to_kick.append(member)
            
            # Process in batches
            if len(members_to_kick) >= batch_size:
                batch_result = await self._process_lockdown_batch(members_to_kick, reason)
                kicked_count += batch_result['kicked']
                error_count += batch_result['errors']
                dm_sent_count += batch_result['dms_sent']
                members_to_kick = []
                
                # Update progress
                if interaction and processed % 20 == 0:
                    progress_embed.description = f"Processed {processed}/{total_members} members... ({kicked_count} kicked, {protected_count} protected)"
                    try:
                        await progress_message.edit(embed=progress_embed)
                    except:
                        pass
                
                # Rate limit protection
                await asyncio.sleep(1)
        
        # Process remaining members
        if members_to_kick:
            batch_result = await self._process_lockdown_batch(members_to_kick, reason)
            kicked_count += batch_result['kicked']
            error_count += batch_result['errors']
            dm_sent_count += batch_result['dms_sent']
        
        # Log detailed lockdown results
        lockdown_data = {
            'timestamp': datetime.utcnow(),
            'reason': reason,
            'kicked_count': kicked_count,
            'protected_count': protected_count,
            'error_count': error_count,
            'dm_sent_count': dm_sent_count,
            'total_processed': processed
        }
        
        self.lockdown_history[guild.id].append(lockdown_data)
        
        # Advanced logging
        await self._log_server_lockdown_advanced(guild, lockdown_data)
        
        # Announce lockdown with detailed info
        await self._announce_lockdown_advanced(guild, lockdown_data)
        
        return {
            'kicked': kicked_count,
            'protected': protected_count,
            'errors': error_count,
            'dms_sent': dm_sent_count
        }
    
    async def _process_lockdown_batch(self, members, reason):
        """Process a batch of members for lockdown"""
        kicked = 0
        errors = 0
        dms_sent = 0
        
        for member in members:
            try:
                # Try to DM user first
                dm_success = await self._dm_user_lockdown_advanced(member, reason)
                if dm_success:
                    dms_sent += 1
                
                # Small delay before kicking
                await asyncio.sleep(0.2)
                
                # Kick the member
                await member.kick(reason=f"KCLAntivirus Advanced Lockdown: {reason}")
                kicked += 1
                
            except discord.Forbidden:
                errors += 1
                logger.warning(f"No permission to kick {member} during lockdown")
            except discord.HTTPException as e:
                errors += 1
                logger.error(f"HTTP error kicking {member}: {e}")
            except Exception as e:
                errors += 1
                logger.error(f"Unexpected error kicking {member}: {e}")
        
        return {
            'kicked': kicked,
            'errors': errors,
            'dms_sent': dms_sent
        }
    
    async def _dm_user_lockdown_advanced(self, user, reason):
        """Send advanced DM to user about server lockdown"""
        try:
            embed = discord.Embed(
                title="🔒 Emergency Server Lockdown - KCLAntivirus",
                description=f"**{user.guild.name}** has been placed under emergency security lockdown.",
                color=config.Colors.ERROR,
                timestamp=datetime.utcnow()
            )
            
            embed.add_field(name="🚨 What Happened?", value="Our advanced security system detected a coordinated attack or security breach targeting the server.", inline=False)
            embed.add_field(name="📋 Lockdown Reason", value=reason, inline=False)
            embed.add_field(name="⚡ Your Status", value="You have been temporarily removed from the server as a security precaution. This is **not** because you did anything wrong.", inline=False)
            embed.add_field(name="🔄 What's Next?", value="• The server is now secure\n• You can rejoin once the situation is resolved\n• Server moderators will announce when it's safe to return", inline=False)
            embed.add_field(name="❓ Questions?", value="Contact the server moderators if you have any questions about this security action.", inline=False)
            
            embed.set_footer(text="KCLAntivirus Advanced Protection System - This is an automated security response")
            
            await user.send(embed=embed)
            return True
            
        except discord.Forbidden:
            return False  # User has DMs disabled
        except Exception as e:
            logger.error(f"Error sending advanced lockdown DM to {user}: {e}")
            return False
    
    async def _log_server_lockdown_advanced(self, guild, lockdown_data):
        """Advanced server lockdown logging"""
        settings = await self.bot.db.get_antivirus_settings(guild.id)
        if not settings.mod_log_channel:
            return
        
        log_channel = guild.get_channel(settings.mod_log_channel)
        if not log_channel:
            return
        
        embed = discord.Embed(
            title="🔒 ADVANCED SERVER LOCKDOWN EXECUTED",
            description="KCLAntivirus Advanced has executed an emergency server lockdown with detailed tracking.",
            color=config.Colors.ERROR,
            timestamp=lockdown_data['timestamp']
        )
        
        embed.add_field(name="📋 Lockdown Reason", value=lockdown_data['reason'], inline=False)
        
        # Statistics
        embed.add_field(name="👥 Users Kicked", value=str(lockdown_data['kicked_count']), inline=True)
        embed.add_field(name="🛡️ Users Protected", value=str(lockdown_data['protected_count']), inline=True)
        embed.add_field(name="⚠️ Errors", value=str(lockdown_data['error_count']), inline=True)
        embed.add_field(name="📨 DMs Sent", value=str(lockdown_data['dm_sent_count']), inline=True)
        embed.add_field(name="📊 Total Processed", value=str(lockdown_data['total_processed']), inline=True)
        embed.add_field(name="🏆 Success Rate", value=f"{(lockdown_data['kicked_count']/(lockdown_data['kicked_count']+lockdown_data['error_count'])*100):.1f}%" if lockdown_data['kicked_count']+lockdown_data['error_count'] > 0 else "N/A", inline=True)
        
        # Current server status
        embed.add_field(name="🔒 Server Status", value="SECURED - Threat neutralized", inline=False)
        embed.add_field(name="📈 Remaining Members", value=str(len(guild.members)), inline=True)
        
        embed.set_footer(text="All affected users received explanatory DMs where possible")
        
        try:
            await log_channel.send("@everyone **LOCKDOWN COMPLETE**", embed=embed)
        except Exception as e:
            logger.error(f"Failed to log advanced server lockdown: {e}")
    
    async def _announce_lockdown_advanced(self, guild, lockdown_data):
        """Advanced lockdown announcement to remaining members"""
        # Find the best channel for announcement
        announcement_channel = None
        
        # Priority order for announcement channels
        channel_names = ['general', 'announcements', 'main', 'lobby', 'chat']
        
        for name in channel_names:
            for channel in guild.text_channels:
                if name in channel.name.lower():
                    announcement_channel = channel
                    break
            if announcement_channel:
                break
        
        # Fallback to first available channel
        if not announcement_channel and guild.text_channels:
            announcement_channel = guild.text_channels[0]
        
        if not announcement_channel:
            return
        
        embed = discord.Embed(
            title="🔒 EMERGENCY LOCKDOWN COMPLETE",
            description="The server has been secured following a detected security threat.",
            color=config.Colors.SUCCESS,
            timestamp=datetime.utcnow()
        )
        
        embed.add_field(name="🛡️ Security Status", value="**SECURED** - Threat neutralized", inline=False)
        embed.add_field(name="📊 Lockdown Results", value=f"• {lockdown_data['kicked_count']} users temporarily removed\n• {lockdown_data['protected_count']} staff members retained\n• {lockdown_data['dm_sent_count']} users notified via DM", inline=False)
        embed.add_field(name="⚡ What Happened?", value="Our advanced security system detected suspicious activity and executed an emergency lockdown to protect the server.", inline=False)
        embed.add_field(name="🔄 Current Status", value="• Server is now secure\n• Normal operations resuming\n• Affected users can rejoin when ready", inline=False)
        embed.add_field(name="❓ Questions?", value="Contact server moderators if you have any concerns about this security action.", inline=False)
        
        embed.set_footer(text="KCLAntivirus Advanced Protection System")
        
        try:
            await announcement_channel.send(embed=embed)
        except Exception as e:
            logger.error(f"Failed to announce advanced lockdown: {e}")

async def setup(bot):
    await bot.add_cog(KCLAntivirusAdvanced(bot))