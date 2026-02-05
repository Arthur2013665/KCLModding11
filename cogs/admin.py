"""
Admin Commands Cog
Contains administrative commands for bot management
"""

import discord
from discord.ext import commands
import asyncio
import sys
import os


class Admin(commands.Cog):
    """Administrative commands for bot owners"""
    
    def __init__(self, bot):
        self.bot = bot
    
    @commands.command(name='shutdown', aliases=['kill', 'stop'])
    @commands.is_owner()
    async def shutdown(self, ctx):
        """
        Shuts down the bot
        Only the bot owner can use this command
        """
        embed = discord.Embed(
            title="🔴 Bot Shutdown",
            description="Bot is shutting down...",
            color=discord.Color.red()
        )
        embed.set_footer(text=f"Requested by {ctx.author}")
        
        await ctx.send(embed=embed)
        
        # Give time for the message to send
        await asyncio.sleep(1)
        
        # Close the bot
        await self.bot.close()
    
    @commands.command(name='restart')
    @commands.is_owner()
    async def restart(self, ctx):
        """
        Restarts the bot
        Only the bot owner can use this command
        """
        embed = discord.Embed(
            title="🔄 Bot Restart",
            description="Bot is restarting...",
            color=discord.Color.orange()
        )
        embed.set_footer(text=f"Requested by {ctx.author}")
        
        await ctx.send(embed=embed)
        
        # Give time for the message to send
        await asyncio.sleep(1)
        
        # Restart the bot
        os.execv(sys.executable, ['python'] + sys.argv)
    
    @shutdown.error
    @restart.error
    async def admin_error(self, ctx, error):
        """Error handler for admin commands"""
        if isinstance(error, commands.NotOwner):
            embed = discord.Embed(
                title="❌ Access Denied",
                description="Only the bot owner can use this command.",
                color=discord.Color.red()
            )
            await ctx.send(embed=embed)


async def setup(bot):
    await bot.add_cog(Admin(bot))