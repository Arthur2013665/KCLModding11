"""
KCLAntivirus - Simplified version for compatibility
Advanced server protection system with VirusTotal integration
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

class KCLAntivirusSimple(commands.Cog):
    """KCLAntivirus - Advanced server protection system"""
    
    def __init__(self, bot):
        self.bot = bot
        self.session = None
        
        # Tracking dictionaries
        self.user_joins = defaultdict(list)
        self.message_activity = defaultdict(list)
        self.scan_cooldowns = defaultdict(dict)
        self.server_scan_cooldowns = {}
        
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
    async def on_message(self, message):
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
    async def on_member_join(self, member):
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
    
    async def _is_protected_user(self, user):
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
    
    async def _scan_attachments(self, message):
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
    
    async def _scan_urls(self, message, urls):
        """Scan URLs for malicious content"""
        for url in urls:
            try:
                scan_result = await self._virustotal_scan_url(url)
                if scan_result:
                    await self._handle_scan_result(message, scan_result, url)
            except Exception as e:
                logger.error(f"Error scanning URL {url}: {e}")
    
    async def _virustotal_scan_file(self, attachment):
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
    
    async def _upload_file_to_virustotal(self, file_data, filename):
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
    
    async def _virustotal_scan_url(self, url):
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
    
    async def _get_virustotal_analysis(self, analysis_id):
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
    
    async def _handle_scan_result(self, message, scan_result, item_name):
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
    
    async def _handle_threat(self, message, item_name, threat_level, malicious, suspicious):
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
            
            # Log to database
            action_taken = f"Message deleted, user timed out for {config.KCLAntivirus.VIRUS_TIMEOUT_DAYS} day(s), warning added"
            await self._log_scan_to_database(
                message.guild.id,
                message.author.id,
                item_name,
                "file" if "." in item_name else "url",
                threat_level,
                malicious,
                suspicious,
                action_taken
            )
            
            # DM the user
            await self._dm_user_threat(message.author, item_name, threat_level, malicious, suspicious)
            
            # Log to mod channel
            await self._log_threat_detection(message, item_name, threat_level, malicious, suspicious)
            
            logger.warning(f"Threat detected: {threat_level} - {item_name} by {message.author} in {message.guild}")
            
        except Exception as e:
            logger.error(f"Error handling threat: {e}")
    
    async def _handle_dangerous_file(self, message, attachment):
        """Handle files with dangerous extensions"""
        await self._handle_threat(
            message, 
            attachment.filename, 
            "DANGEROUS FILE TYPE", 
            1, 
            0
        )
    
    async def _handle_large_file(self, message, attachment):
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
    
    async def _dm_user_threat(self, user, item_name, threat_level, malicious, suspicious):
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
    
    async def _log_threat_detection(self, message, item_name, threat_level, malicious, suspicious):
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
    
    async def _check_raid_activity(self, guild):
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
    
    async def _trigger_raid_protection(self, guild, join_count, message_count):
        """Trigger raid protection measures"""
        logger.warning(f"Raid detected in {guild.name}: {join_count} joins, {message_count} messages")
        
        settings = await self.bot.db.get_antivirus_settings(guild.id)
        if not settings.auto_lockdown:
            # Just alert mods
            await self._alert_mods_raid(guild, join_count, message_count)
            return
        
        # Trigger server lockdown
        await self._server_lockdown(guild, f"Automatic raid protection: {join_count} joins, {message_count} messages in {config.KCLAntivirus.RAID_TIME_WINDOW}s")
    
    async def _alert_mods_raid(self, guild, join_count, message_count):
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
    
    async def _server_lockdown(self, guild, reason):
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
    
    async def _dm_user_lockdown(self, user, reason):
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
    
    async def _log_server_lockdown(self, guild, reason, kicked_count, protected_count):
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
    
    # Enhanced slash commands with all features
    @app_commands.command(name="antivirus-setup")
    @app_commands.describe(
        enabled="Enable or disable KCLAntivirus",
        auto_lockdown="Enable automatic server lockdown on raid detection",
        log_channel="Channel for antivirus security logs"
    )
    @is_moderator()
    async def antivirus_setup(self, interaction, enabled: bool = None, auto_lockdown: bool = None, log_channel: discord.TextChannel = None):
        """Configure KCLAntivirus settings"""
        settings = await self.bot.db.get_antivirus_settings(interaction.guild.id)
        
        if enabled is not None:
            settings.enabled = enabled
        
        if auto_lockdown is not None:
            settings.auto_lockdown = auto_lockdown
        
        if log_channel is not None:
            settings.mod_log_channel = log_channel.id
        
        await self.bot.db.update_antivirus_settings(settings)
        
        embed = success_embed(
            "KCLAntivirus Configuration Updated",
            "Settings have been saved successfully."
        )
        
        embed.add_field(name="Enabled", value="✅ Yes" if settings.enabled else "❌ No", inline=True)
        embed.add_field(name="Auto Lockdown", value="✅ Yes" if settings.auto_lockdown else "❌ No", inline=True)
        embed.add_field(name="Log Channel", value=f"<#{settings.mod_log_channel}>" if settings.mod_log_channel else "Not set", inline=True)
        
        await interaction.response.send_message(embed=embed)
    
    @app_commands.command(name="antivirus-status")
    @is_moderator()
    async def antivirus_status(self, interaction):
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
        
        # Detection thresholds
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
        
        # Current activity
        now = datetime.utcnow()
        recent_joins = len([
            (ts, uid) for ts, uid in self.user_joins.get(interaction.guild.id, [])
            if (now - ts).total_seconds() < 300  # Last 5 minutes
        ])
        recent_messages = len([
            (ts, uid) for ts, uid in self.message_activity.get(interaction.guild.id, [])
            if (now - ts).total_seconds() < 300  # Last 5 minutes
        ])
        
        embed.add_field(
            name="Recent Activity (5min)",
            value=f"Joins: {recent_joins}\nMessages: {recent_messages}",
            inline=True
        )
        
        embed.set_footer(text="Use /antivirus-setup to configure settings")
        
        await interaction.response.send_message(embed=embed)
    
    @app_commands.command(name="antivirus-add-role")
    @app_commands.describe(role="Role to protect from antivirus actions")
    @is_moderator()
    async def antivirus_add_role(self, interaction, role: discord.Role):
        """Add a role to antivirus protection"""
        success = await self.bot.db.add_antivirus_protected_role(interaction.guild.id, role.id)
        
        if success:
            embed = success_embed(
                "Role Protected",
                f"Added {role.mention} to KCLAntivirus protection.\n\nUsers with this role will be immune to antivirus actions."
            )
            await interaction.response.send_message(embed=embed)
        else:
            await interaction.response.send_message(f"❌ {role.mention} is already protected.", ephemeral=True)
    
    @app_commands.command(name="antivirus-remove-role")
    @app_commands.describe(role="Role to remove from antivirus protection")
    @is_moderator()
    async def antivirus_remove_role(self, interaction, role: discord.Role):
        """Remove a role from antivirus protection"""
        success = await self.bot.db.remove_antivirus_protected_role(interaction.guild.id, role.id)
        
        if success:
            embed = success_embed(
                "Protection Removed",
                f"Removed {role.mention} from KCLAntivirus protection.\n\nUsers with this role are no longer immune to antivirus actions."
            )
            await interaction.response.send_message(embed=embed)
        else:
            await interaction.response.send_message(f"❌ {role.mention} is not in the protected roles list.", ephemeral=True)
    
    @app_commands.command(name="antivirus-list-roles")
    @is_moderator()
    async def antivirus_list_roles(self, interaction):
        """List all roles protected from antivirus actions"""
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
    
    @app_commands.command(name="antivirus-clear-roles")
    @is_moderator()
    async def antivirus_clear_roles(self, interaction):
        """Clear all protected roles"""
        count = await self.bot.db.clear_antivirus_protected_roles(interaction.guild.id)
        
        if count > 0:
            embed = success_embed(
                "Protection Cleared",
                f"Removed {count} role(s) from KCLAntivirus protection.\n\nOnly users with built-in permissions (Admin, Manage Server, Manage Messages) are now protected."
            )
            await interaction.response.send_message(embed=embed)
        else:
            await interaction.response.send_message("✅ No additional protected roles were configured.", ephemeral=True)
    
    @app_commands.command(name="server-scan")
    @is_moderator()
    async def server_scan(self, interaction):
        """Scan server for potential threats and security issues"""
        await interaction.response.defer()
        
        # Start scan (no cooldown)
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
    
    @app_commands.command(name="server-file-scan")
    @app_commands.describe(
        hours="How many hours back to scan files (default: 24)",
        channel="Specific channel to scan (optional)"
    )
    @is_moderator()
    async def server_file_scan(self, interaction, hours: int = 24, channel: discord.TextChannel = None):
        """Scan all files uploaded to the server in the specified time period"""
        await interaction.response.defer()
        
        # Start scan
        embed = discord.Embed(
            title="📁 Server File Scan Initiated",
            description=f"Scanning files from the last {hours} hours...",
            color=config.Colors.INFO,
            timestamp=datetime.utcnow()
        )
        
        if channel:
            embed.add_field(name="Target", value=f"Scanning only {channel.mention}", inline=True)
        else:
            embed.add_field(name="Target", value="Scanning all channels", inline=True)
        
        await interaction.followup.send(embed=embed)
        
        # Perform file scan
        scan_results = await self._perform_file_scan(interaction.guild, hours, channel)
        
        # Send results
        await self._send_file_scan_results(interaction, scan_results, hours, channel)
    
    @app_commands.command(name="server-link-scan")
    @app_commands.describe(
        hours="How many hours back to scan links (default: 24)",
        channel="Specific channel to scan (optional)"
    )
    @is_moderator()
    async def server_link_scan(self, interaction, hours: int = 24, channel: discord.TextChannel = None):
        """Scan all links posted to the server in the specified time period"""
        await interaction.response.defer()
        
        # Start scan
        embed = discord.Embed(
            title="🔗 Server Link Scan Initiated",
            description=f"Scanning links from the last {hours} hours...",
            color=config.Colors.INFO,
            timestamp=datetime.utcnow()
        )
        
        if channel:
            embed.add_field(name="Target", value=f"Scanning only {channel.mention}", inline=True)
        else:
            embed.add_field(name="Target", value="Scanning all channels", inline=True)
        
        await interaction.followup.send(embed=embed)
        
        # Perform link scan
        scan_results = await self._perform_link_scan(interaction.guild, hours, channel)
        
        # Send results
        await self._send_link_scan_results(interaction, scan_results, hours, channel)
    
    @app_commands.command(name="server-file-link-scan")
    @app_commands.describe(
        hours="How many hours back to scan files and links (default: 24)",
        channel="Specific channel to scan (optional)"
    )
    @is_moderator()
    async def server_file_link_scan(self, interaction, hours: int = 24, channel: discord.TextChannel = None):
        """Scan all files and links posted to the server in the specified time period"""
        await interaction.response.defer()
        
        # Start scan
        embed = discord.Embed(
            title="📁🔗 Server File & Link Scan Initiated",
            description=f"Scanning files and links from the last {hours} hours...",
            color=config.Colors.INFO,
            timestamp=datetime.utcnow()
        )
        
        if channel:
            embed.add_field(name="Target", value=f"Scanning only {channel.mention}", inline=True)
        else:
            embed.add_field(name="Target", value="Scanning all channels", inline=True)
        
        await interaction.followup.send(embed=embed)
        
        # Perform combined scan
        file_results = await self._perform_file_scan(interaction.guild, hours, channel)
        link_results = await self._perform_link_scan(interaction.guild, hours, channel)
        
        # Send combined results
        await self._send_combined_scan_results(interaction, file_results, link_results, hours, channel)
    
    @app_commands.command(name="server-lockdown")
    @app_commands.describe(reason="Reason for the lockdown")
    @is_moderator()
    async def force_server_lockdown(self, interaction, reason: str = None):
        """Force server lockdown - kicks all non-protected users"""
        if not reason:
            reason = f"Manual lockdown initiated by {interaction.user}"
        
        await interaction.response.defer()
        
        # Show confirmation dialog
        embed = discord.Embed(
            title="⚠️ Confirm Server Lockdown",
            description="This will kick ALL non-protected users from the server!",
            color=config.Colors.WARNING
        )
        
        embed.add_field(name="Reason", value=reason, inline=False)
        embed.add_field(name="Protected Users", value="Users with Admin, Manage Server, Manage Messages permissions and configured protected roles will NOT be kicked.", inline=False)
        
        view = ConfirmLockdownView(self, interaction.guild, reason)
        
        await interaction.followup.send(embed=embed, view=view)
    
    async def _log_scan_to_database(self, guild_id, user_id, item_name, item_type, threat_level, malicious_count, suspicious_count, action_taken):
        """Log scan results to database"""
        try:
            await self.bot.db.add_antivirus_scan_log(
                guild_id, user_id, item_name, item_type, threat_level, 
                malicious_count, suspicious_count, action_taken
            )
        except Exception as e:
            logger.error(f"Failed to log scan to database: {e}")
    
    @app_commands.command(name="antivirus-scan-logs")
    @app_commands.describe(limit="Number of recent logs to show (max 20)")
    @is_moderator()
    async def antivirus_scan_logs(self, interaction, limit: int = 10):
        """View recent antivirus scan logs"""
        if limit > 20:
            limit = 20
        
        logs = await self.bot.db.get_antivirus_scan_logs(interaction.guild.id, limit)
        
        if not logs:
            embed = discord.Embed(
                title="📋 Antivirus Scan Logs",
                description="No scan logs found.",
                color=config.Colors.INFO
            )
            await interaction.response.send_message(embed=embed)
            return
        
        embed = discord.Embed(
            title="📋 Recent Antivirus Scan Logs",
            description=f"Showing last {len(logs)} scan results:",
            color=config.Colors.INFO,
            timestamp=datetime.utcnow()
        )
        
        for log in logs[:10]:  # Show max 10 in embed
            user = interaction.guild.get_member(log['user_id'])
            user_name = user.display_name if user else f"User {log['user_id']}"
            
            threat_emoji = "🦠" if log['threat_level'] == "MALICIOUS" else "⚠️" if log['threat_level'] == "SUSPICIOUS" else "🔍"
            
            embed.add_field(
                name=f"{threat_emoji} {log['threat_level']}",
                value=f"**User:** {user_name}\n**Item:** {log['item_name']}\n**Detection:** {log['malicious_count']}M/{log['suspicious_count']}S\n**Action:** {log['action_taken'] or 'None'}",
                inline=True
            )
        
        embed.set_footer(text=f"Total logs: {len(logs)} | Use limit parameter to see more")
        
        await interaction.response.send_message(embed=embed)
    
    @app_commands.command(name="antivirus-quarantine")
    @app_commands.describe(
        channel="Channel to use for quarantining suspicious content",
        action="Set or remove quarantine channel"
    )
    @app_commands.choices(action=[
        app_commands.Choice(name="set", value="set"),
        app_commands.Choice(name="remove", value="remove")
    ])
    @is_moderator()
    async def antivirus_quarantine(self, interaction, action: str, channel: discord.TextChannel = None):
        """Configure quarantine channel for suspicious content"""
        settings = await self.bot.db.get_antivirus_settings(interaction.guild.id)
        
        if action == "set":
            if not channel:
                await interaction.response.send_message("❌ Please specify a channel to use for quarantine.", ephemeral=True)
                return
            
            settings.quarantine_channel = channel.id
            await self.bot.db.update_antivirus_settings(settings)
            
            embed = success_embed(
                "Quarantine Channel Set",
                f"Suspicious content will now be moved to {channel.mention} instead of being deleted."
            )
            await interaction.response.send_message(embed=embed)
            
        elif action == "remove":
            settings.quarantine_channel = None
            await self.bot.db.update_antivirus_settings(settings)
            
            embed = success_embed(
                "Quarantine Channel Removed",
                "Suspicious content will now be deleted instead of quarantined."
            )
            await interaction.response.send_message(embed=embed)
    
    @app_commands.command(name="antivirus-stats")
    @is_moderator()
    async def antivirus_stats(self, interaction):
        """View detailed antivirus statistics"""
        # Get recent scan logs
        logs = await self.bot.db.get_antivirus_scan_logs(interaction.guild.id, 100)
        
        # Calculate statistics
        total_scans = len(logs)
        malicious_count = len([log for log in logs if log['threat_level'] == 'MALICIOUS'])
        suspicious_count = len([log for log in logs if log['threat_level'] == 'SUSPICIOUS'])
        safe_count = total_scans - malicious_count - suspicious_count
        
        # Get current activity
        now = datetime.utcnow()
        recent_joins = len([
            (ts, uid) for ts, uid in self.user_joins.get(interaction.guild.id, [])
            if (now - ts).total_seconds() < 3600  # Last hour
        ])
        recent_messages = len([
            (ts, uid) for ts, uid in self.message_activity.get(interaction.guild.id, [])
            if (now - ts).total_seconds() < 3600  # Last hour
        ])
        
        embed = discord.Embed(
            title="📊 KCLAntivirus Statistics",
            color=config.Colors.INFO,
            timestamp=datetime.utcnow()
        )
        
        # Scan statistics
        embed.add_field(
            name="Scan Results (Recent 100)",
            value=f"🦠 Malicious: {malicious_count}\n⚠️ Suspicious: {suspicious_count}\n✅ Safe: {safe_count}\n📊 Total: {total_scans}",
            inline=True
        )
        
        # Activity monitoring
        embed.add_field(
            name="Activity (Last Hour)",
            value=f"👥 User Joins: {recent_joins}\n💬 Messages: {recent_messages}",
            inline=True
        )
        
        # Protection status
        protected_roles = await self.bot.db.get_antivirus_protected_roles(interaction.guild.id)
        embed.add_field(
            name="Protection Status",
            value=f"🛡️ Protected Roles: {len(protected_roles)}\n👑 Auto-Protected: Admins, Mods",
            inline=True
        )
        
        # Threat detection rates
        if total_scans > 0:
            threat_rate = ((malicious_count + suspicious_count) / total_scans) * 100
            embed.add_field(
                name="Detection Rate",
                value=f"🎯 Threat Rate: {threat_rate:.1f}%\n🔍 Scans Performed: {total_scans}",
                inline=True
            )
        
        # System health
        api_status = "🟢 Online" if config.VIRUSTOTAL_API_KEY else "🔴 Not Configured"
        embed.add_field(
            name="System Health",
            value=f"🔌 VirusTotal API: {api_status}\n⚡ Background Tasks: Running",
            inline=True
        )
        
        embed.set_footer(text="Statistics are based on recent activity and scan logs")
        
        await interaction.response.send_message(embed=embed)
    
    @app_commands.command(name="antivirus-help")
    @is_moderator()
    async def antivirus_help(self, interaction):
        """Show comprehensive KCLAntivirus help"""
        embed = discord.Embed(
            title="🛡️ KCLAntivirus Help Guide",
            description="Complete guide to using KCLAntivirus protection system",
            color=config.Colors.INFO,
            timestamp=datetime.utcnow()
        )
        
        # Setup commands
        embed.add_field(
            name="🔧 Setup Commands",
            value="`/antivirus-setup` - Configure main settings\n`/antivirus-status` - View system status\n`/antivirus-quarantine` - Set quarantine channel",
            inline=False
        )
        
        # Role management
        embed.add_field(
            name="👥 Role Management",
            value="`/antivirus-add-role` - Protect a role\n`/antivirus-remove-role` - Remove protection\n`/antivirus-list-roles` - List protected roles\n`/antivirus-clear-roles` - Clear all protected roles",
            inline=False
        )
        
        # Security operations
        embed.add_field(
            name="🔍 Security Operations",
            value="`/server-scan` - Comprehensive security audit\n`/server-lockdown` - Emergency lockdown\n`/antivirus-scan-logs` - View scan history\n`/antivirus-stats` - Detailed statistics",
            inline=False
        )
        
        # How it works
        embed.add_field(
            name="⚙️ How It Works",
            value="• Scans all files/URLs with VirusTotal\n• Deletes malicious content instantly\n• Times out users for 1 day\n• Sends explanatory DMs\n• Logs everything for review",
            inline=False
        )
        
        # Protection levels
        embed.add_field(
            name="🛡️ Protection Levels",
            value="**Auto-Protected:** Admin, Manage Server, Manage Messages\n**Custom Protected:** Your configured roles\n**Regular Users:** Subject to all scanning",
            inline=False
        )
        
        # Quick start
        embed.add_field(
            name="🚀 Quick Start",
            value="1. `/antivirus-setup enabled:True`\n2. `/antivirus-setup log_channel:#security`\n3. `/antivirus-add-role role:@Staff`\n4. `/antivirus-status` to verify",
            inline=False
        )
        
        embed.set_footer(text="KCLAntivirus - Military-grade Discord server protection")
        
        await interaction.response.send_message(embed=embed)
    
    async def _perform_file_scan(self, guild, hours, target_channel=None):
        """Perform comprehensive file scan"""
        results = {
            'files_scanned': 0,
            'threats_found': 0,
            'malicious_files': [],
            'suspicious_files': [],
            'safe_files': 0,
            'scan_time': datetime.utcnow(),
            'channels_scanned': 0,
            'errors': []
        }
        
        cutoff_time = datetime.utcnow() - timedelta(hours=hours)
        channels_to_scan = [target_channel] if target_channel else guild.text_channels
        
        for channel in channels_to_scan:
            if not channel.permissions_for(guild.me).read_message_history:
                results['errors'].append(f"No permission to read {channel.name}")
                continue
            
            results['channels_scanned'] += 1
            
            try:
                async for message in channel.history(limit=1000, after=cutoff_time):
                    if message.attachments:
                        for attachment in message.attachments:
                            results['files_scanned'] += 1
                            
                            # Check file extension first
                            file_ext = attachment.filename.lower().split('.')[-1] if '.' in attachment.filename else ''
                            
                            if f'.{file_ext}' in config.KCLAntivirus.DANGEROUS_EXTENSIONS:
                                results['threats_found'] += 1
                                results['malicious_files'].append({
                                    'name': attachment.filename,
                                    'user': message.author,
                                    'channel': channel,
                                    'message_id': message.id,
                                    'reason': 'Dangerous file extension',
                                    'timestamp': message.created_at
                                })
                                continue
                            
                            if f'.{file_ext}' in config.KCLAntivirus.SAFE_EXTENSIONS:
                                results['safe_files'] += 1
                                continue
                            
                            # Scan with VirusTotal if possible
                            if attachment.size <= config.KCLAntivirus.MAX_FILE_SIZE_MB * 1024 * 1024:
                                try:
                                    scan_result = await self._virustotal_scan_file(attachment)
                                    if scan_result:
                                        stats = scan_result.get('stats', {})
                                        malicious = stats.get('malicious', 0)
                                        suspicious = stats.get('suspicious', 0)
                                        
                                        if malicious >= config.KCLAntivirus.MALICIOUS_THRESHOLD:
                                            results['threats_found'] += 1
                                            results['malicious_files'].append({
                                                'name': attachment.filename,
                                                'user': message.author,
                                                'channel': channel,
                                                'message_id': message.id,
                                                'reason': f'{malicious} engines detected malware',
                                                'timestamp': message.created_at
                                            })
                                        elif suspicious >= config.KCLAntivirus.SUSPICIOUS_THRESHOLD:
                                            results['threats_found'] += 1
                                            results['suspicious_files'].append({
                                                'name': attachment.filename,
                                                'user': message.author,
                                                'channel': channel,
                                                'message_id': message.id,
                                                'reason': f'{suspicious} engines flagged as suspicious',
                                                'timestamp': message.created_at
                                            })
                                        else:
                                            results['safe_files'] += 1
                                    else:
                                        results['safe_files'] += 1
                                except Exception as e:
                                    results['errors'].append(f"Error scanning {attachment.filename}: {str(e)[:100]}")
                                    results['safe_files'] += 1
                            else:
                                results['errors'].append(f"File too large to scan: {attachment.filename}")
                                results['safe_files'] += 1
                            
                            # Small delay to avoid rate limits
                            await asyncio.sleep(0.1)
                            
            except Exception as e:
                results['errors'].append(f"Error scanning channel {channel.name}: {str(e)[:100]}")
        
        return results
    
    async def _perform_link_scan(self, guild, hours, target_channel=None):
        """Perform comprehensive link scan"""
        results = {
            'links_scanned': 0,
            'threats_found': 0,
            'malicious_links': [],
            'suspicious_links': [],
            'safe_links': 0,
            'scan_time': datetime.utcnow(),
            'channels_scanned': 0,
            'errors': []
        }
        
        cutoff_time = datetime.utcnow() - timedelta(hours=hours)
        channels_to_scan = [target_channel] if target_channel else guild.text_channels
        
        for channel in channels_to_scan:
            if not channel.permissions_for(guild.me).read_message_history:
                results['errors'].append(f"No permission to read {channel.name}")
                continue
            
            results['channels_scanned'] += 1
            
            try:
                async for message in channel.history(limit=1000, after=cutoff_time):
                    urls = self.url_pattern.findall(message.content)
                    
                    for url in urls:
                        results['links_scanned'] += 1
                        
                        try:
                            scan_result = await self._virustotal_scan_url(url)
                            if scan_result:
                                stats = scan_result.get('stats', {})
                                malicious = stats.get('malicious', 0)
                                suspicious = stats.get('suspicious', 0)
                                
                                if malicious >= config.KCLAntivirus.MALICIOUS_THRESHOLD:
                                    results['threats_found'] += 1
                                    results['malicious_links'].append({
                                        'url': url,
                                        'user': message.author,
                                        'channel': channel,
                                        'message_id': message.id,
                                        'reason': f'{malicious} engines detected malware',
                                        'timestamp': message.created_at
                                    })
                                elif suspicious >= config.KCLAntivirus.SUSPICIOUS_THRESHOLD:
                                    results['threats_found'] += 1
                                    results['suspicious_links'].append({
                                        'url': url,
                                        'user': message.author,
                                        'channel': channel,
                                        'message_id': message.id,
                                        'reason': f'{suspicious} engines flagged as suspicious',
                                        'timestamp': message.created_at
                                    })
                                else:
                                    results['safe_links'] += 1
                            else:
                                results['safe_links'] += 1
                        except Exception as e:
                            results['errors'].append(f"Error scanning URL {url[:50]}...: {str(e)[:100]}")
                            results['safe_links'] += 1
                        
                        # Small delay to avoid rate limits
                        await asyncio.sleep(0.2)
                        
            except Exception as e:
                results['errors'].append(f"Error scanning channel {channel.name}: {str(e)[:100]}")
        
        return results
    
    async def _send_file_scan_results(self, interaction, results, hours, channel):
        """Send file scan results"""
        embed = discord.Embed(
            title="📁 File Scan Results",
            color=config.Colors.SUCCESS if results['threats_found'] == 0 else config.Colors.ERROR,
            timestamp=results['scan_time']
        )
        
        # Summary
        embed.add_field(
            name="📊 Summary",
            value=f"Files Scanned: {results['files_scanned']}\n🦠 Threats Found: {results['threats_found']}\n✅ Safe Files: {results['safe_files']}\n📂 Channels: {results['channels_scanned']}",
            inline=True
        )
        
        # Time period
        embed.add_field(
            name="⏰ Scan Period",
            value=f"Last {hours} hours\n{'All channels' if not channel else f'Only {channel.mention}'}",
            inline=True
        )
        
        # Threats found
        if results['malicious_files'] or results['suspicious_files']:
            threat_list = []
            
            for file_info in results['malicious_files'][:3]:  # Show top 3
                threat_list.append(f"🦠 **{file_info['name']}** by {file_info['user'].mention} in {file_info['channel'].mention}")
            
            for file_info in results['suspicious_files'][:3]:  # Show top 3
                threat_list.append(f"⚠️ **{file_info['name']}** by {file_info['user'].mention} in {file_info['channel'].mention}")
            
            if threat_list:
                embed.add_field(
                    name="🚨 Threats Detected",
                    value="\n".join(threat_list[:5]),  # Max 5 total
                    inline=False
                )
        
        # Errors
        if results['errors']:
            embed.add_field(
                name="⚠️ Scan Issues",
                value=f"{len(results['errors'])} issues encountered during scan",
                inline=True
            )
        
        embed.set_footer(text=f"Scan completed • {results['files_scanned']} files processed")
        
        await interaction.followup.send(embed=embed)
    
    async def _send_link_scan_results(self, interaction, results, hours, channel):
        """Send link scan results"""
        embed = discord.Embed(
            title="🔗 Link Scan Results",
            color=config.Colors.SUCCESS if results['threats_found'] == 0 else config.Colors.ERROR,
            timestamp=results['scan_time']
        )
        
        # Summary
        embed.add_field(
            name="📊 Summary",
            value=f"Links Scanned: {results['links_scanned']}\n🦠 Threats Found: {results['threats_found']}\n✅ Safe Links: {results['safe_links']}\n📂 Channels: {results['channels_scanned']}",
            inline=True
        )
        
        # Time period
        embed.add_field(
            name="⏰ Scan Period",
            value=f"Last {hours} hours\n{'All channels' if not channel else f'Only {channel.mention}'}",
            inline=True
        )
        
        # Threats found
        if results['malicious_links'] or results['suspicious_links']:
            threat_list = []
            
            for link_info in results['malicious_links'][:3]:  # Show top 3
                url_display = link_info['url'][:50] + "..." if len(link_info['url']) > 50 else link_info['url']
                threat_list.append(f"🦠 **{url_display}** by {link_info['user'].mention} in {link_info['channel'].mention}")
            
            for link_info in results['suspicious_links'][:3]:  # Show top 3
                url_display = link_info['url'][:50] + "..." if len(link_info['url']) > 50 else link_info['url']
                threat_list.append(f"⚠️ **{url_display}** by {link_info['user'].mention} in {link_info['channel'].mention}")
            
            if threat_list:
                embed.add_field(
                    name="🚨 Threats Detected",
                    value="\n".join(threat_list[:5]),  # Max 5 total
                    inline=False
                )
        
        # Errors
        if results['errors']:
            embed.add_field(
                name="⚠️ Scan Issues",
                value=f"{len(results['errors'])} issues encountered during scan",
                inline=True
            )
        
        embed.set_footer(text=f"Scan completed • {results['links_scanned']} links processed")
        
        await interaction.followup.send(embed=embed)
    
    async def _send_combined_scan_results(self, interaction, file_results, link_results, hours, channel):
        """Send combined file and link scan results"""
        total_threats = file_results['threats_found'] + link_results['threats_found']
        
        embed = discord.Embed(
            title="📁🔗 Combined File & Link Scan Results",
            color=config.Colors.SUCCESS if total_threats == 0 else config.Colors.ERROR,
            timestamp=datetime.utcnow()
        )
        
        # Summary
        embed.add_field(
            name="📊 Files Summary",
            value=f"Scanned: {file_results['files_scanned']}\n🦠 Threats: {file_results['threats_found']}\n✅ Safe: {file_results['safe_files']}",
            inline=True
        )
        
        embed.add_field(
            name="📊 Links Summary", 
            value=f"Scanned: {link_results['links_scanned']}\n🦠 Threats: {link_results['threats_found']}\n✅ Safe: {link_results['safe_links']}",
            inline=True
        )
        
        embed.add_field(
            name="⏰ Scan Period",
            value=f"Last {hours} hours\n{'All channels' if not channel else f'Only {channel.mention}'}",
            inline=True
        )
        
        # Combined threats
        all_threats = []
        
        for file_info in file_results['malicious_files'][:2]:
            all_threats.append(f"🦠📁 **{file_info['name']}** by {file_info['user'].mention}")
        
        for link_info in link_results['malicious_links'][:2]:
            url_display = link_info['url'][:30] + "..." if len(link_info['url']) > 30 else link_info['url']
            all_threats.append(f"🦠🔗 **{url_display}** by {link_info['user'].mention}")
        
        for file_info in file_results['suspicious_files'][:1]:
            all_threats.append(f"⚠️📁 **{file_info['name']}** by {file_info['user'].mention}")
        
        for link_info in link_results['suspicious_links'][:1]:
            url_display = link_info['url'][:30] + "..." if len(link_info['url']) > 30 else link_info['url']
            all_threats.append(f"⚠️🔗 **{url_display}** by {link_info['user'].mention}")
        
        if all_threats:
            embed.add_field(
                name="🚨 Top Threats Detected",
                value="\n".join(all_threats[:6]),  # Max 6 total
                inline=False
            )
        
        # Overall status
        total_scanned = file_results['files_scanned'] + link_results['links_scanned']
        embed.add_field(
            name="🎯 Overall Results",
            value=f"**Total Items:** {total_scanned}\n**Total Threats:** {total_threats}\n**Success Rate:** {((total_scanned - total_threats) / max(total_scanned, 1) * 100):.1f}%",
            inline=False
        )
        
        embed.set_footer(text=f"Combined scan completed • {total_scanned} items processed")
        
        await interaction.followup.send(embed=embed)
    
    async def _perform_server_scan(self, guild):
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
    
    async def _send_scan_results(self, interaction, results):
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
    
    def __init__(self, antivirus_cog, guild, reason):
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

async def setup(bot):
    await bot.add_cog(KCLAntivirusSimple(bot))