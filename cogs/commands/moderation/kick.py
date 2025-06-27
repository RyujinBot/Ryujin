import nextcord
from nextcord.ext import commands
from nextcord import SlashOption

class KickCog(commands.Cog):
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
        name="kick",
        description="Kick a member from the server.",
        default_member_permissions=nextcord.Permissions(kick_members=True)
    )
    async def kick(
        self,
        interaction: nextcord.Interaction,
        member: nextcord.Member = SlashOption(description="The user to kick"),
        reason: str = SlashOption(description="The reason for the kick")
    ):
        user_id = interaction.user.id
        is_blacklisted, blacklist_reason = self.check_blacklist(user_id)
        
        if is_blacklisted:
            embed = self.create_blacklist_embed(blacklist_reason)
            await interaction.send(embed=embed, ephemeral=True)
            return

        if not interaction.user.guild_permissions.kick_members:
            return await interaction.send("❌ You don't have permission to use this command.", ephemeral=True)

        if member == interaction.user:
            return await interaction.send("❌ You can't kick yourself.", ephemeral=True)

        if member.top_role >= interaction.user.top_role and interaction.user != interaction.guild.owner:
            return await interaction.send("❌ You can't kick someone with equal or higher role than yours.", ephemeral=True)

        try:
            try:
                dm_embed = nextcord.Embed(
                    title="You have been kicked",
                    description=f"You have been kicked from **{interaction.guild.name}**.\nReason: {reason}",
                    color=nextcord.Color.red()
                )
                dm_embed.set_footer(
                    text="© Ryujin Bot (2023-2025) | Moderation System",
                    icon_url=self.RYUJIN_LOGO
                )
                await member.send(embed=dm_embed)
            except nextcord.Forbidden:
                pass

            await member.kick(reason=reason)

            embed = nextcord.Embed(
                title="👢 Member Kicked",
                description=f"**{member.mention}** has been kicked.\nReason: {reason}",
                color=nextcord.Color.red()
            )
            embed.set_footer(
                text="© Ryujin Bot (2023-2025) | Moderation System",
                icon_url=self.RYUJIN_LOGO
            )
            await self.bot.maybe_send_ad(interaction)
            await interaction.send(embed=embed)

        except Exception as e:
            await interaction.send(f"❌ Failed to kick user: {e}", ephemeral=True)

def setup(bot):
    bot.add_cog(KickCog(bot))
