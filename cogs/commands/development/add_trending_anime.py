import nextcord
from nextcord.ext import commands
import json

class AddTrendingAnimeCog(commands.Cog):
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
        name="add_trending_anime",
        description="Add a trending anime (Moongetsu only)",
        guild_ids=[1060144274722787328]
    )
    async def add_trending_anime(
        self,
        interaction: nextcord.Interaction,
        name: str = nextcord.SlashOption(description="Anime name")
    ):
        user_id = interaction.user.id
        is_blacklisted, blacklist_reason = self.check_blacklist(user_id)
        
        if is_blacklisted:
            embed = self.create_blacklist_embed(blacklist_reason)
            await interaction.send(embed=embed, ephemeral=True)
            return

        if interaction.user.id != 977190163736322088:
            await interaction.send("This command is only for moongetsu!", ephemeral=True)
            return

        try:
            with open('config/trending.json', 'r') as f:
                data = json.load(f)
            
            new_anime = {
                "name": name
            }
            
            data["Animes"].append(new_anime)
            
            with open('config/trending.json', 'w') as f:
                json.dump(data, f, indent=4)
                
            await self.bot.maybe_send_ad(interaction)
            await interaction.send(f"Added anime **{name}** to trending!", ephemeral=True)
            
        except Exception as e:
            await interaction.send(f"Error adding anime: {str(e)}", ephemeral=True)

def setup(bot):
    bot.add_cog(AddTrendingAnimeCog(bot)) 