import nextcord
from nextcord.ext import commands
from nextcord import SlashOption
import logging

class Role(commands.Cog):
    def __init__(self, bot):
        self.bot = bot

    def check_blacklist(self, user_id):
        """Check if user is blacklisted"""
        if hasattr(self.bot, 'blacklist'):
            return user_id in self.bot.blacklist, self.bot.blacklist.get(user_id)
        return False, None

    def create_blacklist_embed(self, reason):
        """Create blacklist embed"""
        embed = nextcord.Embed(
            title="You are blacklisted!",
            description=f"**You can't use Ryujin's functions anymore because you have been blacklisted for `{reason}`.**",
            color=nextcord.Color.red()
        )
        embed.set_footer(text="© Ryujin Bot (2023-2025) | Blacklist System")
        embed.set_author(
            name="Ryujin",
            icon_url=self.bot.RYUJIN_LOGO
        )
        return embed

    @nextcord.slash_command(
        name="role",
        description="Add or remove a role from a user. 📋",
        default_member_permissions=nextcord.Permissions(manage_roles=True)
    )
    async def role(
        self,
        interaction: nextcord.Interaction,
        action: str = SlashOption(
            name="action",
            description="Action to perform (add/remove)",
            required=True,
            choices={"add": "add", "remove": "remove"}
        ),
        user: nextcord.Member = SlashOption(
            name="user",
            description="The user to add/remove the role to/from",
            required=True
        ),
        role: nextcord.Role = SlashOption(
            name="role",
            description="The role to add or remove",
            required=True
        )
    ):
        is_blacklisted, reason = self.check_blacklist(interaction.user.id)
        if is_blacklisted:
            embed = self.create_blacklist_embed(reason)
            await interaction.send(embed=embed, ephemeral=True)
            return

        if not interaction.user.guild_permissions.manage_roles:
            await interaction.send("❌ You don't have permission to use this command.", ephemeral=True)
            return

        if role >= interaction.guild.me.top_role:
            await interaction.send("❌ I cannot manage this role because it's higher than or equal to my highest role.", ephemeral=True)
            return

        if action == "add":
            if role in user.roles:
                await interaction.send(f"❌ {user.mention} already has the {role.mention} role.", ephemeral=True)
                return
            try:
                await user.add_roles(role, reason=f"Role added by {interaction.user}")
                embed = nextcord.Embed(
                    title="✅ Role Added Successfully",
                    description=f"Successfully added {role.mention} to {user.mention}",
                    color=nextcord.Color.green()
                )
                embed.add_field(name="User", value=f"{user.mention} ({user.name})", inline=True)
                embed.add_field(name="Role", value=f"{role.mention} ({role.name})", inline=True)
                embed.add_field(name="Added by", value=f"{interaction.user.mention}", inline=True)
                embed.set_footer(text="© Ryujin Bot (2023-2025) | Moderation System")
                embed.set_author(name="Ryujin", icon_url=self.bot.RYUJIN_LOGO)
                await interaction.send(embed=embed, ephemeral=True)
                await self.bot.maybe_send_ad(interaction)
            except Exception as e:
                await interaction.send(f"❌ Failed to add role: `{e}`", ephemeral=True)
        elif action == "remove":
            user_roles = [r.id for r in user.roles]
            if role.id not in user_roles:
                await interaction.send(f"❌ {user.mention} doesn't have the {role.mention} role.", ephemeral=True)
                return
            try:
                await user.remove_roles(role, reason=f"Role removed by {interaction.user}")
                embed = nextcord.Embed(
                    title="✅ Role Removed Successfully",
                    description=f"Successfully removed {role.mention} from {user.mention}",
                    color=nextcord.Color.green()
                )
                embed.add_field(name="User", value=f"{user.mention} ({user.name})", inline=True)
                embed.add_field(name="Role", value=f"{role.mention} ({role.name})", inline=True)
                embed.add_field(name="Removed by", value=f"{interaction.user.mention}", inline=True)
                embed.set_footer(text="© Ryujin Bot (2023-2025) | Moderation System")
                embed.set_author(name="Ryujin", icon_url=self.bot.RYUJIN_LOGO)
                await interaction.send(embed=embed, ephemeral=True)
                await self.bot.maybe_send_ad(interaction)
            except Exception as e:
                await interaction.send(f"❌ Failed to remove role: `{e}`", ephemeral=True)
        else:
            await interaction.send("❌ Invalid action. Use 'add' or 'remove'!", ephemeral=True)

def setup(bot):
    bot.add_cog(Role(bot)) 