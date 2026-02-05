#!/usr/bin/env python3
"""
Test script to verify giveaway cog can be loaded
"""
import sys
import asyncio

async def test_giveaway():
    """Test if giveaway cog loads properly"""
    
    print("🧪 Testing Giveaway Cog")
    print("=" * 40)
    
    try:
        # Test imports
        print("1. Testing imports...")
        import discord
        from discord.ext import commands
        print("   ✅ Discord imports OK")
        
        # Test config
        print("2. Testing config...")
        import config
        print("   ✅ Config OK")
        
        # Test database
        print("3. Testing database...")
        from database.db_manager import DatabaseManager
        db = DatabaseManager(config.DATABASE_PATH)
        await db.initialize()
        print("   ✅ Database OK")
        
        # Test giveaway cog import
        print("4. Testing giveaway cog import...")
        from cogs.giveaway import Giveaway
        print("   ✅ Giveaway cog imports OK")
        
        # Create minimal bot
        print("5. Creating test bot...")
        intents = discord.Intents.default()
        intents.message_content = True
        bot = commands.Bot(command_prefix="!", intents=intents)
        bot.db = db
        print("   ✅ Bot created")
        
        # Try to add cog
        print("6. Adding giveaway cog...")
        await bot.add_cog(Giveaway(bot))
        print("   ✅ Giveaway cog added successfully")
        
        # Check commands
        print("7. Checking commands...")
        commands_list = [cmd.name for cmd in bot.tree.get_commands()]
        print(f"   Found {len(commands_list)} commands:")
        for cmd in commands_list:
            print(f"   - {cmd}")
        
        # Cleanup
        await db.close()
        
        print()
        print("🎉 All tests passed!")
        print()
        print("The giveaway cog is working correctly.")
        print("To see commands in Discord:")
        print("1. Start the bot: ./start.sh")
        print("2. Wait for 'Commands synced' message")
        print("3. Type / in Discord to see commands")
        print()
        
        return True
        
    except Exception as e:
        print(f"\n❌ Error: {e}")
        import traceback
        traceback.print_exc()
        return False

if __name__ == "__main__":
    result = asyncio.run(test_giveaway())
    sys.exit(0 if result else 1)
