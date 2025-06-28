import nextcord
from nextcord.ext import commands
from nextcord import SlashOption
import logging
import asyncio

class RoleAll(commands.Cog):
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
        name="roleall",
        description="Add or remove a role from all users in the server. 📋",
        default_member_permissions=nextcord.Permissions(manage_roles=True)
    )
    async def roleall(
        self,
        interaction: nextcord.Interaction,
        action: str = SlashOption(
            name="action",
            description="Action to perform (add/remove)",
            required=True,
            choices={"add": "add", "remove": "remove"}
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
            members = [member for member in interaction.guild.members if not member.bot]
            if not members:
                await interaction.send("❌ No human members found in this server.", ephemeral=True)
                return
            
            embed = nextcord.Embed(
                title="⚠️ Confirm Role Addition",
                description=f"Are you sure you want to add {role.mention} to **{len(members)}** members? This action cannot be undone easily!",
                color=nextcord.Color.orange()
            )
            embed.add_field(name="Role", value=f"{role.mention} ({role.name})", inline=True)
            embed.add_field(name="Members", value=f"{len(members)} members", inline=True)
            embed.add_field(name="Excluded", value="Bots are excluded", inline=True)
            embed.set_footer(text="© Ryujin Bot (2023-2025) | Moderation System")
            embed.set_author(name="Ryujin", icon_url=self.bot.RYUJIN_LOGO)
            await interaction.send(embed=embed, ephemeral=True)
            
            success_count = 0
            failed_count = 0
            already_had_role = 0
            
            for member in members:
                try:
                    if role in member.roles:
                        already_had_role += 1
                    else:
                        await member.add_roles(role, reason=f"Role added to all by {interaction.user}")
                        success_count += 1
                    await asyncio.sleep(0.1)
                except Exception as e:
                    failed_count += 1
                    logging.error(f"Failed to add role to {member}: {e}")
            
            result_embed = nextcord.Embed(
                title="✅ Role Addition Complete",
                description=f"Successfully processed {len(members)} members",
                color=nextcord.Color.green()
            )
            result_embed.add_field(name="✅ Successfully Added", value=f"{success_count} members", inline=True)
            result_embed.add_field(name="❌ Failed", value=f"{failed_count} members", inline=True)
            result_embed.add_field(name="⚠️ Already Had Role", value=f"{already_had_role} members", inline=True)
            result_embed.add_field(name="Role", value=f"{role.mention} ({role.name})", inline=False)
            result_embed.add_field(name="Executed by", value=f"{interaction.user.mention}", inline=False)
            result_embed.set_footer(text="© Ryujin Bot (2023-2025) | Moderation System")
            result_embed.set_author(name="Ryujin", icon_url=self.bot.RYUJIN_LOGO)
            await interaction.followup.send(embed=result_embed, ephemeral=True)
            await self.bot.maybe_send_ad(interaction)
        elif action == "remove":
            members_with_role = [member for member in interaction.guild.members if not member.bot and role in member.roles]
            if not members_with_role:
                await interaction.send(f"❌ No human members have the {role.mention} role.", ephemeral=True)
                return
            
            embed = nextcord.Embed(
                title="⚠️ Confirm Role Removal",
                description=f"Are you sure you want to remove {role.mention} from **{len(members_with_role)}** members? This action cannot be undone easily!",
                color=nextcord.Color.orange()
            )
            embed.add_field(name="Role", value=f"{role.mention} ({role.name})", inline=True)
            embed.add_field(name="Members", value=f"{len(members_with_role)} members", inline=True)
            embed.add_field(name="Excluded", value="Bots are excluded", inline=True)
            embed.set_footer(text="© Ryujin Bot (2023-2025) | Moderation System")
            embed.set_author(name="Ryujin", icon_url=self.bot.RYUJIN_LOGO)
            await interaction.send(embed=embed, ephemeral=True)
            
            success_count = 0
            failed_count = 0
            
            for member in members_with_role:
                try:
                    await member.remove_roles(role, reason=f"Role removed from all by {interaction.user}")
                    success_count += 1
                    await asyncio.sleep(0.1)
                except Exception as e:
                    failed_count += 1
                    logging.error(f"Failed to remove role from {member}: {e}")
            
            result_embed = nextcord.Embed(
                title="✅ Role Removal Complete",
                description=f"Successfully processed {len(members_with_role)} members",
                color=nextcord.Color.green()
            )
            result_embed.add_field(name="✅ Successfully Removed", value=f"{success_count} members", inline=True)
            result_embed.add_field(name="❌ Failed", value=f"{failed_count} members", inline=True)
            result_embed.add_field(name="Role", value=f"{role.mention} ({role.name})", inline=False)
            result_embed.add_field(name="Executed by", value=f"{interaction.user.mention}", inline=False)
            result_embed.set_footer(text="© Ryujin Bot (2023-2025) | Moderation System")
            result_embed.set_author(name="Ryujin", icon_url=self.bot.RYUJIN_LOGO)
            await interaction.followup.send(embed=result_embed, ephemeral=True)
            await self.bot.maybe_send_ad(interaction)
        else:
            await interaction.send("❌ Invalid action. Use 'add' or 'remove'!", ephemeral=True)

def setup(bot):
    bot.add_cog(RoleAll(bot)) 