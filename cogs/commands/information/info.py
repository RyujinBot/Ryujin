import nextcord
from nextcord.ext import commands

class InfoCog(commands.Cog):
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

    def create_info_embed(self):
        embed = nextcord.Embed(
            title="About Ryujin",
            description="Ryujin is a powerful Discord bot designed for content creators and editors. It provides various tools for media processing, After Effects resources, and community features.",
            color=0x2a2a2a
        )
        embed.add_field(
            name="Features",
            value="• Media Processing (Nightcore, Sped Up, Slowed)\n• After Effects Resources\n• Community Tools\n• Moderation Features",
            inline=False
        )
        embed.add_field(
            name="Developer",
            value="moongetsu",
            inline=True
        )
        embed.add_field(
            name="Version",
            value="0.6b",
            inline=True
        )
        embed.set_footer(
            text="© Ryujin Bot (2023-2025) | Information System",
            icon_url=self.RYUJIN_LOGO
        )
        embed.set_author(
            name="Ryujin",
            icon_url=self.RYUJIN_LOGO
        )
        return embed

    @nextcord.slash_command(name="info", description="Shows information about Ryujin Bot")
    async def info(self, interaction: nextcord.Interaction):
        """Shows information about the bot"""
        user_id = interaction.user.id
        is_blacklisted, reason = self.check_blacklist(user_id)
        
        if is_blacklisted:
            embed = self.create_blacklist_embed(reason)
            await interaction.send(embed=embed, ephemeral=True)
            return

        embed = self.create_info_embed()
        await self.bot.maybe_send_ad(interaction)
        await interaction.send(embed=embed, ephemeral=True)

def setup(bot):
    bot.add_cog(InfoCog(bot))