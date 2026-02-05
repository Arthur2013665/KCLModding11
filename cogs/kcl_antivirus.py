"""
KCLAntivirus - Advanced server protection system
Scans files and links using VirusTotal API, detects raids, and provides server lockdown capabilities
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
from urllib.parse import urlparse

from utils.embeds import success_embed, warning_embed, error_embed
from utils.checks import is_moderator
import config

logger = logging.getLogger('discord_bot.kcl_antivirus')

class KCLAntivirus(commands.Cog):
    """KCLAntivirus - Advanced server protection system"""
    
    def __init__(self, bot):
        self.bot = bot
        self.session = None
        
        # Tracking dictionaries
        self.user_joins = defaultdict(list)  # guild_id: [(timestamp, user_id), ...]
        self.message_activity = defaultdict(list)  # guild_id: [(timestamp, user_id), ...]
        self.scan_cooldowns = defaultdict(dict)  # guild_id: {user_id: timestamp}
        self.server_scan_cooldowns = {}  # guild_id: timestamp
        
        # URL regex pattern
        self.url_pattern = re.compile(
            r'http[s]?://(?:[a-zA-Z]|[0-9]|[$-_@.&+]|[!*\\(\\),]|(?:%[0-9a-fA-F][0-9a-fA-F]))+'
        )
        
        # Start background tasks
        self.cleanup_tracking.start()
    
    async def cog_load(self):
        """Initialize HTTP session when cog loads"""
        self.session = aiohttp.ClientSession()
        logger.info("KCLAntivirus system initialized")
    
    async def cog_unload(self):
        """Cleanup when cog unloads"""
        if self.session:
            await self.session.close()
        self.cleanup_tracking.cancel()
        logger.info("KCLAntivirus system shutdown")
    
    @tasks.loop(minutes=30)
    async def cleanup_tracking(self):
        """Clean up old tracking data"""
        cutoff = datetime.utcnow() - timedelta(hours=1)
        
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
    
    @commands.Cog.listener()
    async def on_message(self, message: discord.Message):
        """Monitor messages for files and links"""
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
        
        # Check for raid patterns
        if await self._check_raid_activity(message.guild):
            return
        
        # Scan attachments
        if message.attachments:
            await self._scan_attachments(message)
        
        # Scan URLs in message content
        urls = self.url_pattern.findall(message.content)
        if urls:
            await self._scan_urls(message, urls)
    
    @commands.Cog.listener()
    async def on_member_join(self, member: discord.Member):
        """Monitor member joins for raid detection"""
        if member.bot:
            return
        
        settings = await self.bot.db.get_antivirus_settings(member.guild.id)
        if not settings.enabled:
            return
        
        # Track user joins
        now = datetime.utcnow()
        self.user_joins[member.guild.id].append((now, member.id))
        
        # Check for raid patterns
        await self._check_raid_activity(member.guild)
    
    async def _is_protected_user(self, user: discord.Member) -> bool:
        """Check if user is protected from antivirus actions"""
        # Bot owner is always protected
        if user.id == self.bot.owner_id:
            return True
        
        # Check permissions
        if user.guild_permissions.administrator:
            return True
        
        if user.guild_permissions.manage_guild:
            return True
        
        if user.guild_permissions.manage_messages:
            return True
        
        # Check protected roles
        protected_roles = await self.bot.db.get_antivirus_protected_roles(user.guild.id)
        user_role_ids = [role.id for role in user.roles]
        
        return any(role_id in user_role_ids for role_id in protected_roles)
    
    async def _scan_attachments(self, message: discord.Message):
        """Scan message attachments for viruses"""
        for attachment in message.attachments:
            try:
                # Check file size
                if attachment.size > config.KCLAntivirus.MAX_FILE_SIZE_MB * 1024 * 1024:
                    await self._handle_large_file(message, attachment)
                    continue
                
                # Check file extension
                file_ext = attachment.filename.lower().split('.')[-1] if '.' in attachment.filename else ''
                
                if f'.{file_ext}' in config.KCLAntivirus.DANGEROUS_EXTENSIONS:
                    await self._handle_dangerous_file(message, attachment)
                    continue
                
                if f'.{file_ext}' in config.KCLAntivirus.SAFE_EXTENSIONS:
                    continue  # Skip safe files
                
                # Scan with VirusTotal
                scan_result = await self._virustotal_scan_file(attachment)
                if scan_result:
                    await self._handle_scan_result(message, scan_result, attachment.filename)
                    
            except Exception as e:
                logger.error(f"Error scanning attachment {attachment.filename}: {e}")
    
    async def _scan_urls(self, message: discord.Message, urls: List[str]):
        """Scan URLs for malicious content"""
        for url in urls:
            try:
                scan_result = await self._virustotal_scan_url(url)
                if scan_result:
                    await self._handle_scan_result(message, scan_result, url)
            except Exception as e:
                logger.error(f"Error scanning URL {url}: {e}")
    
    async def _virustotal_scan_file(self, attachment: discord.Attachment) -> Optional[Dict[str, Any]]:
        """Scan file using VirusTotal API"""
        if not config.VIRUSTOTAL_API_KEY:
            logger.warning("VirusTotal API key not configured")
            return None
        
        try:
            # Download file
            file_data = await attachment.read()
            file_hash = hashlib.sha256(file_data).hexdigest()
            
            # Check if file is already scanned
            headers = {'x-apikey': config.VIRUSTOTAL_API_KEY}
            
            async with self.session.get(
                f'https://www.virustotal.com/api/v3/files/{file_hash}',
                headers=headers
            ) as response:
                if response.status == 200:
                    data = await response.json()
                    return data.get('data', {}).get('attributes', {})
                elif response.status == 404:
                    # File not in database, upload for scanning
                    return await self._upload_file_to_virustotal(file_data, attachment.filename)
                    
        except Exception as e:
            logger.error(f"VirusTotal file scan error: {e}")
            return None
    
    async def _upload_file_to_virustotal(self, file_data: bytes, filename: str) -> Optional[Dict[str, Any]]:
        """Upload file to VirusTotal for scanning"""
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
                        # Wait a bit and get results
                        await asyncio.sleep(10)
                        return await self._get_virustotal_analysis(analysis_id)
                        
        except Exception as e:
            logger.error(f"VirusTotal file upload error: {e}")
            return None
    
    async def _virustotal_scan_url(self, url: str) -> Optional[Dict[str, Any]]:
        """Scan URL using VirusTotal API"""
        if not config.VIRUSTOTAL_API_KEY:
            return None
        
        try:
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
                        return await self._get_virustotal_analysis(analysis_id)
                        
        except Exception as e:
            logger.error(f"VirusTotal URL scan error: {e}")
            return None
    
    async def _get_virustotal_analysis(self, analysis_id: str) -> Optional[Dict[str, Any]]:
        """Get VirusTotal analysis results"""
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
            logger.error(f"VirusTotal analysis retrieval error: {e}")
            return None
    
    async def _handle_scan_result(self, message: discord.Message, scan_result: Dict[str, Any], item_name: str):
        """Handle virus scan results"""
        stats = scan_result.get('stats', {})
        malicious = stats.get('malicious', 0)
        suspicious = stats.get('suspicious', 0)
        
        # Check thresholds
        is_malicious = malicious >= config.KCLAntivirus.MALICIOUS_THRESHOLD
        is_suspicious = suspicious >= config.KCLAntivirus.SUSPICIOUS_THRESHOLD
        
        if is_malicious or is_suspicious:
            threat_level = "MALICIOUS" if is_malicious else "SUSPICIOUS"
            await self._handle_threat(message, item_name, threat_level, malicious, suspicious)
    
    async def _handle_threat(self, message: discord.Message, item_name: str, threat_level: str, malicious: int, suspicious: int):
        """Handle detected threats"""
        try:
            # Delete the message
            await message.delete()
            
            # Timeout the user
            timeout_duration = timedelta(days=config.KCLAntivirus.VIRUS_TIMEOUT_DAYS)
            await message.author.timeout(timeout_duration, reason=f"KCLAntivirus: {threat_level} content detected")
            
            # Add warning
            await self.bot.db.add_warning(
                message.author.id,
                message.guild.id,
                self.bot.user.id,
                f"KCLAntivirus: Posted {threat_level.lower()} content ({item_name})"
            )
            
            # DM the user
            await self._dm_user_threat(message.author, item_name, threat_level, malicious, suspicious)
            
            # Log to mod channel
            await self._log_threat_detection(message, item_name, threat_level, malicious, suspicious)
            
            logger.warning(f"Threat detected: {threat_level} - {item_name} by {message.author} in {message.guild}")
            
        except Exception as e:
            logger.error(f"Error handling threat: {e}")
    
    async def _handle_dangerous_file(self, message: discord.Message, attachment: discord.Attachment):
        """Handle files with dangerous extensions"""
        await self._handle_threat(
            message, 
            attachment.filename, 
            "DANGEROUS FILE TYPE", 
            1, 
            0
        )
    
    async def _handle_large_file(self, message: discord.Message, attachment: discord.Attachment):
        """Handle files too large to scan"""
        # Just log for now, don't delete
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
                
                try:
                    await log_channel.send(embed=embed)
                except:
                    pass
    
    async def _dm_user_threat(self, user: discord.Member, item_name: str, threat_level: str, malicious: int, suspicious: int):
        """Send DM to user about threat detection"""
        try:
            embed = discord.Embed(
                title="🚨 KCLAntivirus Alert",
                description=f"Your message in **{user.guild.name}** was removed due to {threat_level.lower()} content detection.",
                color=config.Colors.ERROR,
                timestamp=datetime.utcnow()
            )
            
            embed.add_field(name="Item", value=item_name, inline=True)
            embed.add_field(name="Threat Level", value=threat_level, inline=True)
            embed.add_field(name="Detection Count", value=f"{malicious} malicious, {suspicious} suspicious", inline=True)
            embed.add_field(name="Action Taken", value=f"• Message deleted\n• {config.KCLAntivirus.VIRUS_TIMEOUT_DAYS} day timeout\n• Warning added", inline=False)
            
            embed.set_footer(text="If you believe this is a false positive, contact server moderators")
            
            await user.send(embed=embed)
            
        except discord.Forbidden:
            logger.info(f"Could not DM user {user} about threat detection")
    
    async def _log_threat_detection(self, message: discord.Message, item_name: str, threat_level: str, malicious: int, suspicious: int):
        """Log threat detection to mod channel"""
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
        embed.add_field(name="Action", value=f"Message deleted, user timed out for {config.KCLAntivirus.VIRUS_TIMEOUT_DAYS} day(s)", inline=True)
        
        if message.content:
            embed.add_field(name="Message Content", value=message.content[:1000], inline=False)
        
        try:
            await log_channel.send(embed=embed)
        except Exception as e:
            logger.error(f"Failed to log threat detection: {e}")
    
    async def _check_raid_activity(self, guild: discord.Guild) -> bool:
        """Check for raid activity patterns"""
        now = datetime.utcnow()
        cutoff = now - timedelta(seconds=config.KCLAntivirus.RAID_TIME_WINDOW)
        
        # Check user joins
        recent_joins = [
            (ts, uid) for ts, uid in self.user_joins.get(guild.id, [])
            if ts > cutoff
        ]
        
        # Check message activity
        recent_messages = [
            (ts, uid) for ts, uid in self.message_activity.get(guild.id, [])
            if ts > cutoff
        ]
        
        # Detect raid patterns
        if (len(recent_joins) >= config.KCLAntivirus.RAID_USER_JOIN_THRESHOLD or
            len(recent_messages) >= config.KCLAntivirus.RAID_MESSAGE_THRESHOLD):
            
            await self._trigger_raid_protection(guild, len(recent_joins), len(recent_messages))
            return True
        
        return False
    
    async def _trigger_raid_protection(self, guild: discord.Guild, join_count: int, message_count: int):
        """Trigger raid protection measures"""
        logger.warning(f"Raid detected in {guild.name}: {join_count} joins, {message_count} messages")
        
        settings = await self.bot.db.get_antivirus_settings(guild.id)
        if not settings.auto_lockdown:
            # Just alert mods
            await self._alert_mods_raid(guild, join_count, message_count)
            return
        
        # Trigger server lockdown
        await self._server_lockdown(guild, f"Automatic raid protection: {join_count} joins, {message_count} messages in {config.KCLAntivirus.RAID_TIME_WINDOW}s")
    
    async def _alert_mods_raid(self, guild: discord.Guild, join_count: int, message_count: int):
        """Alert moderators about potential raid"""
        settings = await self.bot.db.get_antivirus_settings(guild.id)
        if not settings.mod_log_channel:
            return
        
        log_channel = guild.get_channel(settings.mod_log_channel)
        if not log_channel:
            return
        
        embed = discord.Embed(
            title="🚨 POTENTIAL RAID DETECTED",
            description="Suspicious activity patterns detected on the server!",
            color=config.Colors.ERROR,
            timestamp=datetime.utcnow()
        )
        
        embed.add_field(name="Recent Joins", value=str(join_count), inline=True)
        embed.add_field(name="Recent Messages", value=str(message_count), inline=True)
        embed.add_field(name="Time Window", value=f"{config.KCLAntivirus.RAID_TIME_WINDOW}s", inline=True)
        embed.add_field(name="Recommended Action", value="Consider using `/antivirus server-lockdown` if this is a raid", inline=False)
        
        try:
            await log_channel.send("@here", embed=embed)
        except Exception as e:
            logger.error(f"Failed to alert mods about raid: {e}")

async def setup(bot):
    await bot.add_cog(KCLAntivirus(bot))
    async def _server_lockdown(self, guild: discord.Guild, reason: str):
        """Perform server lockdown - kick non-protected users"""
        logger.critical(f"Server lockdown initiated in {guild.name}: {reason}")
        
        # Get protected roles
        protected_roles = await self.bot.db.get_antivirus_protected_roles(guild.id)
        kicked_count = 0
        protected_count = 0
        
        # Kick non-protected members
        for member in guild.members:
            if member.bot:
                continue
            
            if await self._is_protected_user(member):
                protected_count += 1
                continue
            
            try:
                # DM user before kicking
                await self._dm_user_lockdown(member, reason)
                await asyncio.sleep(0.5)  # Brief delay
                
                await member.kick(reason=f"KCLAntivirus Server Lockdown: {reason}")
                kicked_count += 1
                
            except Exception as e:
                logger.error(f"Failed to kick {member}: {e}")
        
        # Log lockdown
        await self._log_server_lockdown(guild, reason, kicked_count, protected_count)
        
        # Alert remaining members
        await self._announce_lockdown(guild, reason, kicked_count)
    
    async def _dm_user_lockdown(self, user: discord.Member, reason: str):
        """DM user about server lockdown"""
        try:
            embed = discord.Embed(
                title="🔒 Server Lockdown - KCLAntivirus",
                description=f"**{user.guild.name}** has been placed under emergency lockdown.",
                color=config.Colors.ERROR,
                timestamp=datetime.utcnow()
            )
            
            embed.add_field(name="Reason", value=reason, inline=False)
            embed.add_field(name="What happened?", value="The server detected suspicious activity that may indicate a raid or security breach.", inline=False)
            embed.add_field(name="What now?", value="You have been temporarily removed from the server for security. You can rejoin once the situation is resolved.", inline=False)
            embed.add_field(name="Not your fault", value="This is an automated security measure. You did nothing wrong.", inline=False)
            
            embed.set_footer(text="Contact server moderators if you have questions")
            
            await user.send(embed=embed)
            
        except discord.Forbidden:
            pass  # User has DMs disabled
    
    async def _log_server_lockdown(self, guild: discord.Guild, reason: str, kicked_count: int, protected_count: int):
        """Log server lockdown to mod channel"""
        settings = await self.bot.db.get_antivirus_settings(guild.id)
        if not settings.mod_log_channel:
            return
        
        log_channel = guild.get_channel(settings.mod_log_channel)
        if not log_channel:
            return
        
        embed = discord.Embed(
            title="🔒 SERVER LOCKDOWN EXECUTED",
            description="KCLAntivirus has executed an emergency server lockdown.",
            color=config.Colors.ERROR,
            timestamp=datetime.utcnow()
        )
        
        embed.add_field(name="Reason", value=reason, inline=False)
        embed.add_field(name="Users Kicked", value=str(kicked_count), inline=True)
        embed.add_field(name="Protected Users", value=str(protected_count), inline=True)
        embed.add_field(name="Total Members", value=str(len(guild.members)), inline=True)
        
        try:
            await log_channel.send("@everyone", embed=embed)
        except Exception as e:
            logger.error(f"Failed to log server lockdown: {e}")
    
    async def _announce_lockdown(self, guild: discord.Guild, reason: str, kicked_count: int):
        """Announce lockdown to remaining members"""
        # Find general channel or first available text channel
        announcement_channel = None
        
        for channel in guild.text_channels:
            if channel.name.lower() in ['general', 'announcements', 'main']:
                announcement_channel = channel
                break
        
        if not announcement_channel:
            announcement_channel = guild.text_channels[0] if guild.text_channels else None
        
        if not announcement_channel:
            return
        
        embed = discord.Embed(
            title="🔒 EMERGENCY SERVER LOCKDOWN",
            description="The server has been placed under emergency lockdown by KCLAntivirus.",
            color=config.Colors.ERROR,
            timestamp=datetime.utcnow()
        )
        
        embed.add_field(name="Reason", value=reason, inline=False)
        embed.add_field(name="Action Taken", value=f"Removed {kicked_count} users as a security precaution", inline=False)
        embed.add_field(name="Status", value="Server is now secure. Normal operations will resume shortly.", inline=False)
        
        try:
            await announcement_channel.send(embed=embed)
        except Exception as e:
            logger.error(f"Failed to announce lockdown: {e}")
    
    # Commands
    @app_commands.command(name="antivirus-setup", description="Configure KCLAntivirus settings")
    @app_commands.describe(
        enabled="Enable or disable KCLAntivirus",
        auto_lockdown="Enable automatic server lockdown on raid detection",
        mod_log_channel="Channel for antivirus logs"
    )
    @is_moderator()
    async def antivirus_setup(
        self,
        interaction: discord.Interaction,
        enabled: Optional[bool] = None,
        auto_lockdown: Optional[bool] = None,
        mod_log_channel: Optional[discord.TextChannel] = None
    ):
        """Configure KCLAntivirus settings"""
        settings = await self.bot.db.get_antivirus_settings(interaction.guild.id)
        
        if enabled is not None:
            settings.enabled = enabled
        
        if auto_lockdown is not None:
            settings.auto_lockdown = auto_lockdown
        
        if mod_log_channel is not None:
            settings.mod_log_channel = mod_log_channel.id
        
        await self.bot.db.update_antivirus_settings(settings)
        
        embed = success_embed(
            "KCLAntivirus Configuration Updated",
            "Settings have been saved successfully."
        )
        
        embed.add_field(name="Enabled", value="✅ Yes" if settings.enabled else "❌ No", inline=True)
        embed.add_field(name="Auto Lockdown", value="✅ Yes" if settings.auto_lockdown else "❌ No", inline=True)
        embed.add_field(name="Log Channel", value=f"<#{settings.mod_log_channel}>" if settings.mod_log_channel else "Not set", inline=True)
        
        await interaction.response.send_message(embed=embed)
    
    @app_commands.command(name="antivirus-status", description="View KCLAntivirus status and statistics")
    @is_moderator()
    async def antivirus_status(self, interaction: discord.Interaction):
        """View KCLAntivirus status"""
        settings = await self.bot.db.get_antivirus_settings(interaction.guild.id)
        protected_roles = await self.bot.db.get_antivirus_protected_roles(interaction.guild.id)
        
        embed = discord.Embed(
            title="🛡️ KCLAntivirus Status",
            color=config.Colors.INFO if settings.enabled else config.Colors.WARNING,
            timestamp=datetime.utcnow()
        )
        
        # Main status
        embed.add_field(
            name="System Status",
            value="🟢 Active" if settings.enabled else "🔴 Disabled",
            inline=True
        )
        
        embed.add_field(
            name="Auto Lockdown",
            value="🟢 Enabled" if settings.auto_lockdown else "🔴 Disabled",
            inline=True
        )
        
        embed.add_field(
            name="VirusTotal API",
            value="🟢 Configured" if config.VIRUSTOTAL_API_KEY else "🔴 Not configured",
            inline=True
        )
        
        # Protection settings
        embed.add_field(
            name="Protected Roles",
            value=f"{len(protected_roles)} roles",
            inline=True
        )
        
        embed.add_field(
            name="Log Channel",
            value=f"<#{settings.mod_log_channel}>" if settings.mod_log_channel else "Not set",
            inline=True
        )
        
        # Thresholds
        embed.add_field(
            name="Detection Thresholds",
            value=f"Malicious: {config.KCLAntivirus.MALICIOUS_THRESHOLD}\nSuspicious: {config.KCLAntivirus.SUSPICIOUS_THRESHOLD}",
            inline=True
        )
        
        # Raid detection
        embed.add_field(
            name="Raid Detection",
            value=f"Join threshold: {config.KCLAntivirus.RAID_USER_JOIN_THRESHOLD}\nMessage threshold: {config.KCLAntivirus.RAID_MESSAGE_THRESHOLD}\nTime window: {config.KCLAntivirus.RAID_TIME_WINDOW}s",
            inline=False
        )
        
        await interaction.response.send_message(embed=embed)
    
    @app_commands.command(name="antivirus-protected-roles", description="Manage roles protected from antivirus actions")
    @app_commands.describe(
        action="Add, remove, or list protected roles",
        role="Role to add/remove from protection"
    )
    @app_commands.choices(action=[
        app_commands.Choice(name="add", value="add"),
        app_commands.Choice(name="remove", value="remove"),
        app_commands.Choice(name="list", value="list"),
        app_commands.Choice(name="clear", value="clear")
    ])
    @is_moderator()
    async def antivirus_protected_roles(
        self,
        interaction: discord.Interaction,
        action: str,
        role: Optional[discord.Role] = None
    ):
        """Manage protected roles"""
        if action == "list":
            protected_roles = await self.bot.db.get_antivirus_protected_roles(interaction.guild.id)
            
            if not protected_roles:
                embed = discord.Embed(
                    title="🛡️ Protected Roles",
                    description="No additional protected roles configured.\n\nUsers with Administrator, Manage Server, or Manage Messages permissions are automatically protected.",
                    color=config.Colors.INFO
                )
            else:
                role_mentions = []
                for role_id in protected_roles:
                    role_obj = interaction.guild.get_role(role_id)
                    if role_obj:
                        role_mentions.append(role_obj.mention)
                    else:
                        role_mentions.append(f"<@&{role_id}> (deleted)")
                
                embed = discord.Embed(
                    title="🛡️ Protected Roles",
                    description="These roles are protected from KCLAntivirus actions:\n\n" + "\n".join(f"• {role}" for role in role_mentions),
                    color=config.Colors.INFO
                )
            
            embed.set_footer(text="Protected users won't be scanned, timed out, or kicked during lockdowns")
            await interaction.response.send_message(embed=embed)
            
        elif action == "add":
            if not role:
                await interaction.response.send_message("❌ Please specify a role to protect.", ephemeral=True)
                return
            
            success = await self.bot.db.add_antivirus_protected_role(interaction.guild.id, role.id)
            
            if success:
                embed = success_embed(
                    "Role Protected",
                    f"Added {role.mention} to KCLAntivirus protection.\n\nUsers with this role will be immune to antivirus actions."
                )
                await interaction.response.send_message(embed=embed)
            else:
                await interaction.response.send_message(f"❌ {role.mention} is already protected.", ephemeral=True)
                
        elif action == "remove":
            if not role:
                await interaction.response.send_message("❌ Please specify a role to remove protection from.", ephemeral=True)
                return
            
            success = await self.bot.db.remove_antivirus_protected_role(interaction.guild.id, role.id)
            
            if success:
                embed = success_embed(
                    "Protection Removed",
                    f"Removed {role.mention} from KCLAntivirus protection.\n\nUsers with this role are no longer immune to antivirus actions."
                )
                await interaction.response.send_message(embed=embed)
            else:
                await interaction.response.send_message(f"❌ {role.mention} is not in the protected roles list.", ephemeral=True)
                
        elif action == "clear":
            count = await self.bot.db.clear_antivirus_protected_roles(interaction.guild.id)
            
            if count > 0:
                embed = success_embed(
                    "Protection Cleared",
                    f"Removed {count} role(s) from KCLAntivirus protection.\n\nOnly users with built-in permissions (Admin, Manage Server, Manage Messages) are now protected."
                )
                await interaction.response.send_message(embed=embed)
            else:
                await interaction.response.send_message("✅ No additional protected roles were configured.", ephemeral=True)
    
    @app_commands.command(name="server-scan", description="Scan server for potential threats and security issues")
    @is_moderator()
    async def server_scan(self, interaction: discord.Interaction):
        """Perform comprehensive server scan"""
        # Check cooldown
        now = datetime.utcnow()
        last_scan = self.server_scan_cooldowns.get(interaction.guild.id)
        
        if last_scan and (now - last_scan).total_seconds() < config.KCLAntivirus.SERVER_SCAN_COOLDOWN:
            remaining = config.KCLAntivirus.SERVER_SCAN_COOLDOWN - (now - last_scan).total_seconds()
            await interaction.response.send_message(
                f"⏳ Server scan is on cooldown. Try again in {remaining/60:.1f} minutes.",
                ephemeral=True
            )
            return
        
        self.server_scan_cooldowns[interaction.guild.id] = now
        
        await interaction.response.defer()
        
        # Start scan
        embed = discord.Embed(
            title="🔍 Server Scan Initiated",
            description="Scanning server for potential threats...",
            color=config.Colors.INFO,
            timestamp=datetime.utcnow()
        )
        
        await interaction.followup.send(embed=embed)
        
        # Perform scan
        scan_results = await self._perform_server_scan(interaction.guild)
        
        # Send results
        await self._send_scan_results(interaction, scan_results)
    
    @app_commands.command(name="server-lockdown", description="Force server lockdown - kicks all non-protected users")
    @app_commands.describe(reason="Reason for the lockdown")
    @is_moderator()
    async def force_server_lockdown(self, interaction: discord.Interaction, reason: Optional[str] = None):
        """Force server lockdown"""
        if not reason:
            reason = f"Manual lockdown initiated by {interaction.user}"
        
        await interaction.response.defer()
        
        # Confirm action
        embed = discord.Embed(
            title="⚠️ Confirm Server Lockdown",
            description="This will kick ALL non-protected users from the server!",
            color=config.Colors.WARNING
        )
        
        embed.add_field(name="Reason", value=reason, inline=False)
        embed.add_field(name="Protected Users", value="Users with Admin, Manage Server, Manage Messages permissions and configured protected roles will NOT be kicked.", inline=False)
        
        view = ConfirmLockdownView(self, interaction.guild, reason)
        
        await interaction.followup.send(embed=embed, view=view)
    
    async def _perform_server_scan(self, guild: discord.Guild) -> Dict[str, Any]:
        """Perform comprehensive server scan"""
        results = {
            'threats_found': 0,
            'suspicious_users': [],
            'recent_joins': 0,
            'high_activity_users': [],
            'potential_raids': False,
            'scan_time': datetime.utcnow()
        }
        
        # Check recent joins
        now = datetime.utcnow()
        recent_cutoff = now - timedelta(hours=24)
        
        recent_joins = [
            (ts, uid) for ts, uid in self.user_joins.get(guild.id, [])
            if ts > recent_cutoff
        ]
        results['recent_joins'] = len(recent_joins)
        
        # Check message activity
        high_activity_cutoff = now - timedelta(hours=1)
        recent_messages = [
            (ts, uid) for ts, uid in self.message_activity.get(guild.id, [])
            if ts > high_activity_cutoff
        ]
        
        # Find high activity users
        user_message_counts = defaultdict(int)
        for ts, uid in recent_messages:
            user_message_counts[uid] += 1
        
        for uid, count in user_message_counts.items():
            if count > 20:  # More than 20 messages in an hour
                user = guild.get_member(uid)
                if user and not await self._is_protected_user(user):
                    results['high_activity_users'].append((user, count))
        
        # Check for raid patterns
        if (results['recent_joins'] > config.KCLAntivirus.RAID_USER_JOIN_THRESHOLD or
            len(recent_messages) > config.KCLAntivirus.RAID_MESSAGE_THRESHOLD):
            results['potential_raids'] = True
        
        return results
    
    async def _send_scan_results(self, interaction: discord.Interaction, results: Dict[str, Any]):
        """Send server scan results"""
        embed = discord.Embed(
            title="🔍 Server Scan Results",
            color=config.Colors.SUCCESS if results['threats_found'] == 0 else config.Colors.WARNING,
            timestamp=results['scan_time']
        )
        
        # Overall status
        if results['threats_found'] == 0 and not results['potential_raids']:
            embed.add_field(name="Status", value="✅ No immediate threats detected", inline=False)
        else:
            embed.add_field(name="Status", value="⚠️ Potential security concerns found", inline=False)
        
        # Statistics
        embed.add_field(name="Recent Joins (24h)", value=str(results['recent_joins']), inline=True)
        embed.add_field(name="High Activity Users", value=str(len(results['high_activity_users'])), inline=True)
        embed.add_field(name="Potential Raid", value="⚠️ Yes" if results['potential_raids'] else "✅ No", inline=True)
        
        # High activity users
        if results['high_activity_users']:
            user_list = []
            for user, count in results['high_activity_users'][:5]:  # Show top 5
                user_list.append(f"• {user.mention} ({count} messages)")
            
            embed.add_field(
                name="High Activity Users (1h)",
                value="\n".join(user_list),
                inline=False
            )
        
        # Recommendations
        recommendations = []
        if results['potential_raids']:
            recommendations.append("• Consider using `/server-lockdown` if this is a raid")
        if results['recent_joins'] > 50:
            recommendations.append("• Monitor new members closely")
        if len(results['high_activity_users']) > 10:
            recommendations.append("• Check for spam or coordinated activity")
        
        if recommendations:
            embed.add_field(name="Recommendations", value="\n".join(recommendations), inline=False)
        
        await interaction.followup.send(embed=embed)


class ConfirmLockdownView(discord.ui.View):
    """Confirmation view for server lockdown"""
    
    def __init__(self, antivirus_cog, guild: discord.Guild, reason: str):
        super().__init__(timeout=60)
        self.antivirus_cog = antivirus_cog
        self.guild = guild
        self.reason = reason
    
    @discord.ui.button(label="Confirm Lockdown", style=discord.ButtonStyle.danger, emoji="🔒")
    async def confirm_lockdown(self, interaction, button):
        await interaction.response.defer()
        
        # Disable all buttons
        for item in self.children:
            item.disabled = True
        
        await interaction.edit_original_response(view=self)
        
        # Execute lockdown
        await self.antivirus_cog._server_lockdown(self.guild, self.reason)
        
        embed = discord.Embed(
            title="🔒 Server Lockdown Executed",
            description="Emergency server lockdown has been initiated.",
            color=config.Colors.ERROR,
            timestamp=datetime.utcnow()
        )
        
        await interaction.followup.send(embed=embed)
    
    @discord.ui.button(label="Cancel", style=discord.ButtonStyle.secondary, emoji="❌")
    async def cancel_lockdown(self, interaction, button):
        embed = discord.Embed(
            title="❌ Lockdown Cancelled",
            description="Server lockdown has been cancelled.",
            color=config.Colors.SUCCESS
        )
        
        await interaction.response.edit_message(embed=embed, view=None)