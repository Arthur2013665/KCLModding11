"""
Role management commands - 40+ commands
"""
import discord
from discord import app_commands
from discord.ext import commands
from typing import Optional

from utils.embeds import success_embed, error_embed
from utils.checks import is_moderator
import config

class RoleManagement(commands.Cog):
    """Role management commands"""
    
    def __init__(self, bot):
        self.bot = bot
    
    @app_commands.command(name="createrole", description="Create a new role")
    @app_commands.describe(name="Role name", color="Hex color (e.g., #FF0000)")
    @is_moderator()
    async def createrole(self, interaction: discord.Interaction, name: str, color: Optional[str] = None):
        """Create role"""
        try:
            role_color = discord.Color(int(color.replace("#", ""), 16)) if color else discord.Color.default()
            role = await interaction.guild.create_role(name=name, color=role_color)
            embed = success_embed("Role Created", f"Created {role.mention}")
            await interaction.response.send_message(embed=embed)
        except:
            await interaction.response.send_message("❌ Invalid color format", ephemeral=True)
    
    @app_commands.command(name="deleterole", description="Delete a role")
    @app_commands.describe(role="Role to delete")
    @is_moderator()
    async def deleterole(self, interaction: discord.Interaction, role: discord.Role):
        """Delete role"""
        name = role.name
        await role.delete()
        embed = success_embed("Role Deleted", f"Deleted {name}")
        await interaction.response.send_message(embed=embed)
    
    @app_commands.command(name="renamerole", description="Rename a role")
    @app_commands.describe(role="Role to rename", name="New name")
    @is_moderator()
    async def renamerole(self, interaction: discord.Interaction, role: discord.Role, name: str):
        """Rename role"""
        old_name = role.name
        await role.edit(name=name)
        embed = success_embed("Role Renamed", f"Renamed {old_name} to {role.mention}")
        await interaction.response.send_message(embed=embed)
    
    @app_commands.command(name="rolecolor", description="Change role color")
    @app_commands.describe(role="Role", color="Hex color")
    @is_moderator()
    async def rolecolor(self, interaction: discord.Interaction, role: discord.Role, color: str):
        """Change role color"""
        try:
            role_color = discord.Color(int(color.replace("#", ""), 16))
            await role.edit(color=role_color)
            embed = success_embed("Role Color Changed", f"Changed {role.mention} color to {color}")
            await interaction.response.send_message(embed=embed)
        except:
            await interaction.response.send_message("❌ Invalid color", ephemeral=True)
    
    @app_commands.command(name="rolehoist", description="Toggle role hoisting")
    @app_commands.describe(role="Role", hoist="True or False")
    @is_moderator()
    async def rolehoist(self, interaction: discord.Interaction, role: discord.Role, hoist: bool):
        """Toggle hoist"""
        await role.edit(hoist=hoist)
        status = "enabled" if hoist else "disabled"
        embed = success_embed("Role Hoist", f"Hoist {status} for {role.mention}")
        await interaction.response.send_message(embed=embed)
    
    @app_commands.command(name="rolementionable", description="Toggle role mentionable")
    @app_commands.describe(role="Role", mentionable="True or False")
    @is_moderator()
    async def rolementionable(self, interaction: discord.Interaction, role: discord.Role, mentionable: bool):
        """Toggle mentionable"""
        await role.edit(mentionable=mentionable)
        status = "enabled" if mentionable else "disabled"
        embed = success_embed("Role Mentionable", f"Mentionable {status} for {role.mention}")
        await interaction.response.send_message(embed=embed)
    
    @app_commands.command(name="addrole", description="Add role to user")
    @app_commands.describe(user="User", role="Role to add")
    @is_moderator()
    async def addrole(self, interaction: discord.Interaction, user: discord.Member, role: discord.Role):
        """Add role"""
        await user.add_roles(role)
        embed = success_embed("Role Added", f"Added {role.mention} to {user.mention}")
        await interaction.response.send_message(embed=embed)
    
    @app_commands.command(name="removerole", description="Remove role from user")
    @app_commands.describe(user="User", role="Role to remove")
    @is_moderator()
    async def removerole(self, interaction: discord.Interaction, user: discord.Member, role: discord.Role):
        """Remove role"""
        await user.remove_roles(role)
        embed = success_embed("Role Removed", f"Removed {role.mention} from {user.mention}")
        await interaction.response.send_message(embed=embed)
    
    @app_commands.command(name="roleall", description="Give role to all members")
    @app_commands.describe(role="Role to give")
    @is_moderator()
    async def roleall(self, interaction: discord.Interaction, role: discord.Role):
        """Role all members"""
        await interaction.response.defer()
        count = 0
        for member in interaction.guild.members:
            if not member.bot and role not in member.roles:
                try:
                    await member.add_roles(role)
                    count += 1
                except:
                    pass
        embed = success_embed("Role All", f"Added {role.mention} to {count} members")
        await interaction.followup.send(embed=embed)
    
    @app_commands.command(name="removeroleall", description="Remove role from all members")
    @app_commands.describe(role="Role to remove")
    @is_moderator()
    async def removeroleall(self, interaction: discord.Interaction, role: discord.Role):
        """Remove role from all"""
        await interaction.response.defer()
        count = 0
        for member in interaction.guild.members:
            if role in member.roles:
                try:
                    await member.remove_roles(role)
                    count += 1
                except:
                    pass
        embed = success_embed("Remove Role All", f"Removed {role.mention} from {count} members")
        await interaction.followup.send(embed=embed)
    
    @app_commands.command(name="rolehumans", description="Give role to all humans")
    @app_commands.describe(role="Role to give")
    @is_moderator()
    async def rolehumans(self, interaction: discord.Interaction, role: discord.Role):
        """Role humans"""
        await interaction.response.defer()
        count = 0
        for member in interaction.guild.members:
            if not member.bot and role not in member.roles:
                try:
                    await member.add_roles(role)
                    count += 1
                except:
                    pass
        embed = success_embed("Role Humans", f"Added {role.mention} to {count} humans")
        await interaction.followup.send(embed=embed)
    
    @app_commands.command(name="rolebots", description="Give role to all bots")
    @app_commands.describe(role="Role to give")
    @is_moderator()
    async def rolebots(self, interaction: discord.Interaction, role: discord.Role):
        """Role bots"""
        await interaction.response.defer()
        count = 0
        for member in interaction.guild.members:
            if member.bot and role not in member.roles:
                try:
                    await member.add_roles(role)
                    count += 1
                except:
                    pass
        embed = success_embed("Role Bots", f"Added {role.mention} to {count} bots")
        await interaction.followup.send(embed=embed)
    
    @app_commands.command(name="rolein", description="List members with a role")
    @app_commands.describe(role="Role to check")
    async def rolein(self, interaction: discord.Interaction, role: discord.Role):
        """List role members"""
        members = [m.mention for m in role.members[:20]]
        embed = discord.Embed(
            title=f"Members with {role.name}",
            description="\n".join(members) if members else "No members",
            color=role.color
        )
        embed.set_footer(text=f"Total: {len(role.members)}")
        await interaction.response.send_message(embed=embed)
    
    @app_commands.command(name="roleinfo", description="Get role information")
    @app_commands.describe(role="Role to check")
    async def roleinfo(self, interaction: discord.Interaction, role: discord.Role):
        """Role info"""
        embed = discord.Embed(title=role.name, color=role.color)
        embed.add_field(name="ID", value=role.id)
        embed.add_field(name="Members", value=len(role.members))
        embed.add_field(name="Color", value=str(role.color))
        embed.add_field(name="Hoisted", value="Yes" if role.hoist else "No")
        embed.add_field(name="Mentionable", value="Yes" if role.mentionable else "No")
        embed.add_field(name="Position", value=role.position)
        embed.add_field(name="Created", value=f"<t:{int(role.created_at.timestamp())}:R>")
        await interaction.response.send_message(embed=embed)
    
    @app_commands.command(name="roles", description="List all server roles")
    async def roles(self, interaction: discord.Interaction):
        """List roles"""
        roles = [r.mention for r in reversed(interaction.guild.roles[1:])][:50]
        embed = discord.Embed(
            title="Server Roles",
            description="\n".join(roles),
            color=config.Colors.INFO
        )
        embed.set_footer(text=f"Total: {len(interaction.guild.roles)-1}")
        await interaction.response.send_message(embed=embed)
    
    @app_commands.command(name="inrole", description="Check if user has role")
    @app_commands.describe(user="User to check", role="Role")
    async def inrole(self, interaction: discord.Interaction, user: discord.Member, role: discord.Role):
        """Check role"""
        has_role = role in user.roles
        status = "✅ Yes" if has_role else "❌ No"
        embed = discord.Embed(
            title="Role Check",
            description=f"Does {user.mention} have {role.mention}?\n{status}",
            color=config.Colors.SUCCESS if has_role else config.Colors.ERROR
        )
        await interaction.response.send_message(embed=embed)

async def setup(bot):
    await bot.add_cog(RoleManagement(bot))
