import nextcord
from nextcord.ext import commands
import json

class AddTrendingSongCog(commands.Cog):
    def __init__(self, bot):
        self.bot = bot
        self.RYUJIN_LOGO = "https://cdn.discordapp.com/avatars/1059400568805785620/63a77f852ea29f37961f458c53fb5a97.png"

    @nextcord.slash_command(
        name="add_trending_song",
        description="Add a trending song (Moongetsu only)",
        guild_ids=[1060144274722787328]
    )
    async def add_trending_song(
        self,
        interaction: nextcord.Interaction,
        name: str = nextcord.SlashOption(description="Song name"),
        link: str = nextcord.SlashOption(description="Original song YouTube link"),
        popular_edit: str = nextcord.SlashOption(description="Popular edit YouTube link")
    ):
        if interaction.user.id != 977190163736322088:
            await interaction.send("This command is only for moongetsu!", ephemeral=True)
            return

        try:
            with open('config/trending.json', 'r') as f:
                data = json.load(f)
            
            new_song = {
                "name": name,
                "link": link,
                "popular-edit": popular_edit
            }
            
            data["Songs"].append(new_song)
            
            with open('config/trending.json', 'w') as f:
                json.dump(data, f, indent=4)
                
            await interaction.send(f"Added song **{name}** to trending!", ephemeral=True)
            
        except Exception as e:
            await interaction.send(f"Error adding song: {str(e)}", ephemeral=True)

def setup(bot):
    bot.add_cog(AddTrendingSongCog(bot)) 