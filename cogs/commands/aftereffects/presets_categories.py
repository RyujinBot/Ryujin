import nextcord
from nextcord.ext import commands
import json

class PresetsCategoriesCog(commands.Cog):
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
        name="presets_categories",
        description="See the presets categories.",
    )
    async def presets_categories(self, interaction: nextcord.Interaction):
        user_id = interaction.user.id
        is_blacklisted, reason = self.check_blacklist(user_id)
        
        if is_blacklisted:
            embed = self.create_blacklist_embed(reason)
            await interaction.send(embed=embed, ephemeral=True)
            return

        with open("config/presets.json", "r") as presets_file:
            presets_data = json.load(presets_file)
        
        presetscategories = presets_data.get("presetscategories", {})
        categories = list(presetscategories.keys())
        categories_list = "\n".join(categories)
        
        embed = nextcord.Embed(title="Presets Categories")
        embed.description = categories_list
        embed.set_footer(
            text="© Ryujin Bot (2023-2025) | After Effects System",
            icon_url=self.RYUJIN_LOGO
        )
        await self.bot.maybe_send_ad(interaction)
        await interaction.send("Have some presets?\n**Please join our discord server!** https://discord.gg/FSjRSaJ4bt", embed=embed, ephemeral=True)

def setup(bot):
    bot.add_cog(PresetsCategoriesCog(bot)) 