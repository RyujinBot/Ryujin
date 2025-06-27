import nextcord
from nextcord.ext import commands
import os
import json

class ProjectFileCog(commands.Cog):
    def __init__(self, bot):
        self.bot = bot
        self.RYUJIN_LOGO = "https://cdn.discordapp.com/avatars/1059400568805785620/63a77f852ea29f37961f458c53fb5a97.png"

    @nextcord.slash_command(
        name="project_file",
        description="Sends a project file and a preview link.",
    )
    async def project_file(self, interaction: nextcord.Interaction, project_number: int):
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

        project_files_dir = "resources/project_files"
        
        # Load project files data
        with open("config/project_files.json", "r") as json_file:
            project_files = json.load(json_file)
        
        try:
            project_name = project_files.get(str(project_number))
        except KeyError:
            return await interaction.send(f"No project file found with number {project_number}.", ephemeral=True)
        
        project_path = os.path.join(project_files_dir, project_name.replace(" ", "_"))
        
        if os.path.exists(project_path):
            aep_file = None
            preview_link = None
            
            for root, dirs, files in os.walk(project_path):
                for file in files:
                    if file.endswith(".aep"):
                        aep_file = os.path.join(root, file)
                    if file == "preview.txt":
                        with open(os.path.join(root, file), "r") as f:
                            preview_link = f.read().strip()
            
            if aep_file and preview_link:
                await interaction.send(f"{preview_link}", file=nextcord.File(aep_file), ephemeral=True)
                await self.bot.maybe_send_ad(interaction)
            else:
                await interaction.send(f"Project file or preview link not found for {project_name}.", ephemeral=True)
        else:
            await interaction.send(f"The specified project files for {project_name} do not exist.", ephemeral=True)

def setup(bot):
    bot.add_cog(ProjectFileCog(bot)) 