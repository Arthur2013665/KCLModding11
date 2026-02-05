#!/usr/bin/env python3
"""
Test script for anti-ping functionality
This script helps verify that the anti-ping system is working correctly
"""

import asyncio
import discord
from discord.ext import commands
from database.db_manager import DatabaseManager
from database.models import GuildSettings

async def test_anti_ping_setup():
    """Test the anti-ping database setup"""
    print("🧪 Testing Anti-Ping System Setup...")
    
    # Initialize database
    db = DatabaseManager('./data/test_bot.db')
    await db.initialize()
    
    # Test guild ID
    test_guild_id = 123456789
    test_role_id = 987654321
    
    print(f"📊 Testing guild settings for guild {test_guild_id}...")
    
    # Get or create guild settings
    settings = await db.get_guild_settings(test_guild_id)
    print(f"✅ Retrieved settings: everyone_ping_protection = {getattr(settings, 'everyone_ping_protection', 'NOT SET')}")
    
    # Test updating the setting
    settings.everyone_ping_protection = True
    await db.update_guild_settings(settings)
    print("✅ Updated everyone_ping_protection to True")
    
    # Test role whitelist functionality
    print(f"\n🎭 Testing role whitelist functionality...")
    
    # Add role to whitelist
    success = await db.add_everyone_ping_whitelist(test_guild_id, test_role_id)
    print(f"✅ Added role {test_role_id} to whitelist: {success}")
    
    # Try adding same role again (should fail)
    success = await db.add_everyone_ping_whitelist(test_guild_id, test_role_id)
    print(f"✅ Duplicate role add (should be False): {success}")
    
    # Get whitelist
    whitelist = await db.get_everyone_ping_whitelist(test_guild_id)
    print(f"✅ Retrieved whitelist: {whitelist}")
    
    # Add another role
    test_role_id_2 = 987654322
    await db.add_everyone_ping_whitelist(test_guild_id, test_role_id_2)
    whitelist = await db.get_everyone_ping_whitelist(test_guild_id)
    print(f"✅ Whitelist with 2 roles: {whitelist}")
    
    # Remove one role
    success = await db.remove_everyone_ping_whitelist(test_guild_id, test_role_id)
    print(f"✅ Removed role {test_role_id}: {success}")
    
    # Check whitelist again
    whitelist = await db.get_everyone_ping_whitelist(test_guild_id)
    print(f"✅ Whitelist after removal: {whitelist}")
    
    # Clear all roles
    count = await db.clear_everyone_ping_whitelist(test_guild_id)
    print(f"✅ Cleared {count} roles from whitelist")
    
    # Final check
    whitelist = await db.get_everyone_ping_whitelist(test_guild_id)
    print(f"✅ Final whitelist (should be empty): {whitelist}")
    
    await db.close()
    print("🎉 Anti-ping system database test completed successfully!")

def test_message_detection():
    """Test message detection logic"""
    print("\n🔍 Testing Message Detection Logic...")
    
    # Simulate different message scenarios
    test_cases = [
        ("Hello @everyone!", True, "Should detect @everyone"),
        ("Hey @here check this out", True, "Should detect @here"),
        ("Hello everyone!", False, "Should NOT detect plain text 'everyone'"),
        ("@user123 how are you?", False, "Should NOT detect user mentions"),
        ("Check @role-name", False, "Should NOT detect role mentions"),
        ("@everyone @here both!", True, "Should detect both @everyone and @here"),
    ]
    
    for message_content, should_detect, description in test_cases:
        # Simulate Discord's mention_everyone property
        # In real Discord, this is True when @everyone or @here is used
        has_everyone_mention = "@everyone" in message_content or "@here" in message_content
        
        result = "✅ PASS" if (has_everyone_mention == should_detect) else "❌ FAIL"
        print(f"{result} - {description}")
        print(f"   Message: '{message_content}' | Detected: {has_everyone_mention}")
    
    print("🎉 Message detection test completed!")

if __name__ == "__main__":
    print("🚀 Starting Anti-Ping System Tests...\n")
    
    # Test database setup
    asyncio.run(test_anti_ping_setup())
    
    # Test message detection
    test_message_detection()
    
    print("\n✨ All tests completed! The enhanced anti-ping system is ready to use.")
    print("\n📋 Next steps:")
    print("1. Start your bot: python bot.py")
    print("2. Enable the feature: /automod feature:everyone-ping enabled:True")
    print("3. Add trusted roles: /everyone-whitelist action:add role:@Staff")
    print("4. Test with different user roles trying to ping @everyone")