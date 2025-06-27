import nextcord
from nextcord.ext import commands

class DonateCog(commands.Cog):
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
        name="donate",
        description="Support the development of Ryujin"
    )
    async def donate(self, interaction: nextcord.Interaction):
        user_id = interaction.user.id
        is_blacklisted, reason = self.check_blacklist(user_id)
        
        if is_blacklisted:
            embed = self.create_blacklist_embed(reason)
            await interaction.send(embed=embed, ephemeral=True)
            return

        embed = nextcord.Embed(
            title="Support the development of Ryujin",
            description="If you want to support the development of Ryujin, you can donate by clicking the button below.",
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
        view.add_item(nextcord.ui.Button(label="Donate", url="https://ko-fi.com/ryujinsupport", style=nextcord.ButtonStyle.link))
        
        await self.bot.maybe_send_ad(interaction)
        await interaction.send(embed=embed, view=view, ephemeral=True)

def setup(bot):
    bot.add_cog(DonateCog(bot)) 