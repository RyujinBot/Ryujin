import nextcord
from nextcord.ext import commands

class EmojisCog(commands.Cog):
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
        name="emojis",
        description="Get a list of all custom emojis in this server."
    )
    async def emojis(self, interaction: nextcord.Interaction):
        user_id = interaction.user.id
        is_blacklisted, reason = self.check_blacklist(user_id)
        
        if is_blacklisted:
            embed = self.create_blacklist_embed(reason)
            await interaction.send(embed=embed, ephemeral=True)
            return

        guild = interaction.guild
        emojis = guild.emojis

        if not emojis:
            description = "No custom emojis found in this server."
        else:
            emote_list = [f"{str(emote)} `:{emote.name}:`" for emote in emojis]
            description = "\n".join(emote_list)

            if len(description) > 4000:
                description = description[:4000] + "\n..."

        embed = nextcord.Embed(
            title=f"😄 Emojis in {guild.name}",
            description=description,
            color=nextcord.Color.blurple()
        )

        if guild.icon:
            embed.set_author(name=guild.name, icon_url=guild.icon.url)
        else:
            embed.set_author(name="Ryujin", icon_url=self.RYUJIN_LOGO)

        embed.set_footer(
            text="© Ryujin Bot (2023-2025) | Information System",
            icon_url=self.RYUJIN_LOGO
        )

        await self.bot.maybe_send_ad(interaction)
        await interaction.send(embed=embed, ephemeral=True)

def setup(bot):
    bot.add_cog(EmojisCog(bot))
