#!/usr/bin/env python3
"""
Test script for KCLAntivirus functionality
This script helps verify that the KCLAntivirus system is working correctly
"""

import asyncio
import os
from database.db_manager import DatabaseManager
from database.models import AntivirusSettings

async def test_antivirus_database():
    """Test the KCLAntivirus database setup"""
    print("🧪 Testing KCLAntivirus Database Setup...")
    
    # Initialize database
    db = DatabaseManager('./data/test_antivirus.db')
    await db.initialize()
    
    # Test guild ID
    test_guild_id = 123456789
    test_role_id = 987654321
    
    print(f"📊 Testing antivirus settings for guild {test_guild_id}...")
    
    # Test antivirus settings
    settings = await db.get_antivirus_settings(test_guild_id)
    print(f"✅ Retrieved settings: enabled={settings.enabled}, auto_lockdown={settings.auto_lockdown}")
    
    # Update settings
    settings.enabled = True
    settings.auto_lockdown = True
    settings.mod_log_channel = 123456
    await db.update_antivirus_settings(settings)
    print("✅ Updated antivirus settings")
    
    # Verify update
    updated_settings = await db.get_antivirus_settings(test_guild_id)
    print(f"✅ Verified: enabled={updated_settings.enabled}, auto_lockdown={updated_settings.auto_lockdown}, log_channel={updated_settings.mod_log_channel}")
    
    # Test protected roles
    print(f"\n🛡️ Testing protected roles functionality...")
    
    # Add protected role
    success = await db.add_antivirus_protected_role(test_guild_id, test_role_id)
    print(f"✅ Added protected role {test_role_id}: {success}")
    
    # Get protected roles
    protected_roles = await db.get_antivirus_protected_roles(test_guild_id)
    print(f"✅ Retrieved protected roles: {protected_roles}")
    
    # Add another role
    test_role_id_2 = 987654322
    await db.add_antivirus_protected_role(test_guild_id, test_role_id_2)
    protected_roles = await db.get_antivirus_protected_roles(test_guild_id)
    print(f"✅ Protected roles with 2 entries: {protected_roles}")
    
    # Remove one role
    success = await db.remove_antivirus_protected_role(test_guild_id, test_role_id)
    print(f"✅ Removed role {test_role_id}: {success}")
    
    # Test scan logging
    print(f"\n📝 Testing scan log functionality...")
    
    log_id = await db.add_antivirus_scan_log(
        test_guild_id, 
        123456, 
        "test_file.exe", 
        "file", 
        "MALICIOUS", 
        5, 
        2, 
        "Message deleted, user timed out"
    )
    print(f"✅ Added scan log entry with ID: {log_id}")
    
    # Get scan logs
    logs = await db.get_antivirus_scan_logs(test_guild_id, 10)
    print(f"✅ Retrieved {len(logs)} scan log entries")
    if logs:
        print(f"   Latest log: {logs[0]['item_name']} - {logs[0]['threat_level']}")
    
    # Clear protected roles
    count = await db.clear_antivirus_protected_roles(test_guild_id)
    print(f"✅ Cleared {count} protected roles")
    
    await db.close()
    print("🎉 KCLAntivirus database test completed successfully!")

def test_configuration():
    """Test configuration and environment setup"""
    print("\n🔧 Testing Configuration...")
    
    # Check if VirusTotal API key is configured
    from config import VIRUSTOTAL_API_KEY
    
    if VIRUSTOTAL_API_KEY:
        print("✅ VirusTotal API key is configured")
        # Don't print the actual key for security
        print(f"   Key length: {len(VIRUSTOTAL_API_KEY)} characters")
    else:
        print("⚠️  VirusTotal API key not configured")
        print("   Add VIRUSTOTAL_API_KEY to your .env file")
    
    # Check KCLAntivirus config
    from config import KCLAntivirus
    
    print(f"✅ Malicious threshold: {KCLAntivirus.MALICIOUS_THRESHOLD}")
    print(f"✅ Suspicious threshold: {KCLAntivirus.SUSPICIOUS_THRESHOLD}")
    print(f"✅ Virus timeout: {KCLAntivirus.VIRUS_TIMEOUT_DAYS} days")
    print(f"✅ Raid join threshold: {KCLAntivirus.RAID_USER_JOIN_THRESHOLD}")
    print(f"✅ Raid time window: {KCLAntivirus.RAID_TIME_WINDOW} seconds")
    print(f"✅ Max file size: {KCLAntivirus.MAX_FILE_SIZE_MB} MB")
    
    print("🎉 Configuration test completed!")

