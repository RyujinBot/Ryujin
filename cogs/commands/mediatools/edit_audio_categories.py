import nextcord
from nextcord.ext import commands

class EditAudioCategoriesCog(commands.Cog):
    def __init__(self, bot):
        self.bot = bot
        self.RYUJIN_LOGO = "https://cdn.discordapp.com/avatars/1059400568805785620/63a77f852ea29f37961f458c53fb5a97.png"

    @nextcord.slash_command(
        name="edit_audio_categories",
        description="See the edit audio categories.",
    )
    async def edit_audio_categories(self, interaction: nextcord.Interaction):
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

        edit_audio_categories = ["dragonball", "fireforce", "naruto", "whooshes", "random"]
        categories_list = "\n".join(edit_audio_categories)
        
        embed = nextcord.Embed(title="Edit Audio Categories")
        embed.description = categories_list
        embed.set_footer(
            text="© Ryujin Bot (2023-2025) | Resources System",
            icon_url=self.RYUJIN_LOGO
        )
        await interaction.send("Have some Edit Audios?\n**Please join our discord server!** https://discord.gg/FSjRSaJ4bt", embed=embed, ephemeral=True)
        await self.bot.maybe_send_ad(interaction)

def setup(bot):
    bot.add_cog(EditAudioCategoriesCog(bot)) 