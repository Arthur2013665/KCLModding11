"""
Events cog for welcome/goodbye messages and other events
"""
import discord
from discord import app_commands
from discord.ext import commands
from typing import Optional

from utils.embeds import success_embed, info_embed
from utils.checks import is_moderator
from utils.helpers import replace_variables
import config

class Events(commands.Cog):
    """Event handlers for welcome, goodbye, etc."""
    
    def __init__(self, bot):
        self.bot = bot
    
    @commands.Cog.listener()
    async def on_member_join(self, member: discord.Member):
        """Handle member join"""
        settings = await self.bot.db.get_guild_settings(member.guild.id)
        
        if settings.welcome_channel and settings.welcome_message:
            channel = member.guild.get_channel(settings.welcome_channel)
            
            if channel:
                # Replace variables
                message = replace_variables(
                    settings.welcome_message,
                    member,
                    member.guild,
                    channel
                )
                
                embed = discord.Embed(
                    title="👋 Welcome!",
                    description=message,
                    color=config.Colors.SUCCESS
                )
                embed.set_thumbnail(url=member.display_avatar.url)
                embed.set_footer(text=f"Member #{member.guild.member_count}")
                
                await channel.send(embed=embed)
    
    @commands.Cog.listener()
    async def on_member_remove(self, member: discord.Member):
        """Handle member leave"""
        settings = await self.bot.db.get_guild_settings(member.guild.id)
        
        if settings.goodbye_channel and settings.goodbye_message:
            channel = member.guild.get_channel(settings.goodbye_channel)
            
            if channel:
                # Replace variables
                message = replace_variables(
                    settings.goodbye_message,
                    member,
                    member.guild,
                    channel
                )
                
                embed = discord.Embed(
                    title="👋 Goodbye",
                    description=message,
                    color=config.Colors.ERROR
                )
                embed.set_thumbnail(url=member.display_avatar.url)
                embed.set_footer(text=f"Members remaining: {member.guild.member_count}")
                
                await channel.send(embed=embed)
    
    @app_commands.command(name="setwelcome", description="Configure welcome messages")
    @app_commands.describe(
        channel="Channel to send welcome messages",
        message="Welcome message (use {user}, {server}, {members})"
    )
    @is_moderator()
    async def setwelcome(
        self,
        interaction: discord.Interaction,
        channel: discord.TextChannel,
        message: str
    ):
        """Configure welcome messages"""
        settings = await self.bot.db.get_guild_settings(interaction.guild.id)
        settings.welcome_channel = channel.id
        settings.welcome_message = message
        await self.bot.db.update_guild_settings(settings)
        
        embed = success_embed(
            "Welcome Message Configured",
            f"**Channel:** {channel.mention}\n**Message:** {message}\n\n"
            f"Variables: `{{user}}`, `{{username}}`, `{{server}}`, `{{members}}`"
        )
        await interaction.response.send_message(embed=embed)
    
    @app_commands.command(name="setgoodbye", description="Configure goodbye messages")
    @app_commands.describe(
        channel="Channel to send goodbye messages",
        message="Goodbye message (use {user}, {server}, {members})"
    )
    @is_moderator()
    async def setgoodbye(
        self,
        interaction: discord.Interaction,
        channel: discord.TextChannel,
        message: str
    ):
        """Configure goodbye messages"""
        settings = await self.bot.db.get_guild_settings(interaction.guild.id)
        settings.goodbye_channel = channel.id
        settings.goodbye_message = message
        await self.bot.db.update_guild_settings(settings)
        
        embed = success_embed(
            "Goodbye Message Configured",
            f"**Channel:** {channel.mention}\n**Message:** {message}\n\n"
            f"Variables: `{{user}}`, `{{username}}`, `{{server}}`, `{{members}}`"
        )
        await interaction.response.send_message(embed=embed)
    
    @app_commands.command(name="testwelcome", description="Test the welcome message")
    @is_moderator()
    async def testwelcome(self, interaction: discord.Interaction):
        """Test welcome message"""
        settings = await self.bot.db.get_guild_settings(interaction.guild.id)
        
        if not settings.welcome_channel or not settings.welcome_message:
            await interaction.response.send_message(
                "❌ Welcome message not configured. Use `/setwelcome` first.",
                ephemeral=True
            )
            return
        
        channel = interaction.guild.get_channel(settings.welcome_channel)
        
        if not channel:
            await interaction.response.send_message(
                "❌ Welcome channel not found.",
                ephemeral=True
            )
            return
        
        # Replace variables with test user
        message = replace_variables(
            settings.welcome_message,
            interaction.user,
            interaction.guild,
            channel
        )
        
        embed = discord.Embed(
            title="👋 Welcome! (TEST)",
            description=message,
            color=config.Colors.SUCCESS
        )
        embed.set_thumbnail(url=interaction.user.display_avatar.url)
        embed.set_footer(text=f"Member #{interaction.guild.member_count}")
        
        await channel.send(embed=embed)
        await interaction.response.send_message(
            f"✅ Test welcome message sent to {channel.mention}",
            ephemeral=True
        )
    
    @app_commands.command(name="testgoodbye", description="Test the goodbye message")
    @is_moderator()
    async def testgoodbye(self, interaction: discord.Interaction):
        """Test goodbye message"""
        settings = await self.bot.db.get_guild_settings(interaction.guild.id)
        
        if not settings.goodbye_channel or not settings.goodbye_message:
            await interaction.response.send_message(
                "❌ Goodbye message not configured. Use `/setgoodbye` first.",
                ephemeral=True
            )
            return
        
        channel = interaction.guild.get_channel(settings.goodbye_channel)
        
        if not channel:
            await interaction.response.send_message(
                "❌ Goodbye channel not found.",
                ephemeral=True
            )
            return
        
        # Replace variables with test user
        message = replace_variables(
            settings.goodbye_message,
            interaction.user,
            interaction.guild,
            channel
        )
        
        embed = discord.Embed(
            title="👋 Goodbye (TEST)",
            description=message,
            color=config.Colors.ERROR
        )
        embed.set_thumbnail(url=interaction.user.display_avatar.url)
        embed.set_footer(text=f"Members remaining: {interaction.guild.member_count}")
        
        await channel.send(embed=embed)
        await interaction.response.send_message(
            f"✅ Test goodbye message sent to {channel.mention}",
            ephemeral=True
        )
    
    @app_commands.command(name="event-create", description="Create a server event announcement")
    @app_commands.describe(
        title="Event title",
        description="Event description",
        date="Event date (e.g., 'Dec 25, 2024 8:00 PM')",
        channel="Channel to announce in (optional)"
    )
    @is_moderator()
    async def event_create(
        self,
        interaction: discord.Interaction,
        title: str,
        description: str,
        date: str,
        channel: discord.TextChannel = None
    ):
        """Create a server event announcement"""
        target_channel = channel or interaction.channel
        
        embed = discord.Embed(
            title="🎉 Server Event",
            color=config.Colors.PRIMARY
        )
        embed.add_field(name="📅 Event", value=title, inline=False)
        embed.add_field(name="📝 Description", value=description, inline=False)
        embed.add_field(name="🕒 Date & Time", value=date, inline=False)
        embed.add_field(name="👤 Hosted by", value=interaction.user.mention, inline=True)
        embed.set_footer(text="React with 🎉 if you're attending!")
        
        message = await target_channel.send(embed=embed)
        await message.add_reaction("🎉")
        await message.add_reaction("❌")
        
        await interaction.response.send_message(
            f"✅ Event created in {target_channel.mention}!",
            ephemeral=True
        )
    
    @app_commands.command(name="announcement", description="Create a server announcement")
    @app_commands.describe(
        title="Announcement title",
        message="Announcement message",
        channel="Channel to announce in (optional)",
        ping_everyone="Ping @everyone (optional)"
    )
    @is_moderator()
    async def announcement(
        self,
        interaction: discord.Interaction,
        title: str,
        message: str,
        channel: discord.TextChannel = None,
        ping_everyone: bool = False
    ):
        """Create a server announcement"""
        target_channel = channel or interaction.channel
        
        embed = discord.Embed(
            title=f"📢 {title}",
            description=message,
            color=config.Colors.INFO
        )
        embed.add_field(name="📝 From", value=interaction.user.mention, inline=True)
        embed.set_footer(text=f"Announcement • {interaction.guild.name}")
        
        content = "@everyone" if ping_everyone else None
        
        await target_channel.send(content=content, embed=embed)
        await interaction.response.send_message(
            f"✅ Announcement posted in {target_channel.mention}!",
            ephemeral=True
        )
    
    @app_commands.command(name="milestone", description="Celebrate a server milestone")
    @app_commands.describe(
        milestone="What milestone was reached",
        message="Celebration message (optional)",
        channel="Channel to celebrate in (optional)"
    )
    @is_moderator()
    async def milestone(
        self,
        interaction: discord.Interaction,
        milestone: str,
        message: str = None,
        channel: discord.TextChannel = None
    ):
        """Celebrate a server milestone"""
        target_channel = channel or interaction.channel
        
        embed = discord.Embed(
            title="🎊 Milestone Reached!",
            description=f"**{milestone}**",
            color=config.Colors.SUCCESS
        )
        
        if message:
            embed.add_field(name="🎉 Celebration", value=message, inline=False)
        
        embed.add_field(name="📊 Server Stats", value=f"**Members:** {interaction.guild.member_count}\n**Channels:** {len(interaction.guild.channels)}\n**Roles:** {len(interaction.guild.roles)}", inline=True)
        embed.add_field(name="👑 Celebrated by", value=interaction.user.mention, inline=True)
        embed.set_thumbnail(url=interaction.guild.icon.url if interaction.guild.icon else None)
        embed.set_footer(text=f"Thank you for being part of {interaction.guild.name}!")
        
        await target_channel.send(embed=embed)
        await interaction.response.send_message(
            f"🎊 Milestone celebration posted in {target_channel.mention}!",
            ephemeral=True
        )
    
    @app_commands.command(name="poll-event", description="Create a poll for an event")
    @app_commands.describe(
        question="Poll question",
        option1="First option",
        option2="Second option",
        option3="Third option (optional)",
        option4="Fourth option (optional)",
        channel="Channel to post poll (optional)"
    )
    @is_moderator()
    async def poll_event(
        self,
        interaction: discord.Interaction,
        question: str,
        option1: str,
        option2: str,
        option3: str = None,
        option4: str = None,
        channel: discord.TextChannel = None
    ):
        """Create a poll for server events"""
        target_channel = channel or interaction.channel
        
        options = [option1, option2]
        if option3:
            options.append(option3)
        if option4:
            options.append(option4)
        
        reactions = ["1️⃣", "2️⃣", "3️⃣", "4️⃣"]
        
        embed = discord.Embed(
            title="📊 Event Poll",
            description=f"**{question}**\n\n" + "\n".join([f"{reactions[i]} {opt}" for i, opt in enumerate(options)]),
            color=config.Colors.PRIMARY
        )
        embed.add_field(name="📝 Created by", value=interaction.user.mention, inline=True)
        embed.set_footer(text="Vote by reacting below!")
        
        message = await target_channel.send(embed=embed)
        
        for i in range(len(options)):
            await message.add_reaction(reactions[i])
        
        await interaction.response.send_message(
            f"📊 Poll created in {target_channel.mention}!",
            ephemeral=True
        )
    
    @app_commands.command(name="countdown", description="Create a countdown to an event")
    @app_commands.describe(
        event_name="Name of the event",
        target_date="Target date (e.g., 'Dec 25, 2024 8:00 PM')",
        channel="Channel to post countdown (optional)"
    )
    @is_moderator()
    async def countdown(
        self,
        interaction: discord.Interaction,
        event_name: str,
        target_date: str,
        channel: discord.TextChannel = None
    ):
        """Create a countdown to an event"""
        target_channel = channel or interaction.channel
        
        embed = discord.Embed(
            title="⏰ Event Countdown",
            color=config.Colors.WARNING
        )
        embed.add_field(name="🎯 Event", value=event_name, inline=False)
        embed.add_field(name="📅 Target Date", value=target_date, inline=False)
        embed.add_field(name="⏳ Status", value="Countdown started! Check back regularly for updates.", inline=False)
        embed.add_field(name="👤 Created by", value=interaction.user.mention, inline=True)
        embed.set_footer(text="Stay tuned for updates!")
        
        await target_channel.send(embed=embed)
        await interaction.response.send_message(
            f"⏰ Countdown posted in {target_channel.mention}!",
            ephemeral=True
        )
    
    @app_commands.command(name="server-update", description="Post a server update")
    @app_commands.describe(
        update_type="Type of update (New Feature, Bug Fix, Announcement, etc.)",
        title="Update title",
        description="Update description",
        channel="Channel to post update (optional)"
    )
    @is_moderator()
    async def server_update(
        self,
        interaction: discord.Interaction,
        update_type: str,
        title: str,
        description: str,
        channel: discord.TextChannel = None
    ):
        """Post a server update"""
        target_channel = channel or interaction.channel
        
        # Choose color based on update type
        color_map = {
            "new feature": config.Colors.SUCCESS,
            "bug fix": config.Colors.WARNING,
            "announcement": config.Colors.INFO,
            "maintenance": config.Colors.ERROR
        }
        color = color_map.get(update_type.lower(), config.Colors.PRIMARY)
        
        embed = discord.Embed(
            title=f"🔄 Server Update: {title}",
            description=description,
            color=color
        )
        embed.add_field(name="📋 Update Type", value=update_type, inline=True)
        embed.add_field(name="👤 Posted by", value=interaction.user.mention, inline=True)
        embed.set_footer(text=f"Server Update • {interaction.guild.name}")
        
        await target_channel.send(embed=embed)
        await interaction.response.send_message(
            f"🔄 Server update posted in {target_channel.mention}!",
            ephemeral=True
        )
    
    @app_commands.command(name="celebration", description="Create a celebration message")
    @app_commands.describe(
        reason="What are we celebrating?",
        message="Celebration message (optional)",
        channel="Channel to celebrate in (optional)"
    )
    @is_moderator()
    async def celebration(
        self,
        interaction: discord.Interaction,
        reason: str,
        message: str = None,
        channel: discord.TextChannel = None
    ):
        """Create a celebration message"""
        target_channel = channel or interaction.channel
        
        embed = discord.Embed(
            title="🎉 Celebration Time!",
            description=f"**{reason}**",
            color=config.Colors.SUCCESS
        )
        
        if message:
            embed.add_field(name="🎊 Message", value=message, inline=False)
        
        embed.add_field(name="🎈 Let's celebrate!", value="React with 🎉 to join the celebration!", inline=False)
        embed.add_field(name="👤 Hosted by", value=interaction.user.mention, inline=True)
        embed.set_footer(text="Time to party! 🎊")
        
        msg = await target_channel.send(embed=embed)
        await msg.add_reaction("🎉")
        await msg.add_reaction("🎊")
        await msg.add_reaction("🥳")
        
        await interaction.response.send_message(
            f"🎉 Celebration started in {target_channel.mention}!",
            ephemeral=True
        )

async def setup(bot):
    await bot.add_cog(Events(bot))
