"""
Database manager for SQLite operations
Handles all database interactions asynchronously
"""
import aiosqlite
import logging
from datetime import datetime
from typing import Optional, List, Dict, Any
from .models import User, Warning, ModLog, CustomCommand, YouTubeSub, BloxFruitsAlert, GuildSettings, Mute, AntivirusSettings

logger = logging.getLogger('discord_bot.database')

class DatabaseManager:
    """Manages database connections and operations"""
    
    def __init__(self, db_path: str):
        self.db_path = db_path
        self.connection: Optional[aiosqlite.Connection] = None
    
    async def initialize(self):
        """Initialize database connection and create tables"""
        self.connection = await aiosqlite.connect(self.db_path)
        self.connection.row_factory = aiosqlite.Row
        await self._create_tables()
        logger.info(f"Database initialized at {self.db_path}")
    
    async def _create_tables(self):
        """Create all necessary database tables"""
        async with self.connection.cursor() as cursor:
            # Users table
            await cursor.execute("""
                CREATE TABLE IF NOT EXISTS users (
                    user_id INTEGER NOT NULL,
                    guild_id INTEGER NOT NULL,
                    xp INTEGER DEFAULT 0,
                    level INTEGER DEFAULT 1,
                    balance INTEGER DEFAULT 0,
                    last_daily TIMESTAMP,
                    last_message TIMESTAMP,
                    PRIMARY KEY (user_id, guild_id)
                )
            """)
            
            # Warnings table
            await cursor.execute("""
                CREATE TABLE IF NOT EXISTS warnings (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    user_id INTEGER NOT NULL,
                    guild_id INTEGER NOT NULL,
                    moderator_id INTEGER NOT NULL,
                    reason TEXT NOT NULL,
                    timestamp TIMESTAMP DEFAULT CURRENT_TIMESTAMP
                )
            """)
            
            # Moderation logs table
            await cursor.execute("""
                CREATE TABLE IF NOT EXISTS mod_logs (
                    case_id INTEGER PRIMARY KEY AUTOINCREMENT,
                    guild_id INTEGER NOT NULL,
                    action_type TEXT NOT NULL,
                    user_id INTEGER NOT NULL,
                    moderator_id INTEGER NOT NULL,
                    reason TEXT,
                    timestamp TIMESTAMP DEFAULT CURRENT_TIMESTAMP
                )
            """)
            
            # Custom commands table
            await cursor.execute("""
                CREATE TABLE IF NOT EXISTS custom_commands (
                    guild_id INTEGER NOT NULL,
                    trigger TEXT NOT NULL,
                    response TEXT NOT NULL,
                    created_by INTEGER NOT NULL,
                    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                    PRIMARY KEY (guild_id, trigger)
                )
            """)
            
            # YouTube subscriptions table
            await cursor.execute("""
                CREATE TABLE IF NOT EXISTS youtube_subs (
                    guild_id INTEGER NOT NULL,
                    channel_id TEXT NOT NULL,
                    notification_channel INTEGER NOT NULL,
                    last_video_id TEXT,
                    PRIMARY KEY (guild_id, channel_id)
                )
            """)
            
            # Blox Fruits alerts table
            await cursor.execute("""
                CREATE TABLE IF NOT EXISTS bloxfruits_alerts (
                    user_id INTEGER NOT NULL,
                    guild_id INTEGER NOT NULL,
                    fruit_name TEXT NOT NULL,
                    PRIMARY KEY (user_id, guild_id, fruit_name)
                )
            """)
            
            # Guild settings table
            await cursor.execute("""
                CREATE TABLE IF NOT EXISTS guild_settings (
                    guild_id INTEGER PRIMARY KEY,
                    welcome_channel INTEGER,
                    welcome_message TEXT,
                    goodbye_channel INTEGER,
                    goodbye_message TEXT,
                    mod_log_channel INTEGER,
                    bot_log_channel INTEGER,
                    automod_enabled BOOLEAN DEFAULT 1,
                    spam_detection BOOLEAN DEFAULT 1,
                    blacklist_enabled BOOLEAN DEFAULT 1,
                    invite_link TEXT
                )
            """)
            
            # Add invite_link column if it doesn't exist (migration)
            try:
                await cursor.execute("""
                    ALTER TABLE guild_settings ADD COLUMN invite_link TEXT
                """)
            except:
                pass  # Column already exists
            
            # Add bot_log_channel column if it doesn't exist (migration)
            try:
                await cursor.execute("""
                    ALTER TABLE guild_settings ADD COLUMN bot_log_channel INTEGER
                """)
            except:
                pass  # Column already exists
            
            # Add everyone_ping_protection column if it doesn't exist (migration)
            try:
                await cursor.execute("""
                    ALTER TABLE guild_settings ADD COLUMN everyone_ping_protection BOOLEAN DEFAULT 1
                """)
            except:
                pass  # Column already exists
            
            # Blacklist table
            await cursor.execute("""
                CREATE TABLE IF NOT EXISTS blacklist (
                    guild_id INTEGER NOT NULL,
                    word TEXT NOT NULL,
                    PRIMARY KEY (guild_id, word)
                )
            """)
            
            # Mutes table
            await cursor.execute("""
                CREATE TABLE IF NOT EXISTS mutes (
                    user_id INTEGER NOT NULL,
                    guild_id INTEGER NOT NULL,
                    unmute_at TIMESTAMP NOT NULL,
                    reason TEXT,
                    PRIMARY KEY (user_id, guild_id)
                )
            """)
            
            # Everyone ping whitelist table
            await cursor.execute("""
                CREATE TABLE IF NOT EXISTS everyone_ping_whitelist (
                    guild_id INTEGER NOT NULL,
                    role_id INTEGER NOT NULL,
                    PRIMARY KEY (guild_id, role_id)
                )
            """)
            
            # KCLAntivirus settings table
            await cursor.execute("""
                CREATE TABLE IF NOT EXISTS antivirus_settings (
                    guild_id INTEGER PRIMARY KEY,
                    enabled BOOLEAN DEFAULT 1,
                    auto_lockdown BOOLEAN DEFAULT 0,
                    mod_log_channel INTEGER,
                    scan_attachments BOOLEAN DEFAULT 1,
                    scan_urls BOOLEAN DEFAULT 1,
                    quarantine_channel INTEGER
                )
            """)
            
            # KCLAntivirus protected roles table
            await cursor.execute("""
                CREATE TABLE IF NOT EXISTS antivirus_protected_roles (
                    guild_id INTEGER NOT NULL,
                    role_id INTEGER NOT NULL,
                    PRIMARY KEY (guild_id, role_id)
                )
            """)
            
            # KCLAntivirus scan logs table
            await cursor.execute("""
                CREATE TABLE IF NOT EXISTS antivirus_scan_logs (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    guild_id INTEGER NOT NULL,
                    user_id INTEGER NOT NULL,
                    item_name TEXT NOT NULL,
                    item_type TEXT NOT NULL,
                    threat_level TEXT NOT NULL,
                    malicious_count INTEGER DEFAULT 0,
                    suspicious_count INTEGER DEFAULT 0,
                    action_taken TEXT,
                    timestamp TIMESTAMP DEFAULT CURRENT_TIMESTAMP
                )
            """)
            
            # Custom media table (for web dashboard)
            await cursor.execute("""
                CREATE TABLE IF NOT EXISTS custom_media (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    name TEXT NOT NULL,
                    filename TEXT,
                    filepath TEXT,
                    url TEXT,
                    guild_id TEXT,
                    uploaded_by TEXT,
                    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
                )
            """)
            
            # Play queue table (for web dashboard integration)
            await cursor.execute("""
                CREATE TABLE IF NOT EXISTS play_queue (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    guild_id TEXT NOT NULL,
                    media_id INTEGER,
                    media_name TEXT NOT NULL,
                    media_path TEXT,
                    media_url TEXT,
                    requested_by TEXT,
                    status TEXT DEFAULT 'pending',
                    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
                )
            """)
            
            await self.connection.commit()
    
    # User operations
    async def get_user(self, user_id: int, guild_id: int) -> Optional[User]:
        """Get user data"""
        async with self.connection.cursor() as cursor:
            await cursor.execute(
                "SELECT * FROM users WHERE user_id = ? AND guild_id = ?",
                (user_id, guild_id)
            )
            row = await cursor.fetchone()
            if row:
                data = dict(row)
                # Convert timestamp strings back to datetime objects
                if data.get('last_daily'):
                    data['last_daily'] = datetime.fromisoformat(data['last_daily'])
                if data.get('last_message'):
                    data['last_message'] = datetime.fromisoformat(data['last_message'])
                return User(**data)
            return None
    
    async def create_user(self, user_id: int, guild_id: int) -> User:
        """Create a new user"""
        async with self.connection.cursor() as cursor:
            await cursor.execute(
                "INSERT INTO users (user_id, guild_id) VALUES (?, ?)",
                (user_id, guild_id)
            )
            await self.connection.commit()
            return User(user_id=user_id, guild_id=guild_id)
    
    async def update_user(self, user: User):
        """Update user data"""
        async with self.connection.cursor() as cursor:
            await cursor.execute("""
                UPDATE users SET xp = ?, level = ?, balance = ?, 
                last_daily = ?, last_message = ?
                WHERE user_id = ? AND guild_id = ?
            """, (user.xp, user.level, user.balance, user.last_daily, 
                  user.last_message, user.user_id, user.guild_id))
            await self.connection.commit()
    
    async def get_or_create_user(self, user_id: int, guild_id: int) -> User:
        """Get user or create if doesn't exist"""
        user = await self.get_user(user_id, guild_id)
        if not user:
            user = await self.create_user(user_id, guild_id)
        return user
    
    # Warning operations
    async def add_warning(self, user_id: int, guild_id: int, moderator_id: int, reason: str) -> int:
        """Add a warning"""
        async with self.connection.cursor() as cursor:
            await cursor.execute("""
                INSERT INTO warnings (user_id, guild_id, moderator_id, reason)
                VALUES (?, ?, ?, ?)
            """, (user_id, guild_id, moderator_id, reason))
            await self.connection.commit()
            return cursor.lastrowid
    
    async def get_warnings(self, user_id: int, guild_id: int) -> List[Warning]:
        """Get all warnings for a user"""
        async with self.connection.cursor() as cursor:
            await cursor.execute("""
                SELECT * FROM warnings 
                WHERE user_id = ? AND guild_id = ?
                ORDER BY timestamp DESC
            """, (user_id, guild_id))
            rows = await cursor.fetchall()
            return [Warning(**dict(row)) for row in rows]
    
    async def remove_warning(self, warning_id: int) -> bool:
        """Remove a specific warning"""
        async with self.connection.cursor() as cursor:
            await cursor.execute("DELETE FROM warnings WHERE id = ?", (warning_id,))
            await self.connection.commit()
            return cursor.rowcount > 0
    
    async def clear_warnings(self, user_id: int, guild_id: int):
        """Clear all warnings for a user"""
        async with self.connection.cursor() as cursor:
            await cursor.execute("""
                DELETE FROM warnings WHERE user_id = ? AND guild_id = ?
            """, (user_id, guild_id))
            await self.connection.commit()
    
    # Moderation log operations
    async def add_mod_log(self, guild_id: int, action_type: str, user_id: int, 
                         moderator_id: int, reason: Optional[str] = None) -> int:
        """Add a moderation log entry"""
        async with self.connection.cursor() as cursor:
            await cursor.execute("""
                INSERT INTO mod_logs (guild_id, action_type, user_id, moderator_id, reason)
                VALUES (?, ?, ?, ?, ?)
            """, (guild_id, action_type, user_id, moderator_id, reason))
            await self.connection.commit()
            return cursor.lastrowid
    
    async def get_mod_logs(self, user_id: int, guild_id: int) -> List[ModLog]:
        """Get moderation logs for a user"""
        async with self.connection.cursor() as cursor:
            await cursor.execute("""
                SELECT * FROM mod_logs 
                WHERE user_id = ? AND guild_id = ?
                ORDER BY timestamp DESC
            """, (user_id, guild_id))
            rows = await cursor.fetchall()
            return [ModLog(**dict(row)) for row in rows]
    
    async def get_mod_log_by_case(self, case_id: int) -> Optional[ModLog]:
        """Get a specific moderation log by case ID"""
        async with self.connection.cursor() as cursor:
            await cursor.execute("SELECT * FROM mod_logs WHERE case_id = ?", (case_id,))
            row = await cursor.fetchone()
            if row:
                return ModLog(**dict(row))
            return None
    
    # Custom command operations
    async def add_custom_command(self, guild_id: int, trigger: str, response: str, created_by: int):
        """Add a custom command"""
        async with self.connection.cursor() as cursor:
            await cursor.execute("""
                INSERT OR REPLACE INTO custom_commands (guild_id, trigger, response, created_by)
                VALUES (?, ?, ?, ?)
            """, (guild_id, trigger.lower(), response, created_by))
            await self.connection.commit()
    
    async def remove_custom_command(self, guild_id: int, trigger: str) -> bool:
        """Remove a custom command"""
        async with self.connection.cursor() as cursor:
            await cursor.execute("""
                DELETE FROM custom_commands WHERE guild_id = ? AND trigger = ?
            """, (guild_id, trigger.lower()))
            await self.connection.commit()
            return cursor.rowcount > 0
    
    async def get_custom_command(self, guild_id: int, trigger: str) -> Optional[CustomCommand]:
        """Get a custom command"""
        async with self.connection.cursor() as cursor:
            await cursor.execute("""
                SELECT * FROM custom_commands WHERE guild_id = ? AND trigger = ?
            """, (guild_id, trigger.lower()))
            row = await cursor.fetchone()
            if row:
                return CustomCommand(**dict(row))
            return None
    
    async def get_all_custom_commands(self, guild_id: int) -> List[CustomCommand]:
        """Get all custom commands for a guild"""
        async with self.connection.cursor() as cursor:
            await cursor.execute("""
                SELECT * FROM custom_commands WHERE guild_id = ?
            """, (guild_id,))
            rows = await cursor.fetchall()
            return [CustomCommand(**dict(row)) for row in rows]
    
    # Guild settings operations
    async def get_guild_settings(self, guild_id: int) -> GuildSettings:
        """Get guild settings"""
        async with self.connection.cursor() as cursor:
            await cursor.execute("""
                SELECT * FROM guild_settings WHERE guild_id = ?
            """, (guild_id,))
            row = await cursor.fetchone()
            if row:
                return GuildSettings(**dict(row))
            # Create default settings
            await cursor.execute("""
                INSERT INTO guild_settings (guild_id) VALUES (?)
            """, (guild_id,))
            await self.connection.commit()
            return GuildSettings(guild_id=guild_id)
    
    async def update_guild_settings(self, settings: GuildSettings):
        """Update guild settings"""
        async with self.connection.cursor() as cursor:
            await cursor.execute("""
                UPDATE guild_settings SET 
                welcome_channel = ?, welcome_message = ?,
                goodbye_channel = ?, goodbye_message = ?,
                mod_log_channel = ?, bot_log_channel = ?,
                automod_enabled = ?,
                spam_detection = ?, blacklist_enabled = ?,
                everyone_ping_protection = ?,
                invite_link = ?
                WHERE guild_id = ?
            """, (settings.welcome_channel, settings.welcome_message,
                  settings.goodbye_channel, settings.goodbye_message,
                  settings.mod_log_channel, settings.bot_log_channel,
                  settings.automod_enabled,
                  settings.spam_detection, settings.blacklist_enabled,
                  settings.everyone_ping_protection,
                  settings.invite_link, settings.guild_id))
            await self.connection.commit()
    
    # Blacklist operations
    async def add_blacklist_word(self, guild_id: int, word: str):
        """Add word to blacklist"""
        async with self.connection.cursor() as cursor:
            await cursor.execute("""
                INSERT OR IGNORE INTO blacklist (guild_id, word) VALUES (?, ?)
            """, (guild_id, word.lower()))
            await self.connection.commit()
    
    async def remove_blacklist_word(self, guild_id: int, word: str) -> bool:
        """Remove word from blacklist"""
        async with self.connection.cursor() as cursor:
            await cursor.execute("""
                DELETE FROM blacklist WHERE guild_id = ? AND word = ?
            """, (guild_id, word.lower()))
            await self.connection.commit()
            return cursor.rowcount > 0
    
    async def get_blacklist(self, guild_id: int) -> List[str]:
        """Get all blacklisted words"""
        async with self.connection.cursor() as cursor:
            await cursor.execute("""
                SELECT word FROM blacklist WHERE guild_id = ?
            """, (guild_id,))
            rows = await cursor.fetchall()
            return [row['word'] for row in rows]
    
    # Mute operations
    async def add_mute(self, user_id: int, guild_id: int, unmute_at: datetime, reason: Optional[str] = None):
        """Add a mute"""
        async with self.connection.cursor() as cursor:
            await cursor.execute("""
                INSERT OR REPLACE INTO mutes (user_id, guild_id, unmute_at, reason)
                VALUES (?, ?, ?, ?)
            """, (user_id, guild_id, unmute_at, reason))
            await self.connection.commit()
    
    async def remove_mute(self, user_id: int, guild_id: int):
        """Remove a mute"""
        async with self.connection.cursor() as cursor:
            await cursor.execute("""
                DELETE FROM mutes WHERE user_id = ? AND guild_id = ?
            """, (user_id, guild_id))
            await self.connection.commit()
    
    async def get_expired_mutes(self) -> List[Mute]:
        """Get all expired mutes"""
        async with self.connection.cursor() as cursor:
            await cursor.execute("""
                SELECT * FROM mutes WHERE unmute_at <= datetime('now')
            """)
            rows = await cursor.fetchall()
            return [Mute(**dict(row)) for row in rows]
    
    # Leaderboard operations
    async def get_top_users_by_balance(self, guild_id: int, limit: int = 10) -> List[User]:
        """Get top users by balance"""
        async with self.connection.cursor() as cursor:
            await cursor.execute("""
                SELECT * FROM users WHERE guild_id = ?
                ORDER BY balance DESC LIMIT ?
            """, (guild_id, limit))
            rows = await cursor.fetchall()
            return [User(**dict(row)) for row in rows]
    
    async def get_top_users_by_level(self, guild_id: int, limit: int = 10) -> List[User]:
        """Get top users by level"""
        async with self.connection.cursor() as cursor:
            await cursor.execute("""
                SELECT * FROM users WHERE guild_id = ?
                ORDER BY level DESC, xp DESC LIMIT ?
            """, (guild_id, limit))
            rows = await cursor.fetchall()
            return [User(**dict(row)) for row in rows]
    
    # YouTube subscription operations
    async def add_youtube_sub(self, guild_id: int, channel_id: str, notification_channel: int):
        """Add YouTube subscription"""
        async with self.connection.cursor() as cursor:
            await cursor.execute("""
                INSERT OR REPLACE INTO youtube_subs (guild_id, channel_id, notification_channel)
                VALUES (?, ?, ?)
            """, (guild_id, channel_id, notification_channel))
            await self.connection.commit()
    
    async def remove_youtube_sub(self, guild_id: int, channel_id: str) -> bool:
        """Remove YouTube subscription"""
        async with self.connection.cursor() as cursor:
            await cursor.execute("""
                DELETE FROM youtube_subs WHERE guild_id = ? AND channel_id = ?
            """, (guild_id, channel_id))
            await self.connection.commit()
            return cursor.rowcount > 0
    
    async def get_youtube_subs(self, guild_id: int) -> List[YouTubeSub]:
        """Get all YouTube subscriptions for a guild"""
        async with self.connection.cursor() as cursor:
            await cursor.execute("""
                SELECT * FROM youtube_subs WHERE guild_id = ?
            """, (guild_id,))
            rows = await cursor.fetchall()
            return [YouTubeSub(**dict(row)) for row in rows]
    
    async def get_all_youtube_subs(self) -> List[YouTubeSub]:
        """Get all YouTube subscriptions"""
        async with self.connection.cursor() as cursor:
            await cursor.execute("SELECT * FROM youtube_subs")
            rows = await cursor.fetchall()
            return [YouTubeSub(**dict(row)) for row in rows]
    
    async def update_youtube_last_video(self, guild_id: int, channel_id: str, video_id: str):
        """Update last video ID for YouTube subscription"""
        async with self.connection.cursor() as cursor:
            await cursor.execute("""
                UPDATE youtube_subs SET last_video_id = ?
                WHERE guild_id = ? AND channel_id = ?
            """, (video_id, guild_id, channel_id))
            await self.connection.commit()
    
    # Custom media operations
    async def add_custom_media(self, name: str, filename: str = None, filepath: str = None, 
                              url: str = None, guild_id: str = None, uploaded_by: str = None):
        """Add custom media item"""
        async with self.connection.cursor() as cursor:
            await cursor.execute("""
                INSERT INTO custom_media (name, filename, filepath, url, guild_id, uploaded_by)
                VALUES (?, ?, ?, ?, ?, ?)
            """, (name, filename, filepath, url, guild_id, uploaded_by))
            await self.connection.commit()
            return cursor.lastrowid
    
    async def get_custom_media(self, name: str, guild_id: str = None):
        """Get custom media by name"""
        async with self.connection.cursor() as cursor:
            if guild_id:
                await cursor.execute("""
                    SELECT * FROM custom_media 
                    WHERE name = ? AND (guild_id = ? OR guild_id IS NULL)
                    ORDER BY guild_id DESC LIMIT 1
                """, (name.lower(), guild_id))
            else:
                await cursor.execute("""
                    SELECT * FROM custom_media WHERE name = ? LIMIT 1
                """, (name.lower(),))
            return await cursor.fetchone()
    
    async def get_all_custom_media(self, guild_id: str = None):
        """Get all custom media for a guild"""
        async with self.connection.cursor() as cursor:
            if guild_id:
                await cursor.execute("""
                    SELECT * FROM custom_media 
                    WHERE guild_id = ? OR guild_id IS NULL
                    ORDER BY created_at DESC
                """, (guild_id,))
            else:
                await cursor.execute("""
                    SELECT * FROM custom_media ORDER BY created_at DESC
                """)
            return await cursor.fetchall()
    
    async def delete_custom_media(self, media_id: int):
        """Delete custom media item"""
        async with self.connection.cursor() as cursor:
            await cursor.execute("DELETE FROM custom_media WHERE id = ?", (media_id,))
            await self.connection.commit()
            return cursor.rowcount > 0
    
    # Play queue operations
    async def add_play_request(self, guild_id: str, media_name: str, media_id: int = None,
                              media_path: str = None, media_url: str = None, requested_by: str = None):
        """Add play request to queue"""
        async with self.connection.cursor() as cursor:
            await cursor.execute("""
                INSERT INTO play_queue (guild_id, media_id, media_name, media_path, media_url, requested_by)
                VALUES (?, ?, ?, ?, ?, ?)
            """, (guild_id, media_id, media_name, media_path, media_url, requested_by))
            await self.connection.commit()
            return cursor.lastrowid
    
    async def get_pending_play_requests(self):
        """Get all pending play requests"""
        async with self.connection.cursor() as cursor:
            await cursor.execute("""
                SELECT * FROM play_queue 
                WHERE status = 'pending' 
                ORDER BY created_at ASC
            """)
            return await cursor.fetchall()
    
    async def update_play_request_status(self, request_id: int, status: str):
        """Update play request status"""
        async with self.connection.cursor() as cursor:
            await cursor.execute("""
                UPDATE play_queue SET status = ? WHERE id = ?
            """, (status, request_id))
            await self.connection.commit()
    
    async def cleanup_old_play_requests(self, hours: int = 24):
        """Clean up old play requests"""
        async with self.connection.cursor() as cursor:
            await cursor.execute("""
                DELETE FROM play_queue 
                WHERE created_at < datetime('now', '-{} hours')
            """.format(hours))
            await self.connection.commit()
    
    # Everyone ping whitelist operations
    async def add_everyone_ping_whitelist(self, guild_id: int, role_id: int) -> bool:
        """Add role to everyone ping whitelist"""
        async with self.connection.cursor() as cursor:
            try:
                await cursor.execute("""
                    INSERT INTO everyone_ping_whitelist (guild_id, role_id) VALUES (?, ?)
                """, (guild_id, role_id))
                await self.connection.commit()
                return True
            except:
                return False  # Role already exists
    
    async def remove_everyone_ping_whitelist(self, guild_id: int, role_id: int) -> bool:
        """Remove role from everyone ping whitelist"""
        async with self.connection.cursor() as cursor:
            await cursor.execute("""
                DELETE FROM everyone_ping_whitelist WHERE guild_id = ? AND role_id = ?
            """, (guild_id, role_id))
            await self.connection.commit()
            return cursor.rowcount > 0
    
    async def get_everyone_ping_whitelist(self, guild_id: int) -> List[int]:
        """Get all whitelisted role IDs for everyone pings"""
        async with self.connection.cursor() as cursor:
            await cursor.execute("""
                SELECT role_id FROM everyone_ping_whitelist WHERE guild_id = ?
            """, (guild_id,))
            rows = await cursor.fetchall()
            return [row['role_id'] for row in rows]
    
    async def clear_everyone_ping_whitelist(self, guild_id: int) -> int:
        """Clear all roles from everyone ping whitelist"""
        async with self.connection.cursor() as cursor:
            await cursor.execute("""
                DELETE FROM everyone_ping_whitelist WHERE guild_id = ?
            """, (guild_id,))
            await self.connection.commit()
            return cursor.rowcount
    
    # KCLAntivirus operations
    async def get_antivirus_settings(self, guild_id: int) -> AntivirusSettings:
        """Get antivirus settings for a guild"""
        async with self.connection.cursor() as cursor:
            await cursor.execute("""
                SELECT * FROM antivirus_settings WHERE guild_id = ?
            """, (guild_id,))
            row = await cursor.fetchone()
            if row:
                return AntivirusSettings(**dict(row))
            # Create default settings
            await cursor.execute("""
                INSERT INTO antivirus_settings (guild_id) VALUES (?)
            """, (guild_id,))
            await self.connection.commit()
            return AntivirusSettings(guild_id=guild_id)
    
    async def update_antivirus_settings(self, settings: AntivirusSettings):
        """Update antivirus settings"""
        async with self.connection.cursor() as cursor:
            await cursor.execute("""
                UPDATE antivirus_settings SET 
                enabled = ?, auto_lockdown = ?, mod_log_channel = ?,
                scan_attachments = ?, scan_urls = ?, quarantine_channel = ?
                WHERE guild_id = ?
            """, (settings.enabled, settings.auto_lockdown, settings.mod_log_channel,
                  settings.scan_attachments, settings.scan_urls, settings.quarantine_channel,
                  settings.guild_id))
            await self.connection.commit()
    
    async def add_antivirus_protected_role(self, guild_id: int, role_id: int) -> bool:
        """Add role to antivirus protection"""
        async with self.connection.cursor() as cursor:
            try:
                await cursor.execute("""
                    INSERT INTO antivirus_protected_roles (guild_id, role_id) VALUES (?, ?)
                """, (guild_id, role_id))
                await self.connection.commit()
                return True
            except:
                return False  # Role already exists
    
    async def remove_antivirus_protected_role(self, guild_id: int, role_id: int) -> bool:
        """Remove role from antivirus protection"""
        async with self.connection.cursor() as cursor:
            await cursor.execute("""
                DELETE FROM antivirus_protected_roles WHERE guild_id = ? AND role_id = ?
            """, (guild_id, role_id))
            await self.connection.commit()
            return cursor.rowcount > 0
    
    async def get_antivirus_protected_roles(self, guild_id: int) -> List[int]:
        """Get all protected role IDs for antivirus"""
        async with self.connection.cursor() as cursor:
            await cursor.execute("""
                SELECT role_id FROM antivirus_protected_roles WHERE guild_id = ?
            """, (guild_id,))
            rows = await cursor.fetchall()
            return [row['role_id'] for row in rows]
    
    async def clear_antivirus_protected_roles(self, guild_id: int) -> int:
        """Clear all roles from antivirus protection"""
        async with self.connection.cursor() as cursor:
            await cursor.execute("""
                DELETE FROM antivirus_protected_roles WHERE guild_id = ?
            """, (guild_id,))
            await self.connection.commit()
            return cursor.rowcount
    
    async def add_antivirus_scan_log(self, guild_id: int, user_id: int, item_name: str, 
                                   item_type: str, threat_level: str, malicious_count: int = 0,
                                   suspicious_count: int = 0, action_taken: str = None) -> int:
        """Add antivirus scan log entry"""
        async with self.connection.cursor() as cursor:
            await cursor.execute("""
                INSERT INTO antivirus_scan_logs 
                (guild_id, user_id, item_name, item_type, threat_level, malicious_count, suspicious_count, action_taken)
                VALUES (?, ?, ?, ?, ?, ?, ?, ?)
            """, (guild_id, user_id, item_name, item_type, threat_level, malicious_count, suspicious_count, action_taken))
            await self.connection.commit()
            return cursor.lastrowid
    
    async def get_antivirus_scan_logs(self, guild_id: int, limit: int = 50) -> List[Dict[str, Any]]:
        """Get recent antivirus scan logs"""
        async with self.connection.cursor() as cursor:
            await cursor.execute("""
                SELECT * FROM antivirus_scan_logs 
                WHERE guild_id = ?
                ORDER BY timestamp DESC
                LIMIT ?
            """, (guild_id, limit))
            rows = await cursor.fetchall()
            return [dict(row) for row in rows]
    
    async def close(self):
        """Close database connection"""
        if self.connection:
            await self.connection.close()
            logger.info("Database connection closed")
