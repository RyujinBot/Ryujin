import nextcord
from nextcord.ext import commands
from nextcord import SlashOption
from datetime import timedelta

class TimeoutCog(commands.Cog):
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
        name="timeout",
        description="Timeout a user for a specific duration and reason.",
        default_member_permissions=nextcord.Permissions(moderate_members=True)
    )
    async def timeout(
        self,
        interaction: nextcord.Interaction,
        user: nextcord.Member = SlashOption(description="User to timeout"),
        duration: int = SlashOption(description="Duration in minutes"),
        reason: str = SlashOption(description="Reason for the timeout")
    ):
        user_id = interaction.user.id
        is_blacklisted, blacklist_reason = self.check_blacklist(user_id)
        
        if is_blacklisted:
            embed = self.create_blacklist_embed(blacklist_reason)
            await interaction.send(embed=embed, ephemeral=True)
            return

        if not interaction.user.guild_permissions.moderate_members:
            return await interaction.send("❌ You don't have permission to use this command.", ephemeral=True)

        if user.top_role >= interaction.user.top_role and interaction.user != interaction.guild.owner:
            return await interaction.send("❌ You can't timeout someone with equal or higher role than yours.", ephemeral=True)

        try:
            await user.timeout(timedelta(minutes=duration), reason=reason)

            embed = nextcord.Embed(
                title="⏱️ User Timed Out",
                description=f"**{user.mention}** has been timed out for **{duration}** minutes.\nReason: {reason}",
                color=nextcord.Color.red()
            )
            embed.set_footer(
                text="© Ryujin Bot (2023-2025) | Moderation System",
                icon_url=self.RYUJIN_LOGO
            )
            await self.bot.maybe_send_ad(interaction)
            await interaction.send(embed=embed)

        except Exception as e:
            await interaction.send(f"❌ Error: {e}", ephemeral=True)

    @nextcord.slash_command(
        name="remove_timeout",
        description="Remove timeout from a user.",
        default_member_permissions=nextcord.Permissions(moderate_members=True)
    )
    async def remove_timeout(
        self,
        interaction: nextcord.Interaction,
        user: nextcord.Member = SlashOption(description="User to remove timeout")
    ):
        user_id = interaction.user.id
        is_blacklisted, blacklist_reason = self.check_blacklist(user_id)
        
        if is_blacklisted:
            embed = self.create_blacklist_embed(blacklist_reason)
            await interaction.send(embed=embed, ephemeral=True)
            return

        if not interaction.user.guild_permissions.moderate_members:
            return await interaction.send("❌ You don't have permission to use this command.", ephemeral=True)

        try:
            await user.timeout(None)

            embed = nextcord.Embed(
                title="✅ Timeout Removed",
                description=f"Timeout has been removed for {user.mention}.",
                color=nextcord.Color.green()
            )
            embed.set_footer(
                text="© Ryujin Bot (2023-2025) | Moderation System",
                icon_url=self.RYUJIN_LOGO
            )
            await self.bot.maybe_send_ad(interaction)
            await interaction.send(embed=embed)

        except Exception as e:
            await interaction.send(f"❌ Error: {e}", ephemeral=True)

def setup(bot):
    bot.add_cog(TimeoutCog(bot))
