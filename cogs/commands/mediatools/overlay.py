import nextcord
from nextcord.ext import commands
import os
import random

class OverlayCog(commands.Cog):
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
        name="overlay",
        description="Sends a random overlay!",
    )
    async def overlay(self, interaction: nextcord.Interaction):
        user_id = interaction.user.id
        is_blacklisted, reason = self.check_blacklist(user_id)
        
        if is_blacklisted:
            embed = self.create_blacklist_embed(reason)
            await interaction.send(embed=embed, ephemeral=True)
            return

        assets = [f for f in os.listdir("resources/overlays") if f.endswith(".mp4")]
        if not assets:
            await interaction.send("No overlays found.", ephemeral=True)
            return

        asset = random.choice(assets)
        file_path = os.path.join("resources/overlays", asset)
        
        button_view = AnotherButton()
        await self.bot.maybe_send_ad(interaction)
        await interaction.send(file=nextcord.File(file_path), view=button_view, ephemeral=True)

class AnotherButton(nextcord.ui.View):
    def __init__(self):
        super().__init__()

    @nextcord.ui.button(label="Another One 👀", style=nextcord.ButtonStyle.gray)
    async def create_ronde(self, button: nextcord.ui.Button, interaction: nextcord.Interaction):
        global current_overlay
        assets = [f for f in os.listdir("resources/overlays") if f.endswith(".mp4")]
        new_overlay = random.choice(assets)
        while new_overlay == current_overlay:
            new_overlay = random.choice(assets)
        current_overlay = new_overlay
        file_path = os.path.join("resources/overlays", current_overlay)
        await interaction.response.edit_message(file=nextcord.File(file_path))

def setup(bot):
    bot.add_cog(OverlayCog(bot))
