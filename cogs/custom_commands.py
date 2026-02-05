"""
Custom commands cog
"""
import discord
from discord import app_commands
from discord.ext import commands
from typing import Optional

from utils.embeds import success_embed, info_embed, error_embed
from utils.checks import is_moderator
from utils.helpers import replace_variables
import config

class CustomCommands(commands.Cog):
    """Custom command system"""
    
    def __init__(self, bot):
        self.bot = bot
    
    @commands.Cog.listener()
    async def on_message(self, message: discord.Message):
        """Check for custom commands"""
        if message.author.bot or not message.guild:
            return
        
        # Check if message starts with prefix
        if not message.content.startswith(config.PREFIX):
            return
        
        # Extract command trigger
        trigger = message.content[len(config.PREFIX):].split()[0].lower()
        
        # Check if custom command exists
        custom_cmd = await self.bot.db.get_custom_command(message.guild.id, trigger)
        
        if custom_cmd:
            # Replace variables in response
            response = replace_variables(
                custom_cmd.response,
                message.author,
                message.guild,
                message.channel
            )
            
            await message.channel.send(response)
    
    @app_commands.command(name="customcmd-add", description="Create a custom command")
    @app_commands.describe(
        trigger="Command trigger (without prefix)",
        response="Command response"
    )
    @is_moderator()
    async def customcmd_add(
        self,
        interaction: discord.Interaction,
        trigger: str,
        response: str
    ):
        """Create a custom command"""
        trigger = trigger.lower()
        
        # Check if trigger is a built-in command
        if trigger in ['help', 'ping', 'ban', 'kick', 'mute']:
            await interaction.response.send_message(
                "❌ Cannot override built-in commands!",
                ephemeral=True
            )
            return
        
        # Add to database
        await self.bot.db.add_custom_command(
            interaction.guild.id,
            trigger,
            response,
            interaction.user.id
        )
        
        embed = success_embed(
            "Custom Command Created",
            f"**Trigger:** `{config.PREFIX}{trigger}`\n**Response:** {response}\n\n"
            f"Variables: `{{user}}`, `{{server}}`, `{{members}}`, `{{channel}}`"
        )
        await interaction.response.send_message(embed=embed)
    
    @app_commands.command(name="customcmd-remove", description="Delete a custom command")
    @app_commands.describe(trigger="Command trigger to remove")
    @is_moderator()
    async def customcmd_remove(
        self,
        interaction: discord.Interaction,
        trigger: str
    ):
        """Delete a custom command"""
        trigger = trigger.lower()
        
        success = await self.bot.db.remove_custom_command(interaction.guild.id, trigger)
        
        if success:
            embed = success_embed(
                "Custom Command Removed",
                f"Removed command: `{config.PREFIX}{trigger}`"
            )
            await interaction.response.send_message(embed=embed)
        else:
            await interaction.response.send_message(
                f"❌ Custom command `{config.PREFIX}{trigger}` not found.",
                ephemeral=True
            )
    
    @app_commands.command(name="customcmd-list", description="List all custom commands")
    @is_moderator()
    async def customcmd_list(self, interaction: discord.Interaction):
        """List all custom commands"""
        commands = await self.bot.db.get_all_custom_commands(interaction.guild.id)
        
        if not commands:
            await interaction.response.send_message(
                "✅ No custom commands configured.",
                ephemeral=True
            )
            return
        
        embed = discord.Embed(
            title="Custom Commands",
            description=f"Total: {len(commands)}",
            color=config.Colors.INFO
        )
        
        for cmd in commands[:25]:  # Show max 25
            embed.add_field(
                name=f"{config.PREFIX}{cmd.trigger}",
                value=cmd.response[:100] + ("..." if len(cmd.response) > 100 else ""),
                inline=False
            )
        
        if len(commands) > 25:
            embed.set_footer(text=f"Showing 25 of {len(commands)} commands")
        
        await interaction.response.send_message(embed=embed)
    
    @app_commands.command(name="customcmd-info", description="View custom command details")
    @app_commands.describe(trigger="Command trigger")
    @is_moderator()
    async def customcmd_info(
        self,
        interaction: discord.Interaction,
        trigger: str
    ):
        """View custom command details"""
        trigger = trigger.lower()
        
        cmd = await self.bot.db.get_custom_command(interaction.guild.id, trigger)
        
        if not cmd:
            await interaction.response.send_message(
                f"❌ Custom command `{config.PREFIX}{trigger}` not found.",
                ephemeral=True
            )
            return
        
        creator = await self.bot.fetch_user(cmd.created_by)
        
        embed = info_embed(
            f"Custom Command: {config.PREFIX}{trigger}",
            f"**Response:**\n{cmd.response}"
        )
        embed.add_field(name="Created By", value=creator.mention, inline=True)
        embed.add_field(
            name="Created At",
            value=f"<t:{int(cmd.created_at.timestamp())}:R>",
            inline=True
        )
        
        await interaction.response.send_message(embed=embed)

async def setup(bot):
    await bot.add_cog(CustomCommands(bot))
