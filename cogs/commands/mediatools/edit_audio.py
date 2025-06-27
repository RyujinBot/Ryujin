import nextcord
from nextcord.ext import commands
import os
import random

class EditAudioCog(commands.Cog):
    def __init__(self, bot):
        self.bot = bot
        self.RYUJIN_LOGO = "https://cdn.discordapp.com/avatars/1059400568805785620/63a77f852ea29f37961f458c53fb5a97.png"

    @nextcord.slash_command(
        name="edit_audio",
        description="Sends a random edit audio!",
    )
    async def edit_audio(self, interaction: nextcord.Interaction, category: str):
        user_id = interaction.user.id
        if hasattr(self.bot, 'blacklist') and user_id in self.bot.blacklist:
            embed = nextcord.Embed(
                title="You are blacklisted!",
                description=f"**You can't use Ryujin's commands anymore because you have been blacklisted for `{self.bot.blacklist[user_id]}`.**",
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
            await interaction.send(embed=embed, ephemeral=True)
            return

        edit_audio_categories = {
            "dragonball": "dragonball",
            "fireforce": "fireforce", 
            "naruto": "naruto",
            "whooshes": "whooshes",
            "random": "random"
        }

        if category not in edit_audio_categories:
            await interaction.send(f"**The category `{category}` was not found! Please use `/edit_audio_categories` to see the categories available.**", ephemeral=True)
            return

        assets = [f for f in os.listdir(f"resources/edit audios/{category}") if f.endswith(".mp3")]
        if not assets:
            await interaction.send(f"No edit audios found in the `{category}` category.", ephemeral=True)
            return

        asset = random.choice(assets)
        file_path = os.path.join(f"resources/edit audios/{category}", asset)
        await interaction.send(file=nextcord.File(file_path), ephemeral=True)
        await self.bot.maybe_send_ad(interaction)

def setup(bot):
    bot.add_cog(EditAudioCog(bot)) 