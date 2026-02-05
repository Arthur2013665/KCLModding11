"""
Utility commands cog
"""
import discord
from discord import app_commands
from discord.ext import commands
from datetime import datetime, timedelta
import asyncio
from typing import Optional

from utils.embeds import user_info_embed, server_info_embed, info_embed, success_embed
from utils.helpers import parse_time
import config

class Utility(commands.Cog):
    """Utility and information commands"""
    
    def __init__(self, bot):
        self.bot = bot
        self.afk_users = {}  # user_id: reason
    
    @commands.hybrid_command(name="userinfo", description="Get information about a user")
    @app_commands.describe(user="User to get info about (optional)")
    async def userinfo(
        self,
        ctx: commands.Context,
        user: Optional[discord.Member] = None
    ):
        """Get user information"""
        target = user or ctx.author
        embed = user_info_embed(target)
        await ctx.send(embed=embed)
    
    @commands.hybrid_command(name="serverinfo", description="Get information about the server")
    async def serverinfo(self, ctx: commands.Context):
        """Get server information"""
        embed = server_info_embed(ctx.guild)
        await ctx.send(embed=embed)
    
    @commands.hybrid_command(name="avatar", description="Get a user's avatar")
    @app_commands.describe(user="User to get avatar (optional)")
    async def avatar(
        self,
        ctx: commands.Context,
        user: Optional[discord.Member] = None
    ):
        """Get user avatar"""
        target = user or ctx.author
        
        embed = discord.Embed(
            title=f"{target.name}'s Avatar",
            color=target.color if target.color != discord.Color.default() else config.Colors.PRIMARY
        )
        embed.set_image(url=target.display_avatar.url)
        embed.add_field(
            name="Links",
            value=f"[PNG]({target.display_avatar.replace(format='png', size=1024).url}) | "
                  f"[JPG]({target.display_avatar.replace(format='jpg', size=1024).url}) | "
                  f"[WEBP]({target.display_avatar.replace(format='webp', size=1024).url})"
        )
        
        await ctx.send(embed=embed)
    
    @app_commands.command(name="poll", description="Create a poll")
    @app_commands.describe(
        question="Poll question",
        option1="First option",
        option2="Second option",
        option3="Third option (optional)",
        option4="Fourth option (optional)",
        option5="Fifth option (optional)"
    )
    async def poll(
        self,
        interaction: discord.Interaction,
        question: str,
        option1: str,
        option2: str,
        option3: Optional[str] = None,
        option4: Optional[str] = None,
        option5: Optional[str] = None
    ):
        """Create a poll"""
        options = [option1, option2]
        if option3:
            options.append(option3)
        if option4:
            options.append(option4)
        if option5:
            options.append(option5)
        
        # Emojis for reactions
        emojis = ['1️⃣', '2️⃣', '3️⃣', '4️⃣', '5️⃣']
        
        embed = discord.Embed(
            title=f"📊 {question}",
            description="\n".join([f"{emojis[i]} {opt}" for i, opt in enumerate(options)]),
            color=config.Colors.PRIMARY
        )
        embed.set_footer(text=f"Poll by {interaction.user.name}")
        
        await interaction.response.send_message(embed=embed)
        message = await interaction.original_response()
        
        # Add reactions
        for i in range(len(options)):
            await message.add_reaction(emojis[i])
    
    @app_commands.command(name="remind", description="Set a reminder")
    @app_commands.describe(
        time="Time until reminder (e.g., 1h, 30m, 1d)",
        message="Reminder message"
    )
    async def remind(
        self,
        interaction: discord.Interaction,
        time: str,
        message: str
    ):
        """Set a reminder"""
        time_delta = parse_time(time)
        
        if not time_delta:
            await interaction.response.send_message(
                "❌ Invalid time format. Use formats like: 1h, 30m, 1d",
                ephemeral=True
            )
            return
        
        if time_delta.total_seconds() < 60:
            await interaction.response.send_message(
                "❌ Reminder must be at least 1 minute.",
                ephemeral=True
            )
            return
        
        if time_delta.total_seconds() > 2592000:  # 30 days
            await interaction.response.send_message(
                "❌ Reminder cannot be more than 30 days.",
                ephemeral=True
            )
            return
        
        from utils.helpers import format_time
        
        embed = success_embed(
            "Reminder Set",
            f"I'll remind you in {format_time(int(time_delta.total_seconds()))}:\n**{message}**"
        )
        await interaction.response.send_message(embed=embed)
        
        # Wait and send reminder
        await asyncio.sleep(time_delta.total_seconds())
        
        try:
            reminder_embed = discord.Embed(
                title="⏰ Reminder",
                description=message,
                color=config.Colors.INFO
            )
            await interaction.user.send(embed=reminder_embed)
        except:
            pass  # User has DMs disabled
    
    @app_commands.command(name="afk", description="Set your AFK status")
    @app_commands.describe(reason="Reason for being AFK (optional)")
    async def afk(
        self,
        interaction: discord.Interaction,
        reason: Optional[str] = "AFK"
    ):
        """Set AFK status"""
        self.afk_users[interaction.user.id] = {
            'reason': reason,
            'time': datetime.utcnow()
        }
        
        embed = success_embed(
            "AFK Status Set",
            f"You are now AFK: {reason}"
        )
        await interaction.response.send_message(embed=embed)
    
    @commands.Cog.listener()
    async def on_message(self, message: discord.Message):
        """Check for AFK users"""
        if message.author.bot:
            return
        
        # Check if user is AFK and remove status
        if message.author.id in self.afk_users:
            afk_data = self.afk_users.pop(message.author.id)
            time_afk = datetime.utcnow() - afk_data['time']
            
            from utils.helpers import format_time
            
            await message.channel.send(
                f"Welcome back {message.author.mention}! You were AFK for {format_time(int(time_afk.total_seconds()))}.",
                delete_after=5
            )
        
        # Check if message mentions AFK users
        for mention in message.mentions:
            if mention.id in self.afk_users:
                afk_data = self.afk_users[mention.id]
                time_afk = datetime.utcnow() - afk_data['time']
                
                from utils.helpers import format_time
                
                await message.channel.send(
                    f"{mention.name} is AFK: {afk_data['reason']} ({format_time(int(time_afk.total_seconds()))} ago)",
                    delete_after=5
                )
    
    @commands.hybrid_command(name="ping", description="Check bot latency")
    async def ping(self, ctx: commands.Context):
        """Check bot latency"""
        latency = round(self.bot.latency * 1000)
        
        embed = discord.Embed(
            title="🏓 Pong!",
            description=f"Latency: **{latency}ms**",
            color=config.Colors.SUCCESS if latency < 200 else config.Colors.WARNING
        )
        await ctx.send(embed=embed)
    
    @app_commands.command(name="uptime", description="Check bot uptime")
    async def uptime(self, interaction: discord.Interaction):
        """Check bot uptime"""
        uptime = datetime.utcnow() - self.bot.start_time
        
        days = uptime.days
        hours, remainder = divmod(uptime.seconds, 3600)
        minutes, seconds = divmod(remainder, 60)
        
        uptime_str = f"{days}d {hours}h {minutes}m {seconds}s"
        
        embed = info_embed(
            "Bot Uptime",
            f"I've been online for: **{uptime_str}**"
        )
        await interaction.response.send_message(embed=embed)
    
    @app_commands.command(name="invite", description="Get bot invite link")
    async def invite(self, interaction: discord.Interaction):
        """Get bot invite link"""
        invite_url = discord.utils.oauth_url(
            self.bot.user.id,
            permissions=discord.Permissions(administrator=True)
        )
        
        embed = info_embed(
            "Invite Me!",
            f"[Click here to invite me to your server!]({invite_url})"
        )
        await interaction.response.send_message(embed=embed)
    
    @app_commands.command(name="help", description="View all bot commands")
    async def help_command(self, interaction: discord.Interaction):
        """Help command"""
        embed = discord.Embed(
            title=f"📚 {config.BOT_NAME} Commands",
            description=f"Version {config.BOT_VERSION}\n\nUse `/` to use commands!",
            color=config.Colors.PRIMARY
        )
        
        embed.add_field(
            name="🛡️ Moderation",
            value="`/ban` `/kick` `/timeout` `/warn` `/purge` `/lock` `/unlock` `/slowmode` `/nuke`",
            inline=False
        )
        
        embed.add_field(
            name="📝 Logging",
            value="`/setbotlog` `/setmodlog` `/modlogs` `/case`\nTracks commands, joins, bans, role/channel changes",
            inline=False
        )
        
        embed.add_field(
            name="💰 Economy & Leveling",
            value="`/balance` `/daily` `/work` `/rob` `/pay` `/level` `/leaderboard` `/setlevel`",
            inline=False
        )
        
        embed.add_field(
            name="🎉 Giveaways",
            value="`/gstart` `/gend` `/greroll` `/glist`\nSupports level requirements and custom requirements",
            inline=False
        )
        
        embed.add_field(
            name="🎮 Fun",
            value="`/8ball` `/coinflip` `/dice` `/joke` `/ship` `/roast` `/compliment` `/hack` and more...",
            inline=False
        )
        
        embed.add_field(
            name="🔧 Utility",
            value="`/userinfo` `/serverinfo` `/avatar` `/ping` `/uptime` `/commands` `/help`",
            inline=False
        )
        
        embed.add_field(
            name="🎨 Custom Commands",
            value="`/customcmd-add` `/customcmd-remove` `/customcmd-list` `/customcmd-info`",
            inline=False
        )
        
        embed.add_field(
            name="🤖 Auto-Moderation",
            value="`/automod` `/blacklist`\nSpam, caps, invites, mentions detection",
            inline=False
        )
        
        embed.add_field(
            name="💡 Tip",
            value="Type `/` in chat to see all available commands!\nUse `/commands` for a complete list.",
            inline=False
        )
        
        embed.set_footer(text=f"Use /commands for full list | Prefix: {config.PREFIX}")
        
        await interaction.response.send_message(embed=embed)
    
    @commands.command(name='help', aliases=['h'])
    async def help_prefix(self, ctx):
        """Help command (prefix version)"""
        embed = discord.Embed(
            title=f"📚 {config.BOT_NAME} Commands",
            description=f"Version {config.BOT_VERSION}\n\nUse `{config.PREFIX}` for prefix commands or `/` for slash commands!",
            color=config.Colors.PRIMARY
        )
        
        embed.add_field(
            name="🛡️ Moderation",
            value="`/ban` `/kick` `/timeout` `/warn` `/purge` `/lock` `/unlock` `/slowmode` `/nuke`",
            inline=False
        )
        
        embed.add_field(
            name="📝 Logging",
            value="`/setbotlog` `/setmodlog` `/modlogs` `/case`\nTracks commands, joins, bans, role/channel changes",
            inline=False
        )
        
        embed.add_field(
            name="💰 Economy & Leveling",
            value="`/balance` `/daily` `/work` `/rob` `/pay` `/level` `/leaderboard` `/setlevel`",
            inline=False
        )
        
        embed.add_field(
            name="🎉 Giveaways",
            value="`/gstart` `/gend` `/greroll` `/glist`\nSupports level requirements and custom requirements",
            inline=False
        )
        
        embed.add_field(
            name="🎮 Fun",
            value="`/8ball` `/coinflip` `/dice` `/joke` `/ship` `/roast` `/compliment` `/hack` and more...",
            inline=False
        )
        
        embed.add_field(
            name="🔧 Utility",
            value="`/userinfo` `/serverinfo` `/avatar` `/ping` `/uptime` `/commands` `/help`",
            inline=False
        )
        
        embed.add_field(
            name="🎨 Custom Commands",
            value="`/customcmd-add` `/customcmd-remove` `/customcmd-list` `/customcmd-info`",
            inline=False
        )
        
        embed.add_field(
            name="🤖 Auto-Moderation",
            value="`/automod` `/blacklist`\nSpam, caps, invites, mentions detection",
            inline=False
        )
        
        embed.add_field(
            name="🔴 Admin (Owner Only)",
            value=f"`{config.PREFIX}shutdown` `{config.PREFIX}kill` `{config.PREFIX}stop` `{config.PREFIX}restart`",
            inline=False
        )
        
        embed.add_field(
            name="💡 Tip",
            value="Type `/` in chat to see all available commands!\nUse `/commands` for a complete list.",
            inline=False
        )
        
        embed.set_footer(text=f"Use /commands for full list | Prefix: {config.PREFIX}")
        
        await ctx.send(embed=embed)
    
    @app_commands.command(name="invitelink", description="Get the server invite link")
    async def invitelink(self, interaction: discord.Interaction):
        """Get server invite link"""
        # Check if server has a configured invite link in database
        settings = await self.bot.db.get_guild_settings(interaction.guild.id)
        
        if hasattr(settings, 'invite_link') and settings.invite_link:
            embed = discord.Embed(
                title=f"📨 {interaction.guild.name} Invite",
                description=f"[Click here to join!]({settings.invite_link})\n\n`{settings.invite_link}`",
                color=config.Colors.PRIMARY
            )
            embed.set_thumbnail(url=interaction.guild.icon.url if interaction.guild.icon else None)
            await interaction.response.send_message(embed=embed)
        else:
            await interaction.response.send_message(
                "❌ No invite link configured. Use `/setinvitelink <url>` to set one.",
                ephemeral=True
            )
    
    @app_commands.command(name="setinvitelink", description="Set the server invite link")
    @app_commands.describe(invite_url="The invite URL or code")
    async def setinvitelink(self, interaction: discord.Interaction, invite_url: str):
        """Set server invite link"""
        # Check if user has manage server permission
        if not interaction.user.guild_permissions.manage_guild:
            await interaction.response.send_message(
                "❌ You need 'Manage Server' permission to set the invite link.",
                ephemeral=True
            )
            return
        
        # Clean up the invite URL if it's just a code
        if not invite_url.startswith('http'):
            invite_url = f"https://discord.gg/{invite_url}"
        
        # Store in database
        settings = await self.bot.db.get_guild_settings(interaction.guild.id)
        settings.invite_link = invite_url
        await self.bot.db.update_guild_settings(settings)
        
        embed = success_embed(
            "Invite Link Set",
            f"Server invite link has been set to:\n{invite_url}\n\nUsers can now use `/invitelink` to get it!"
        )
        await interaction.response.send_message(embed=embed)
    
    @app_commands.command(name="reply", description="Reply to a user with a message")
    @app_commands.describe(user="User to reply to", message="Your message")
    async def reply(self, interaction: discord.Interaction, user: discord.Member, message: str):
        """Reply to a user"""
        embed = discord.Embed(
            description=message,
            color=config.Colors.PRIMARY,
            timestamp=datetime.utcnow()
        )
        embed.set_author(
            name=f"{interaction.user.name} replies to {user.name}",
            icon_url=interaction.user.display_avatar.url
        )
        embed.set_footer(text=f"Replying to {user.name}", icon_url=user.display_avatar.url)
        
        await interaction.response.send_message(f"{user.mention}", embed=embed)
    
    @app_commands.command(name="commands", description="List all available bot commands")
    async def commands_list(self, interaction: discord.Interaction):
        """List all bot commands"""
        
        # Get all commands
        commands = self.bot.tree.get_commands()
        
        embed = discord.Embed(
            title="📋 Bot Commands",
            description=f"Total commands: **{len(commands)}**\n\n"
                       f"Use `/help` for detailed information about each command.",
            color=config.Colors.PRIMARY
        )
        
        # Group commands by category
        categories = {}
        for cmd in commands:
            # Get cog name
            if hasattr(cmd, 'binding') and cmd.binding:
                cog_name = cmd.binding.__class__.__name__
            else:
                cog_name = "Other"
            
            if cog_name not in categories:
                categories[cog_name] = []
            categories[cog_name].append(cmd.name)
        
        # Add fields for each category
        for category, cmds in sorted(categories.items()):
            cmd_list = ", ".join([f"`/{cmd}`" for cmd in sorted(cmds)])
            embed.add_field(
                name=f"{category} ({len(cmds)})",
                value=cmd_list[:1024],  # Discord field limit
                inline=False
            )
        
        embed.set_footer(text=f"Bot: {self.bot.user.name}")
        
        await interaction.response.send_message(embed=embed, ephemeral=True)

async def setup(bot):
    await bot.add_cog(Utility(bot))
