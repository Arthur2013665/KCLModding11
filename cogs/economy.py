"""
Economy system cog
"""
import discord
from discord import app_commands
from discord.ext import commands
from datetime import datetime, timedelta
import random
from typing import Optional

from utils.embeds import economy_embed, leaderboard_embed, success_embed, error_embed
import config

class Economy(commands.Cog):
    """Economy and currency commands"""
    
    def __init__(self, bot):
        self.bot = bot
    
    @commands.Cog.listener()
    async def on_message(self, message: discord.Message):
        """Award XP for messages"""
        # Ignore bots and DMs
        if message.author.bot or not message.guild:
            return
        
        user_data = await self.bot.db.get_or_create_user(
            message.author.id,
            message.guild.id
        )
        
        now = datetime.utcnow()
        
        # Check cooldown
        if user_data.last_message:
            time_since = now - user_data.last_message
            if time_since.total_seconds() < config.Leveling.XP_COOLDOWN:
                return
        
        # Award XP
        xp_gain = random.randint(
            config.Leveling.XP_PER_MESSAGE_MIN,
            config.Leveling.XP_PER_MESSAGE_MAX
        )
        
        old_level = user_data.level
        user_data.xp += xp_gain
        user_data.last_message = now
        
        # Calculate new level
        new_level = config.Leveling.calculate_level(user_data.xp)
        
        # Cap level at 1000 for regular users (admins can go to 10000 via /setlevel)
        if new_level > 1000:
            new_level = 1000
            user_data.xp = config.Leveling.calculate_xp_for_level(1000)
        
        # Check for level up
        if new_level > old_level:
            user_data.level = new_level
            
            # Send level up message
            embed = discord.Embed(
                title=f"{config.Emojis.LEVEL_UP} Level Up!",
                description=f"{message.author.mention} reached level **{new_level}**!",
                color=config.Colors.SUCCESS
            )
            
            # Add special message if they hit max level
            if new_level == 1000:
                embed.add_field(
                    name="🏆 Max Level Reached!",
                    value="You've reached the maximum level for regular users!",
                    inline=False
                )
            
            await message.channel.send(embed=embed, delete_after=10)
        
        await self.bot.db.update_user(user_data)
        
        # Process commands (required for prefix commands to work)
        await self.bot.process_commands(message)
    
    @app_commands.command(name="level", description="Check your or someone's level")
    @app_commands.describe(user="User to check level (optional)")
    async def level(
        self,
        interaction: discord.Interaction,
        user: Optional[discord.Member] = None
    ):
        """Check level and XP"""
        target = user or interaction.user
        
        user_data = await self.bot.db.get_or_create_user(target.id, interaction.guild.id)
        
        # Calculate next level XP
        next_level_xp = config.Leveling.calculate_xp_for_level(user_data.level + 1)
        
        embed = economy_embed(
            target,
            user_data.balance,
            user_data.level,
            user_data.xp,
            next_level_xp
        )
        
        await interaction.response.send_message(embed=embed)
    
    @app_commands.command(name="balance", description="Check your or someone's balance")
    @app_commands.describe(user="User to check balance (optional)")
    async def balance(
        self,
        interaction: discord.Interaction,
        user: Optional[discord.Member] = None
    ):
        """Check balance"""
        target = user or interaction.user
        
        user_data = await self.bot.db.get_or_create_user(target.id, interaction.guild.id)
        
        # Calculate next level XP
        next_level_xp = config.Leveling.calculate_xp_for_level(user_data.level + 1)
        
        embed = economy_embed(
            target,
            user_data.balance,
            user_data.level,
            user_data.xp,
            next_level_xp
        )
        
        await interaction.response.send_message(embed=embed)
    
    @app_commands.command(name="daily", description="Claim your daily reward")
    async def daily(self, interaction: discord.Interaction):
        """Claim daily reward"""
        user_data = await self.bot.db.get_or_create_user(
            interaction.user.id,
            interaction.guild.id
        )
        
        now = datetime.utcnow()
        
        # Check if daily is available
        if user_data.last_daily:
            time_since = now - user_data.last_daily
            if time_since < timedelta(days=1):
                time_left = timedelta(days=1) - time_since
                hours = int(time_left.total_seconds() // 3600)
                minutes = int((time_left.total_seconds() % 3600) // 60)
                
                await interaction.response.send_message(
                    f"⏳ You can claim your daily reward in {hours}h {minutes}m",
                    ephemeral=True
                )
                return
        
        # Give reward
        user_data.balance += config.Economy.DAILY_REWARD
        user_data.last_daily = now
        await self.bot.db.update_user(user_data)
        
        embed = success_embed(
            "Daily Reward Claimed",
            f"You received **${config.Economy.DAILY_REWARD:,}**!\n\nNew balance: **${user_data.balance:,}**"
        )
        await interaction.response.send_message(embed=embed)
    
    @app_commands.command(name="work", description="Work to earn money")
    async def work(self, interaction: discord.Interaction):
        """Work to earn money"""
        user_data = await self.bot.db.get_or_create_user(
            interaction.user.id,
            interaction.guild.id
        )
        
        # Random earnings
        earnings = random.randint(config.Economy.WORK_MIN, config.Economy.WORK_MAX)
        user_data.balance += earnings
        await self.bot.db.update_user(user_data)
        
        jobs = [
            "worked as a developer",
            "delivered pizzas",
            "walked dogs",
            "mowed lawns",
            "washed cars",
            "tutored students",
            "streamed on Twitch",
            "made YouTube videos"
        ]
        
        job = random.choice(jobs)
        
        embed = success_embed(
            "Work Complete",
            f"You {job} and earned **${earnings:,}**!\n\nNew balance: **${user_data.balance:,}**"
        )
        await interaction.response.send_message(embed=embed)
    
    @app_commands.command(name="beg", description="Beg for money")
    async def beg(self, interaction: discord.Interaction):
        """Beg for money"""
        user_data = await self.bot.db.get_or_create_user(
            interaction.user.id,
            interaction.guild.id
        )
        
        # Random earnings (smaller than work)
        earnings = random.randint(config.Economy.BEG_MIN, config.Economy.BEG_MAX)
        user_data.balance += earnings
        await self.bot.db.update_user(user_data)
        
        responses = [
            f"Someone gave you **${earnings:,}**!",
            f"You found **${earnings:,}** on the ground!",
            f"A kind stranger donated **${earnings:,}**!",
            f"You received **${earnings:,}** from begging!"
        ]
        
        embed = success_embed(
            "Begging Success",
            f"{random.choice(responses)}\n\nNew balance: **${user_data.balance:,}**"
        )
        await interaction.response.send_message(embed=embed)
    
    @app_commands.command(name="rob", description="Attempt to rob another user")
    @app_commands.describe(user="User to rob")
    async def rob(
        self,
        interaction: discord.Interaction,
        user: discord.Member
    ):
        """Rob another user"""
        if user.id == interaction.user.id:
            await interaction.response.send_message(
                "❌ You can't rob yourself!",
                ephemeral=True
            )
            return
        
        if user.bot:
            await interaction.response.send_message(
                "❌ You can't rob bots!",
                ephemeral=True
            )
            return
        
        robber_data = await self.bot.db.get_or_create_user(
            interaction.user.id,
            interaction.guild.id
        )
        target_data = await self.bot.db.get_or_create_user(
            user.id,
            interaction.guild.id
        )
        
        # Check if target has money
        if target_data.balance < 100:
            await interaction.response.send_message(
                f"❌ {user.mention} doesn't have enough money to rob!",
                ephemeral=True
            )
            return
        
        # Random success/failure
        if random.random() < config.Economy.ROB_SUCCESS_RATE:
            # Success
            amount = int(target_data.balance * random.uniform(
                config.Economy.ROB_MIN_PERCENT,
                config.Economy.ROB_MAX_PERCENT
            ))
            
            robber_data.balance += amount
            target_data.balance -= amount
            
            await self.bot.db.update_user(robber_data)
            await self.bot.db.update_user(target_data)
            
            embed = success_embed(
                "Robbery Successful",
                f"You robbed **${amount:,}** from {user.mention}!\n\nYour balance: **${robber_data.balance:,}**"
            )
            await interaction.response.send_message(embed=embed)
        else:
            # Failure - lose money
            fine = random.randint(50, 200)
            robber_data.balance = max(0, robber_data.balance - fine)
            await self.bot.db.update_user(robber_data)
            
            embed = error_embed(
                "Robbery Failed",
                f"You got caught and paid a fine of **${fine:,}**!\n\nYour balance: **${robber_data.balance:,}**"
            )
            await interaction.response.send_message(embed=embed)
    
    @app_commands.command(name="pay", description="Pay money to another user")
    @app_commands.describe(
        user="User to pay",
        amount="Amount to pay"
    )
    async def pay(
        self,
        interaction: discord.Interaction,
        user: discord.Member,
        amount: int
    ):
        """Pay money to another user"""
        if user.id == interaction.user.id:
            await interaction.response.send_message(
                "❌ You can't pay yourself!",
                ephemeral=True
            )
            return
        
        if user.bot:
            await interaction.response.send_message(
                "❌ You can't pay bots!",
                ephemeral=True
            )
            return
        
        if amount <= 0:
            await interaction.response.send_message(
                "❌ Amount must be positive!",
                ephemeral=True
            )
            return
        
        payer_data = await self.bot.db.get_or_create_user(
            interaction.user.id,
            interaction.guild.id
        )
        
        if payer_data.balance < amount:
            await interaction.response.send_message(
                f"❌ You don't have enough money! Your balance: **${payer_data.balance:,}**",
                ephemeral=True
            )
            return
        
        receiver_data = await self.bot.db.get_or_create_user(
            user.id,
            interaction.guild.id
        )
        
        # Transfer money
        payer_data.balance -= amount
        receiver_data.balance += amount
        
        await self.bot.db.update_user(payer_data)
        await self.bot.db.update_user(receiver_data)
        
        embed = success_embed(
            "Payment Sent",
            f"You paid **${amount:,}** to {user.mention}!\n\nYour balance: **${payer_data.balance:,}**"
        )
        await interaction.response.send_message(embed=embed)
    
    @app_commands.command(name="leaderboard", description="View server leaderboard")
    @app_commands.describe(type="Leaderboard type (balance or level)")
    async def leaderboard(
        self,
        interaction: discord.Interaction,
        type: str = "balance"
    ):
        """View leaderboard"""
        type = type.lower()
        
        if type not in ['balance', 'level']:
            await interaction.response.send_message(
                "❌ Type must be 'balance' or 'level'",
                ephemeral=True
            )
            return
        
        if type == 'balance':
            users = await self.bot.db.get_top_users_by_balance(interaction.guild.id, 10)
        else:
            users = await self.bot.db.get_top_users_by_level(interaction.guild.id, 10)
        
        if not users:
            await interaction.response.send_message(
                "❌ No users found in the leaderboard.",
                ephemeral=True
            )
            return
        
        embed = leaderboard_embed(interaction.guild, users, type)
        await interaction.response.send_message(embed=embed)
    
    @app_commands.command(name="setlevel", description="Set a user's level (Admin only)")
    @app_commands.describe(user="User to set level for", level="Level to set")
    async def setlevel(
        self,
        interaction: discord.Interaction,
        user: discord.Member,
        level: int
    ):
        """Set a user's level"""
        # Check if user has administrator permission
        if not interaction.user.guild_permissions.administrator:
            await interaction.response.send_message(
                "❌ You need Administrator permission to use this command.",
                ephemeral=True
            )
            return
        
        if level < 0:
            await interaction.response.send_message(
                "❌ Level must be 0 or higher.",
                ephemeral=True
            )
            return
        
        # Check max level based on permissions
        max_level = 10000 if interaction.user.guild_permissions.administrator else 1000
        if level > max_level:
            await interaction.response.send_message(
                f"❌ Level cannot exceed {max_level:,}.",
                ephemeral=True
            )
            return
        
        # Get or create user
        user_data = await self.bot.db.get_or_create_user(user.id, interaction.guild.id)
        
        # Calculate XP for the new level
        new_xp = config.Leveling.calculate_xp_for_level(level)
        
        # Update user data
        user_data.level = level
        user_data.xp = new_xp
        await self.bot.db.update_user(user_data)
        
        embed = success_embed(
            "Level Set",
            f"Set {user.mention}'s level to **{level}**\nXP: **{new_xp:,}**"
        )
        await interaction.response.send_message(embed=embed)

async def setup(bot):
    await bot.add_cog(Economy(bot))
