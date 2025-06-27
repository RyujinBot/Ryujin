import nextcord
from nextcord.ext import commands
import os
import random

class SfxCog(commands.Cog):
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
        name="sfx",
        description="Sends a random SFX!",
    )
    async def sfx(self, interaction: nextcord.Interaction, category: str):
        user_id = interaction.user.id
        is_blacklisted, reason = self.check_blacklist(user_id)
        
        if is_blacklisted:
            embed = self.create_blacklist_embed(reason)
            await interaction.send(embed=embed, ephemeral=True)
            return

        if category not in self.sfxcategories:
            await interaction.send(f"**The category `{category}` was not found! Please use `/sfx_categories` to see the categories available.**")
            return

        assets = [f for f in os.listdir(f"resources/sfx/{category}") if f.endswith(".mp3")]
        asset = random.choice(assets)
        file_path = os.path.join(f"resources/sfx/{category}", asset)
        await self.bot.maybe_send_ad(interaction)
        await interaction.send(file=nextcord.File(file_path), ephemeral=True)

def setup(bot):
    bot.add_cog(SfxCog(bot)) 