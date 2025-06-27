import nextcord
from nextcord.ext import commands

class BugCog(commands.Cog):
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
        name="bug",
        description="Report a bug to the Ryujin team"
    )
    async def bug(self, interaction: nextcord.Interaction):
        user_id = interaction.user.id
        is_blacklisted, reason = self.check_blacklist(user_id)
        
        if is_blacklisted:
            embed = self.create_blacklist_embed(reason)
            await interaction.send(embed=embed, ephemeral=True)
            return

        embed = nextcord.Embed(
            title="Report a bug to the Ryujin team",
            description="If you want to report a bug, you need to join the support server and report it in the `🐞〢bugs` channel.",
            color=0x2a2a2a
        )
        embed.set_footer(
            text="© Ryujin Bot (2023-2025) | Information System",
            icon_url=self.RYUJIN_LOGO
        )
        embed.set_author(
            name="Ryujin",
            icon_url=self.RYUJIN_LOGO
        )
        view = nextcord.ui.View()
        view.add_item(nextcord.ui.Button(label="Support Server", url="https://discord.gg/FSjRSaJ4bt", style=nextcord.ButtonStyle.link))
        
        await self.bot.maybe_send_ad(interaction)
        await interaction.send(embed=embed, view=view, ephemeral=True)

def setup(bot):
    bot.add_cog(BugCog(bot)) 