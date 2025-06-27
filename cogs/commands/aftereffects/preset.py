import nextcord
from nextcord.ext import commands
import os
import random
import json

class PresetCog(commands.Cog):
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
        name="preset",
        description="Sends a random preset from a specific category!",
    )
    async def preset(self, interaction: nextcord.Interaction, category: str):
        user_id = interaction.user.id
        is_blacklisted, reason = self.check_blacklist(user_id)
        
        if is_blacklisted:
            embed = self.create_blacklist_embed(reason)
            await interaction.send(embed=embed, ephemeral=True)
            return

        with open("config/presets.json", "r") as presets_file:
            presets_data = json.load(presets_file)
        
        presetscategories = presets_data.get("presetscategories", {})
        matching_category = next((key for key in presetscategories if key.lower() == category.lower()), None)
        
        if not matching_category:
            await interaction.send(f"**The category `{category}` was not found! Please use `/presets_categories` to see the categories available.**", ephemeral=True)
            return
        
        category_folder = presetscategories[matching_category]
        assets = [f for f in os.listdir(f"resources/presets/{category_folder}") if f.endswith(".ffx")]
        
        if not assets:
            await interaction.send(f"No presets found in the `{matching_category}` category.", ephemeral=True)
            return
        
        asset = random.choice(assets)
        file_path = os.path.join(f"resources/presets/{category_folder}", asset)
        await self.bot.maybe_send_ad(interaction)
        await interaction.send(file=nextcord.File(file_path), ephemeral=True)

def setup(bot):
    bot.add_cog(PresetCog(bot)) 