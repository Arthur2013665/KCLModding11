#!/usr/bin/env python3
"""
Database migration script
Adds missing tables for web dashboard integration
"""
import sqlite3
import os
from datetime import datetime

def migrate_database():
    """Add missing tables to existing database"""
    
    # Database path
    db_path = './data/bot.db'
    
    if not os.path.exists(db_path):
        print("❌ Database not found at ./data/bot.db")
        print("The database will be created when you start the bot.")
        return
    
    print("🔄 Migrating database...")
    
    # Connect to database
    conn = sqlite3.connect(db_path)
    cursor = conn.cursor()
    
    try:
        # Check if tables already exist
        cursor.execute("SELECT name FROM sqlite_master WHERE type='table' AND name='custom_media'")
        custom_media_exists = cursor.fetchone() is not None
        
        cursor.execute("SELECT name FROM sqlite_master WHERE type='table' AND name='play_queue'")
        play_queue_exists = cursor.fetchone() is not None
        
        # Create custom_media table if it doesn't exist
        if not custom_media_exists:
            print("📁 Creating custom_media table...")
            cursor.execute("""
                CREATE TABLE custom_media (
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
            print("✅ custom_media table created")
        else:
            print("✅ custom_media table already exists")
        
        # Create play_queue table if it doesn't exist
        if not play_queue_exists:
            print("🎵 Creating play_queue table...")
            cursor.execute("""
                CREATE TABLE play_queue (
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
            print("✅ play_queue table created")
        else:
            print("✅ play_queue table already exists")
        
        # Commit changes
        conn.commit()
        
        # Show table info
        cursor.execute("SELECT name FROM sqlite_master WHERE type='table'")
        tables = cursor.fetchall()
        
        print(f"\n📊 Database now has {len(tables)} tables:")
        for table in tables:
            cursor.execute(f"SELECT COUNT(*) FROM {table[0]}")
            count = cursor.fetchone()[0]
            print(f"  - {table[0]}: {count} records")
        
        print("\n🎉 Database migration completed successfully!")
        
    except Exception as e:
        print(f"❌ Migration failed: {e}")
        conn.rollback()
    
    finally:
        conn.close()

if __name__ == "__main__":
    migrate_database()