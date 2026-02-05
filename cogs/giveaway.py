"""
Giveaway system cog
Allows creating, managing, and ending giveaways
"""
import discord
from discord import app_commands
from discord.ext import commands, tasks
import asyncio
from datetime import datetime, timedelta
import random
import logging

from utils.embeds import success_embed, info_embed, error_embed
import config

logger = logging.getLogger('discord_bot.giveaway')

class Giveaway(commands.Cog):
    """Giveaway commands"""
    
    def __init__(self, bot):
        self.bot = bot
        self.check_giveaways.start()
    
    def cog_unload(self):
        self.check_giveaways.cancel()
    
    @app_commands.command(name="gstart", description="Start a new giveaway")
    @app_commands.describe(
        prize="What are you giving away?",
        duration="Duration (e.g., 1h, 30m, 1d)",
        requirements="Requirements to enter (e.g., 'Must have 10+ invites')",
        winners="Number of winners (default: 1)",
        min_level="Minimum level required to enter (optional)",
        channel="Channel to post giveaway (optional)"
    )
    @app_commands.checks.has_permissions(manage_guild=True)
    async def gstart(
        self, 
        interaction: discord.Interaction, 
        prize: str,
        duration: str,
        requirements: str,
        winners: int = 1,
        min_level: int = None,
        channel: discord.TextChannel = None
    ):
        """Start a new giveaway"""
        
        # Parse duration
        try:
            time_value, time_unit = self._parse_duration(duration)
            if time_unit == 's':
                end_time = datetime.utcnow() + timedelta(seconds=time_value)
            elif time_unit == 'm':
                end_time = datetime.utcnow() + timedelta(minutes=time_value)
            elif time_unit == 'h':
                end_time = datetime.utcnow() + timedelta(hours=time_value)
            elif time_unit == 'd':
                end_time = datetime.utcnow() + timedelta(days=time_value)
            else:
                raise ValueError("Invalid time unit")
        except:
            await interaction.response.send_message(
                "❌ Invalid duration format! Use: 30s, 5m, 2h, or 1d",
                ephemeral=True
            )
            return
        
        # Validate winners
        if winners < 1 or winners > 20:
            await interaction.response.send_message(
                "❌ Number of winners must be between 1 and 20!",
                ephemeral=True
            )
            return
        
        # Use current channel if not specified
        target_channel = channel or interaction.channel
        
        # Build requirements display
        requirements_display = requirements
        if min_level:
            requirements_display += f"\n• Must be level {min_level} or higher"
        
        # Create giveaway embed
        embed = discord.Embed(
            title="🎉 GIVEAWAY 🎉",
            description=f"**Prize:** {prize}\n\n"
                       f"**Winners:** {winners}\n"
                       f"**Ends:** <t:{int(end_time.timestamp())}:R> (<t:{int(end_time.timestamp())}:f>)\n\n"
                       f"React with 🎉 to enter!",
            color=config.Colors.PRIMARY
        )
        embed.set_footer(text=f"Giveaway ends")
        embed.add_field(name="Hosted by", value=interaction.user.mention, inline=False)
        embed.add_field(name="📋 Requirements", value=requirements_display, inline=False)
        
        # Post giveaway
        await interaction.response.defer()
        giveaway_msg = await target_channel.send(embed=embed)
        await giveaway_msg.add_reaction("🎉")
        
        # Store in database
        await self.bot.db.connection.execute(
            """INSERT INTO giveaways 
               (message_id, channel_id, guild_id, prize, winners, end_time, host_id, active, requirements, min_level)
               VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?)""",
            (giveaway_msg.id, target_channel.id, interaction.guild.id, 
             prize, winners, end_time, interaction.user.id, True, requirements, min_level)
        )
        await self.bot.db.connection.commit()
        
        # Confirm
        await interaction.followup.send(
            embed=success_embed(
                "Giveaway Started!",
                f"Giveaway posted in {target_channel.mention}\n"
                f"Prize: **{prize}**\n"
                f"Duration: **{duration}**\n"
                f"Winners: **{winners}**\n"
                f"Requirements: **{requirements}**" +
                (f"\nMin Level: **{min_level}**" if min_level else "")
            )
        )
        
        logger.info(f"Giveaway started by {interaction.user} in {interaction.guild.name}: {prize}")
    
    @app_commands.command(name="gend", description="End a giveaway early")
    @app_commands.describe(message_id="Message ID of the giveaway to end")
    @app_commands.checks.has_permissions(manage_guild=True)
    async def gend(self, interaction: discord.Interaction, message_id: str):
        """End a giveaway early"""
        
        try:
            msg_id = int(message_id)
        except:
            await interaction.response.send_message(
                "❌ Invalid message ID!",
                ephemeral=True
            )
            return
        
        # Get giveaway from database
        async with self.bot.db.connection.execute(
            "SELECT * FROM giveaways WHERE message_id = ? AND guild_id = ? AND active = ?",
            (msg_id, interaction.guild.id, True)
        ) as cursor:
            giveaway = await cursor.fetchone()
        
        if not giveaway:
            await interaction.response.send_message(
                "❌ Giveaway not found or already ended!",
                ephemeral=True
            )
            return
        
        await interaction.response.defer()
        
        # End the giveaway
        await self._end_giveaway(giveaway)
        
        await interaction.followup.send(
            embed=success_embed(
                "Giveaway Ended",
                f"The giveaway has been ended early!"
            )
        )
    
    @app_commands.command(name="greroll", description="Reroll a giveaway winner")
    @app_commands.describe(message_id="Message ID of the giveaway to reroll")
    @app_commands.checks.has_permissions(manage_guild=True)
    async def greroll(self, interaction: discord.Interaction, message_id: str):
        """Reroll a giveaway winner"""
        
        try:
            msg_id = int(message_id)
        except:
            await interaction.response.send_message(
                "❌ Invalid message ID!",
                ephemeral=True
            )
            return
        
        # Get giveaway from database
        async with self.bot.db.connection.execute(
            "SELECT * FROM giveaways WHERE message_id = ? AND guild_id = ?",
            (msg_id, interaction.guild.id)
        ) as cursor:
            giveaway = await cursor.fetchone()
        
        if not giveaway:
            await interaction.response.send_message(
                "❌ Giveaway not found!",
                ephemeral=True
            )
            return
        
        await interaction.response.defer()
        
        # Get the message
        try:
            channel = self.bot.get_channel(giveaway[2])
            message = await channel.fetch_message(giveaway[1])
        except:
            await interaction.followup.send(
                "❌ Could not find the giveaway message!",
                ephemeral=True
            )
            return
        
        # Get participants
        reaction = discord.utils.get(message.reactions, emoji="🎉")
        if not reaction:
            await interaction.followup.send(
                "❌ No reactions found on giveaway!",
                ephemeral=True
            )
            return
        
        users = [user async for user in reaction.users() if not user.bot]
        
        if not users:
            await interaction.followup.send(
                "❌ No valid participants!",
                ephemeral=True
            )
            return
        
        # Pick new winner
        winner = random.choice(users)
        
        # Announce reroll
        embed = discord.Embed(
            title="🎉 Giveaway Rerolled!",
            description=f"**New Winner:** {winner.mention}\n"
                       f"**Prize:** {giveaway[4]}",
            color=config.Colors.SUCCESS
        )
        
        await channel.send(
            content=f"Congratulations {winner.mention}!",
            embed=embed
        )
        
        await interaction.followup.send(
            embed=success_embed(
                "Giveaway Rerolled",
                f"New winner: {winner.mention}"
            )
        )
        
        logger.info(f"Giveaway rerolled in {interaction.guild.name}: {winner}")
    
    @app_commands.command(name="glist", description="List active giveaways")
    async def glist(self, interaction: discord.Interaction):
        """List all active giveaways"""
        
        # Get active giveaways
        async with self.bot.db.connection.execute(
            "SELECT * FROM giveaways WHERE guild_id = ? AND active = ? ORDER BY end_time ASC",
            (interaction.guild.id, True)
        ) as cursor:
            giveaways = await cursor.fetchall()
        
        if not giveaways:
            await interaction.response.send_message(
                embed=info_embed(
                    "No Active Giveaways",
                    "There are no active giveaways in this server."
                )
            )
            return
        
        # Create embed
        embed = discord.Embed(
            title="🎉 Active Giveaways",
            color=config.Colors.PRIMARY
        )
        
        for giveaway in giveaways[:10]:  # Limit to 10
            channel = self.bot.get_channel(giveaway[2])
            end_time = datetime.fromisoformat(giveaway[6])
            
            embed.add_field(
                name=f"Prize: {giveaway[4]}",
                value=f"Channel: {channel.mention if channel else 'Unknown'}\n"
                      f"Winners: {giveaway[5]}\n"
                      f"Ends: <t:{int(end_time.timestamp())}:R>\n"
                      f"Message ID: `{giveaway[1]}`",
                inline=False
            )
        
        await interaction.response.send_message(embed=embed)
    
    @tasks.loop(seconds=30)
    async def check_giveaways(self):
        """Check for ended giveaways"""
        try:
            now = datetime.utcnow()
            
            # Get ended giveaways
            async with self.bot.db.connection.execute(
                "SELECT * FROM giveaways WHERE active = ? AND end_time <= ?",
                (True, now)
            ) as cursor:
                ended_giveaways = await cursor.fetchall()
            
            for giveaway in ended_giveaways:
                await self._end_giveaway(giveaway)
        
        except Exception as e:
            logger.error(f"Error checking giveaways: {e}")
    
    @check_giveaways.before_loop
    async def before_check_giveaways(self):
        await self.bot.wait_until_ready()
    
    async def _end_giveaway(self, giveaway):
        """End a giveaway and pick winners"""
        try:
            # Get the message
            channel = self.bot.get_channel(giveaway[2])
            if not channel:
                logger.error(f"Channel {giveaway[2]} not found for giveaway")
                return
            
            try:
                message = await channel.fetch_message(giveaway[1])
            except:
                logger.error(f"Message {giveaway[1]} not found for giveaway")
                # Mark as inactive
                await self.bot.db.connection.execute(
                    "UPDATE giveaways SET active = ? WHERE message_id = ?",
                    (False, giveaway[1])
                )
                await self.bot.db.connection.commit()
                return
            
            # Get participants
            reaction = discord.utils.get(message.reactions, emoji="🎉")
            if not reaction:
                # No participants
                embed = discord.Embed(
                    title="🎉 Giveaway Ended",
                    description=f"**Prize:** {giveaway[4]}\n\n"
                               f"No valid participants!",
                    color=config.Colors.ERROR
                )
                await message.edit(embed=embed)
                
                # Mark as inactive
                await self.bot.db.connection.execute(
                    "UPDATE giveaways SET active = ? WHERE message_id = ?",
                    (False, giveaway[1])
                )
                await self.bot.db.connection.commit()
                return
            
            # Get users who reacted (exclude bots)
            all_users = [user async for user in reaction.users() if not user.bot]
            
            # Filter by level requirement if set
            valid_users = []
            if giveaway[9]:  # min_level column
                guild = channel.guild
                for user in all_users:
                    try:
                        member = guild.get_member(user.id) or await guild.fetch_member(user.id)
                        user_data = await self.bot.db.get_user(member.id, guild.id)
                        if user_data.level >= giveaway[9]:
                            valid_users.append(member)
                    except:
                        continue
            else:
                valid_users = all_users
            
            if not valid_users:
                # No valid participants
                embed = discord.Embed(
                    title="🎉 Giveaway Ended",
                    description=f"**Prize:** {giveaway[4]}\n\n"
                               f"No valid participants!",
                    color=config.Colors.ERROR
                )
                await message.edit(embed=embed)
            else:
                # Pick winners
                num_winners = min(giveaway[5], len(valid_users))
                winners = random.sample(valid_users, num_winners)
                
                # Update embed
                winner_mentions = ", ".join([w.mention for w in winners])
                embed = discord.Embed(
                    title="🎉 Giveaway Ended!",
                    description=f"**Prize:** {giveaway[4]}\n\n"
                               f"**{'Winner' if num_winners == 1 else 'Winners'}:** {winner_mentions}",
                    color=config.Colors.SUCCESS
                )
                embed.set_footer(text="Giveaway ended")
                
                await message.edit(embed=embed)
                
                # Announce winners
                await channel.send(
                    f"🎉 Congratulations {winner_mentions}! You won **{giveaway[4]}**!"
                )
                
                logger.info(f"Giveaway ended: {giveaway[4]} - Winners: {[str(w) for w in winners]}")
            
            # Mark as inactive
            await self.bot.db.connection.execute(
                "UPDATE giveaways SET active = ? WHERE message_id = ?",
                (False, giveaway[1])
            )
            await self.bot.db.connection.commit()
        
        except Exception as e:
            logger.error(f"Error ending giveaway: {e}")
    
    def _parse_duration(self, duration: str):
        """Parse duration string (e.g., '1h', '30m', '1d')"""
        duration = duration.lower().strip()
        
        if duration[-1] in ['s', 'm', 'h', 'd']:
            time_unit = duration[-1]
            time_value = int(duration[:-1])
            return time_value, time_unit
        else:
            raise ValueError("Invalid duration format")

async def setup(bot):
    # Create giveaways table
    await bot.db.connection.execute("""
        CREATE TABLE IF NOT EXISTS giveaways (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            message_id INTEGER NOT NULL,
            channel_id INTEGER NOT NULL,
            guild_id INTEGER NOT NULL,
            prize TEXT NOT NULL,
            winners INTEGER DEFAULT 1,
            end_time TIMESTAMP NOT NULL,
            host_id INTEGER NOT NULL,
            active BOOLEAN DEFAULT 1,
            requirements TEXT,
            min_level INTEGER,
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
        )
    """)
    await bot.db.connection.commit()
    
    # Add requirements column if it doesn't exist (migration)
    try:
        await bot.db.connection.execute("ALTER TABLE giveaways ADD COLUMN requirements TEXT")
        await bot.db.connection.commit()
    except:
        pass
    
    # Add min_level column if it doesn't exist (migration)
    try:
        await bot.db.connection.execute("ALTER TABLE giveaways ADD COLUMN min_level INTEGER")
        await bot.db.connection.commit()
    except:
        pass
    
    await bot.add_cog(Giveaway(bot))
