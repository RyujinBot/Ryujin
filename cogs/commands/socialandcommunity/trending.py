import nextcord
from nextcord.ext import commands
import json

class TrendingCog(commands.Cog):
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
        name="trending",
        description="See what's trending in AMV Community!"
    )
    async def trending(self, interaction: nextcord.Interaction):
        user_id = interaction.user.id
        is_blacklisted, reason = self.check_blacklist(user_id)
        
        if is_blacklisted:
            embed = self.create_blacklist_embed(reason)
            await interaction.send(embed=embed, ephemeral=True)
            return

        try:
            with open('config/trending.json', 'r') as f:
                trending_data = json.load(f)
            
            description = "Here's what's currently trending in the AMV community:\n\n"
            description += "🎵 **Trending Songs in AMVs**\n"
            
            for song in trending_data["Songs"]:
                description += f"» **{song['name']}**\n"
                description += f"Original: [YouTube]({song['link']})\n"
                description += f"Popular Edit: [YouTube]({song['popular-edit']})\n\n"
            
            description += "📺 **Trending Anime**\n"
            for anime in trending_data["Animes"]:
                description += f"» **{anime['name']}**\n"
            
            embed = nextcord.Embed(
                title="📈 AMV Community Trends",
                description=description,
                color=0x2a2a2a
            )
            
            embed.set_footer(
                text="© Ryujin Bot (2023-2025) | Social & Community System",
                icon_url=self.RYUJIN_LOGO
            )
            
            embed.set_author(
                name="Ryujin",
                icon_url=self.RYUJIN_LOGO
            )
            await self.bot.maybe_send_ad(interaction)
            await interaction.send(embed=embed, ephemeral=True)
        except Exception as e:
            error_embed = nextcord.Embed(
                title="❌ Error",
                description="Could not fetch trending data. Please try again later.",
                color=nextcord.Color.red()
            )
            await interaction.send(embed=error_embed, ephemeral=True)

def setup(bot):
    bot.add_cog(TrendingCog(bot)) 