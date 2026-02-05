"""
Configuration module for Discord bot
Loads environment variables and provides configuration constants
"""
import os
from dotenv import load_dotenv

# Load environment variables from .env file
load_dotenv()

# Discord Configuration
DISCORD_TOKEN = os.getenv('DISCORD_TOKEN')
PREFIX = os.getenv('PREFIX', '-')

# API Keys
# YOUTUBE_API_KEY = os.getenv('YOUTUBE_API_KEY')  # Removed - YouTube functionality disabled
VIRUSTOTAL_API_KEY = os.getenv('VIRUSTOTAL_API_KEY')

# Database Configuration
DATABASE_PATH = os.getenv('DATABASE_PATH', './data/bot.db')

# External APIs
# BLOXFRUITS_API_URL = os.getenv('BLOXFRUITS_API_URL', 'https://api.blox-fruits.com/stock')  # Removed - Blox Fruits functionality disabled

# Bot Settings
BOT_NAME = "Discord Bot"
BOT_VERSION = "1.0.0"
BOT_DESCRIPTION = "A comprehensive Discord bot with 100+ commands"

# Colors for embeds (hex values)
class Colors:
    PRIMARY = 0x5865F2
    SUCCESS = 0x57F287
    WARNING = 0xFEE75C
    ERROR = 0xED4245
    INFO = 0x5865F2
    MODERATION = 0xED4245

# Emojis
class Emojis:
    SUCCESS = "✅"
    ERROR = "❌"
    WARNING = "⚠️"
    INFO = "ℹ️"
    LOADING = "⏳"
    MUSIC = "🎵"
    MONEY = "💰"
    LEVEL_UP = "⬆️"

# Economy Settings
class Economy:
    DAILY_REWARD = 500
    WEEKLY_REWARD = 3500
    WORK_MIN = 100
    WORK_MAX = 500
    BEG_MIN = 10
    BEG_MAX = 100
    ROB_SUCCESS_RATE = 0.4
    ROB_MIN_PERCENT = 0.1
    ROB_MAX_PERCENT = 0.3

# Leveling Settings
class Leveling:
    XP_PER_MESSAGE_MIN = 15
    XP_PER_MESSAGE_MAX = 25
    XP_COOLDOWN = 60  # seconds
    
    @staticmethod
    def calculate_level(xp: int) -> int:
        """Calculate level from XP using formula: level = floor(0.1 * sqrt(xp))"""
        return int(0.1 * (xp ** 0.5))
    
    @staticmethod
    def calculate_xp_for_level(level: int) -> int:
        """Calculate XP required for a specific level"""
        return (level * 10) ** 2

# Auto-moderation Settings
class AutoMod:
    SPAM_MESSAGE_COUNT = 5
    SPAM_TIME_WINDOW = 3  # seconds
    CAPS_THRESHOLD = 0.7  # 70% caps
    MAX_MENTIONS = 5

# KCLAntivirus Settings
class KCLAntivirus:
    # VirusTotal scan thresholds
    MALICIOUS_THRESHOLD = 1  # Number of engines that must detect as malicious
    SUSPICIOUS_THRESHOLD = 3  # Number of engines that must detect as suspicious
    
    # Timeout durations (in days)
    VIRUS_TIMEOUT_DAYS = 1
    RAID_TIMEOUT_DAYS = 7
    
    # File size limits (in MB)
    MAX_FILE_SIZE_MB = 32  # VirusTotal free API limit
    
    # Scan cooldowns (in seconds)
    USER_SCAN_COOLDOWN = 300  # 5 minutes between user scans
    SERVER_SCAN_COOLDOWN = 3600  # 1 hour between server scans
    
    # Raid detection settings
    RAID_USER_JOIN_THRESHOLD = 10  # Users joining in time window
    RAID_TIME_WINDOW = 60  # seconds
    RAID_MESSAGE_THRESHOLD = 20  # Messages in time window
    
    # Protected file extensions (won't be scanned)
    SAFE_EXTENSIONS = ['.txt', '.md', '.json', '.yml', '.yaml', '.log']
    
    # Dangerous file extensions (always flagged)
    DANGEROUS_EXTENSIONS = ['.exe', '.scr', '.bat', '.cmd', '.com', '.pif', '.vbs', '.js']

# Validation
def validate_config():
    """Validate that required configuration is present"""
    if not DISCORD_TOKEN:
        raise ValueError("DISCORD_TOKEN is not set in environment variables")
    
    # Create data directory if it doesn't exist
    os.makedirs(os.path.dirname(DATABASE_PATH), exist_ok=True)
    
    return True
