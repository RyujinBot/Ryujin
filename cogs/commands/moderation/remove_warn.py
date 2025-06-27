import nextcord
from nextcord.ext import commands
from cogs.utils.db import remove_warning, get_user_warnings, get_warning_count

class RemoveWarnCog(commands.Cog):
    def __init__(self, bot):
        self.bot = bot
        self.RYUJIN_LOGO = "https://cdn.discordapp.com/avatars/1059400568805785620/63a77f852ea29f37961f458c53fb5a97.png"

    def check_blacklist(self, user_id):
        if hasattr(self.bot, 'blacklist') and user_id in self.bot.blacklist:
            return True, self.bot.blacklist[user_id]
        return False, None

    def create_blacklist_embed(self, reason):
        embed = nextcord.Embed(
            title="You are blacklisted!",
            description=f"**You can't use Ryujin's commands anymore because you have been blacklisted for `{reason}`.**",
            color=nextcord.Color.red()
        )
        embed.set_footer(
            text="© Ryujin Bot (2023-2025) | Blacklist System",
            icon_url=self.RYUJIN_LOGO
        )
        
        embed.set_author(
            name="Ryujin",
            icon_url=self.RYUJIN_LOGO
        )
        return embed

    @nextcord.slash_command(
        name="remove_warn",
        description="Remove a specific warning from a member.",
        default_member_permissions=nextcord.Permissions(manage_messages=True)
    )
    async def remove_warn(
        self,
        interaction: nextcord.Interaction,
        warn_number: int = nextcord.SlashOption(
            name="warn_number",
            description="The warning ID number to remove",
            required=True
        ),
        user: nextcord.Member = nextcord.SlashOption(
            name="user",
            description="The user to remove the warning from",
            required=True
        ),
        reason: str = nextcord.SlashOption(
            name="reason",
            description="Reason for removing the warning",
            required=False
        )
    ):
        user_id = interaction.user.id
        is_blacklisted, blacklist_reason = self.check_blacklist(user_id)
        
        if is_blacklisted:
            embed = self.create_blacklist_embed(blacklist_reason)
            await interaction.send(embed=embed, ephemeral=True)
            return

        # Check permissions
        if not interaction.user.guild_permissions.manage_messages:
            await interaction.send(
                "❌ You don't have permission to remove warnings.",
                ephemeral=True
            )
            return

        # Check role hierarchy
        if user.top_role >= interaction.user.top_role:
            await interaction.send(
                "❌ You can't remove warnings from this user due to role hierarchy.",
                ephemeral=True
            )
            return

        # Validate warn number
        if warn_number <= 0:
            await interaction.send(
                "❌ Warning number must be a positive integer.",
                ephemeral=True
            )
            return

        try:
            # Get user's warnings to verify the warning exists
            user_warnings = await get_user_warnings(
                self.bot.connection,
                interaction.guild.id,
                user.id
            )

            # Check if warning exists
            warning_exists = any(warning[0] == warn_number for warning in user_warnings)
            
            if not warning_exists:
                await interaction.send(
                    f"❌ Warning #{warn_number} not found for {user.mention}.",
                    ephemeral=True
                )
                return

            # Prepare reason
            remove_reason = reason or "No reason provided"

            # Remove the warning
            success = await remove_warning(
                self.bot.connection,
                warn_number,
                interaction.guild.id,
                remove_reason
            )

            if not success:
                await interaction.send(
                    "❌ Failed to remove warning from database.",
                    ephemeral=True
                )
                return

            # Get updated warning count
            total_warnings = await get_warning_count(
                self.bot.connection,
                interaction.guild.id,
                user.id
            )

            # Create success embed
            embed = nextcord.Embed(
                title="✅ Warning Removed",
                description=f"Warning #{warn_number} has been removed from **{user.mention}**.\n\n"
                          f"**User:** {user.mention} ({user.name})\n"
                          f"**Removed by:** {interaction.user.mention} ({interaction.user.name})\n"
                          f"**Reason:** {remove_reason}\n"
                          f"**Remaining Warnings:** {total_warnings}",
                color=nextcord.Color.green()
            )
            
            embed.set_footer(
                text="© Ryujin Bot (2023-2025) | Moderation System",
                icon_url=self.RYUJIN_LOGO
            )
            
            embed.set_author(
                name="Ryujin",
                icon_url=self.RYUJIN_LOGO
            )

            await self.bot.maybe_send_ad(interaction)
            await interaction.send(embed=embed, ephemeral=True)

        except Exception as e:
            await interaction.send(
                f"❌ An error occurred while removing the warning: `{e}`",
                ephemeral=True
            )

def setup(bot):
    bot.add_cog(RemoveWarnCog(bot)) 