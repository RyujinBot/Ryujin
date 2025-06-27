import nextcord
from nextcord.ext import commands

class SfxCategoriesCog(commands.Cog):
    def __init__(self, bot):
        self.bot = bot
        self.RYUJIN_LOGO = "https://cdn.discordapp.com/avatars/1059400568805785620/63a77f852ea29f37961f458c53fb5a97.png"
        self.sfxcategories = {
            "dragonball": "dragonball",
            "fireforce": "fireforce",
            "naruto": "naruto",
            "whooshes": "whooshes",
            "random": "random"
        }

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
        name="sfx_categories",
        description="See the SFX categories.",
    )
    async def sfx_categories(self, interaction: nextcord.Interaction):
        user_id = interaction.user.id
        is_blacklisted, reason = self.check_blacklist(user_id)
        
        if is_blacklisted:
            embed = self.create_blacklist_embed(reason)
            await interaction.send(embed=embed, ephemeral=True)
            return

        embed = nextcord.Embed(title="SFX Categories")
        embed.description = "\n".join(self.sfxcategories)
        embed.set_footer(
            text="© Ryujin Bot (2023-2025) | Media Tools System",
            icon_url=self.RYUJIN_LOGO
        )
        await self.bot.maybe_send_ad(interaction)
        await interaction.send("Have some SFX?\n**Please join our discord server!** https://discord.gg/FSjRSaJ4bt", embed=embed, ephemeral=True)

def setup(bot):
    bot.add_cog(SfxCategoriesCog(bot)) 