import nextcord
from nextcord.ext import commands
import os

class ScriptsListCog(commands.Cog):
    def __init__(self, bot):
        self.bot = bot
        self.RYUJIN_LOGO = "https://cdn.discordapp.com/avatars/1059400568805785620/63a77f852ea29f37961f458c53fb5a97.png"

    @nextcord.slash_command(
        name="scripts_list",
        description="Shows all the available scripts for After Effects"
    )
    async def scripts_list(self, interaction: nextcord.Interaction):
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

        subfolders = os.listdir("resources/scripts")
        subfolders = [folder.replace("_", " ") for folder in subfolders]
        
        subfolders.sort()
        
        files = "\n".join(f"**{i+1}**. {folder}" for i, folder in enumerate(subfolders))
        embed = nextcord.Embed(title="Scripts List")
        embed.description = files
        embed.add_field(name="How to use the command?", value="\n Example:\nIf you want to download `Flow Script`, you can just use: **/script 1**.")
        embed.set_footer(
            text="© Ryujin Bot (2023-2025) | Resources System",
            icon_url=self.RYUJIN_LOGO
        )
        await interaction.send(embed=embed, ephemeral=True)
        await self.bot.maybe_send_ad(interaction)

def setup(bot):
    bot.add_cog(ScriptsListCog(bot)) 