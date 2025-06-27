import nextcord
from nextcord.ext import commands

class NickCog(commands.Cog):
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
        name="nick",
        description="Change the bot's nickname in this server."
    )
    async def nick(
        self,
        interaction: nextcord.Interaction,
        new_nick: str = nextcord.SlashOption(
            name="name",
            description="New nickname for the bot",
            required=True
        )
    ):
        user_id = interaction.user.id
        is_blacklisted, blacklist_reason = self.check_blacklist(user_id)
        
        if is_blacklisted:
            embed = self.create_blacklist_embed(blacklist_reason)
            await interaction.send(embed=embed, ephemeral=True)
            return

        if not interaction.user.guild_permissions.manage_nicknames:
            await interaction.send(
                "❌ You don't have permission to use this command.",
                ephemeral=True
            )
            return

        try:
            await interaction.guild.me.edit(nick=new_nick)
            embed = nextcord.Embed(
                title="✅ Nickname Changed",
                description=f"The bot's nickname has been changed to **{new_nick}**.",
                color=nextcord.Color.green()
            )
            embed.set_footer(
                text="© Ryujin Bot (2023-2025) | Moderation System",
                icon_url=self.RYUJIN_LOGO
            )

            embed.set_author(
                name="Ryujin",
                icon_url=self.RYUJIN_LOGO
            )

            await self.bot.maybe_send_ad(interaction)
            await interaction.send(embed=embed, ephemeral=True)
        except nextcord.Forbidden:
            await interaction.send(
                "❌ I don't have permission to change my nickname. Please check my role hierarchy and permissions.",
                ephemeral=True
            )
        except Exception as e:
            await interaction.send(f"⚠️ An error occurred: `{e}`", ephemeral=True)

def setup(bot):
    bot.add_cog(NickCog(bot))
