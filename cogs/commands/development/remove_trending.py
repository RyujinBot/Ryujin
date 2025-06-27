import nextcord
from nextcord.ext import commands
import json

class RemoveTrendingCog(commands.Cog):
    def __init__(self, bot):
        self.bot = bot
        self.RYUJIN_LOGO = "https://cdn.discordapp.com/avatars/1059400568805785620/63a77f852ea29f37961f458c53fb5a97.png"

    @nextcord.slash_command(
        name="remove_trending",
        description="Remove a trending item (Moongetsu only)",
        guild_ids=[1060144274722787328]
    )
    async def remove_trending(
        self,
        interaction: nextcord.Interaction,
        type: str = nextcord.SlashOption(choices=["song", "anime"], description="Type to remove"),
        name: str = nextcord.SlashOption(description="Name of item to remove")
    ):
        if interaction.user.id != 977190163736322088:
            await interaction.send("This command is only for moongetsu!", ephemeral=True)
            return

        try:
            with open('config/trending.json', 'r') as f:
                data = json.load(f)
            
            if type == "song":
                data["Songs"] = [s for s in data["Songs"] if s["name"] != name]
                item_type = "song"
            else:
                data["Animes"] = [a for a in data["Animes"] if a["name"] != name]
                item_type = "anime"
            
            with open('config/trending.json', 'w') as f:
                json.dump(data, f, indent=4)
                
            await interaction.send(f"Removed {item_type} **{name}** from trending!", ephemeral=True)
            
        except Exception as e:
            await interaction.send(f"Error removing item: {str(e)}", ephemeral=True)

def setup(bot):
    bot.add_cog(RemoveTrendingCog(bot)) 