def test_file_extension_detection():
    """Test file extension detection logic"""
    print("\n📁 Testing File Extension Detection...")
    
    from config import KCLAntivirus
    
    test_files = [
        ("document.txt", "SAFE", "Should be skipped"),
        ("config.json", "SAFE", "Should be skipped"),
        ("virus.exe", "DANGEROUS", "Should be auto-flagged"),
        ("script.bat", "DANGEROUS", "Should be auto-flagged"),
        ("image.jpg", "SCAN", "Should be scanned"),
        ("archive.zip", "SCAN", "Should be scanned"),
        ("readme.md", "SAFE", "Should be skipped"),
        ("malware.scr", "DANGEROUS", "Should be auto-flagged"),
    ]
    
    for filename, expected, description in test_files:
        file_ext = f".{filename.split('.')[-1].lower()}"
        
        if file_ext in KCLAntivirus.SAFE_EXTENSIONS:
            result = "SAFE"
        elif file_ext in KCLAntivirus.DANGEROUS_EXTENSIONS:
            result = "DANGEROUS"
        else:
            result = "SCAN"
        
        status = "✅ PASS" if result == expected else "❌ FAIL"
        print(f"{status} - {filename}: {result} ({description})")
    
    print("🎉 File extension detection test completed!")

def test_url_pattern_detection():
    """Test URL pattern detection"""
    print("\n🔗 Testing URL Pattern Detection...")
    
    import re
    
    # URL regex pattern from the cog
    url_pattern = re.compile(
        r'http[s]?://(?:[a-zA-Z]|[0-9]|[$-_@.&+]|[!*\\(\\),]|(?:%[0-9a-fA-F][0-9a-fA-F]))+'
    )
    
    test_messages = [
        ("Check out https://example.com", True, "Should detect HTTPS URL"),
        ("Visit http://test.org for more info", True, "Should detect HTTP URL"),
        ("No links in this message", False, "Should not detect any URLs"),
        ("Multiple links: https://site1.com and http://site2.net", True, "Should detect multiple URLs"),
        ("Malicious link: https://malware-site.evil/payload", True, "Should detect suspicious URL"),
        ("Just text with www.example.com", False, "Should not detect www without protocol"),
        ("ftp://files.example.com", False, "Should not detect FTP URLs"),
    ]
    
    for message, should_detect, description in test_messages:
        urls = url_pattern.findall(message)
        detected = len(urls) > 0
        
        status = "✅ PASS" if detected == should_detect else "❌ FAIL"
        print(f"{status} - {description}")
        print(f"   Message: '{message}'")
        print(f"   URLs found: {urls if urls else 'None'}")
    
    print("🎉 URL pattern detection test completed!")

async def main():
    """Run all tests"""
    print("🚀 Starting KCLAntivirus System Tests...\n")
    
    # Test database functionality
    await test_antivirus_database()
    
    # Test configuration
    test_configuration()
    
    # Test file extension detection
    test_file_extension_detection()
    
    # Test URL pattern detection
    test_url_pattern_detection()
    
    print("\n✨ All KCLAntivirus tests completed!")
    print("\n📋 Next steps:")
    print("1. Add VIRUSTOTAL_API_KEY to your .env file")
    print("2. Start your bot: python bot.py")
    print("3. Enable the system: /antivirus-setup enabled:True")
    print("4. Set up protected roles: /antivirus-protected-roles action:add role:@Staff")
    print("5. Test with a harmless file upload")
    
    # Cleanup test database
    try:
        os.remove('./data/test_antivirus.db')
        print("\n🧹 Cleaned up test database")
    except:
        pass

if __name__ == "__main__":
    asyncio.run(main())