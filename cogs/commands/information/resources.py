import nextcord
from nextcord.ext import commands
import os

class ResourcesCog(commands.Cog):
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
        name="resources",
        description="See the editing resources that the bot has.",
    )
    async def resources(self, interaction: nextcord.Interaction):
        user_id = interaction.user.id
        is_blacklisted, reason = self.check_blacklist(user_id)
        
        if is_blacklisted:
            embed = self.create_blacklist_embed(reason)
            await interaction.send(embed=embed, ephemeral=True)
            return

        overlays = len([f for f in os.listdir("resources/overlays") if f.endswith(".mp4")])
        edit_audios_categories = len(os.listdir("resources/edit audios"))
        with open("edits.txt", "r") as f:
            edits = len(f.read().strip().split("\n"))
        
        stats = nextcord.Embed(title="Resources", description=f"**Number of resouces that `Ryujin Editing Bot` has:**\n\n**Overlays:** {overlays}\n**Edit audios categories:** {edit_audios_categories}\n**Edits:** {edits}")
        stats.set_footer(
            text="© Ryujin Bot (2023-2025) | Information System",
            icon_url=self.RYUJIN_LOGO
        )
        stats.set_author(name="Ryujin", icon_url=self.RYUJIN_LOGO)
        
        await self.bot.maybe_send_ad(interaction)
        await interaction.send(embed=stats, ephemeral=True)

def setup(bot):
    bot.add_cog(ResourcesCog(bot)) 