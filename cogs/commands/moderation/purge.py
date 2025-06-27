import nextcord
from nextcord.ext import commands
from nextcord import SlashOption

class PurgeCog(commands.Cog):
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
        name="purge",
        description="Delete a certain number of messages from a channel."
    )
    async def purge(
        self,
        interaction: nextcord.Interaction,
        messages: int = SlashOption(
            name="messages",
            description="The number of messages to delete (max 100).",
            required=True
        )
    ):
        user_id = interaction.user.id
        is_blacklisted, blacklist_reason = self.check_blacklist(user_id)
        
        if is_blacklisted:
            embed = self.create_blacklist_embed(blacklist_reason)
            await interaction.send(embed=embed, ephemeral=True)
            return

        await interaction.response.defer(ephemeral=True)

        if not interaction.user.guild_permissions.manage_messages:
            return await interaction.send("❌ You don't have permission to use this command.", ephemeral=True)

        if messages < 1 or messages > 100:
            return await interaction.send("❌ You must specify between 1 and 100 messages.", ephemeral=True)

        try:
            deleted = await interaction.channel.purge(limit=messages)
            embed = nextcord.Embed(
                title="🧹 Messages Purged",
                description=f"Successfully deleted `{len(deleted)}` messages from {interaction.channel.mention}.",
                color=nextcord.Color.red()
            )
            embed.set_footer(
                text="© Ryujin Bot (2023-2025) | Moderation System", icon_url=self.RYUJIN_LOGO)

            if interaction.guild.icon:
                embed.set_author(
                    name=interaction.guild.name, 
                    icon_url=interaction.guild.icon.url
                )
            else:
                embed.set_author(
                    name="Ryujin", 
                    icon_url=self.RYUJIN_LOGO
            )

            await self.bot.maybe_send_ad(interaction)
            await interaction.send(embed=embed, ephemeral=True)

        except Exception as e:
            await interaction.send(f"❌ Failed to purge messages: `{e}`", ephemeral=True)

def setup(bot):
    bot.add_cog(PurgeCog(bot))
