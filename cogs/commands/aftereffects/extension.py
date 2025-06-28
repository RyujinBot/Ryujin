import nextcord
from nextcord.ext import commands
import os
import json

class ExtensionCog(commands.Cog):
    def __init__(self, bot):
        self.bot = bot
        self.RYUJIN_LOGO = "https://cdn.discordapp.com/avatars/1059400568805785620/63a77f852ea29f37961f458c53fb5a97.png"

    @nextcord.slash_command(
        name="extension",
        description="Sends an extension for After Effects.",
    )
    async def extension(self, interaction: nextcord.Interaction, extension_number: int):
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

        extension_files_dir = "resources/extensions"
        
        with open("config/extensions.json", "r") as json_file:
            extension_files = json.load(json_file)
        
        try:
            extension_name = extension_files.get(str(extension_number))
        except KeyError:
            return await interaction.send(f"No extension found with number {extension_number}.", ephemeral=True)

        extension_path = os.path.join(extension_files_dir, extension_name.replace(" ", "_"))

        if os.path.exists(extension_path):
            extension_file = None
            preview_link = None
            
            for root, dirs, files in os.walk(extension_path):
                for file in files:
                    if file.endswith((".zip", ".rar", ".jsx")):
                        extension_file = os.path.join(root, file)
                    if file == "preview.txt":
                        with open(os.path.join(root, file), "r") as f:
                            preview_link = f.read().strip()

            if extension_file and preview_link:
                await interaction.send(f"{preview_link}", file=nextcord.File(extension_file), ephemeral=True)
                await self.bot.maybe_send_ad(interaction)
            else:
                await interaction.send(f"Extension file or preview link not found for {extension_name}.", ephemeral=True)
        else:
            await interaction.send(f"The specified extension file for {extension_name} does not exist.", ephemeral=True)

def setup(bot):
    bot.add_cog(ExtensionCog(bot)) 