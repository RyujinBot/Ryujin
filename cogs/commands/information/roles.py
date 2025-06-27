import nextcord
from nextcord.ext import commands

class RolesCog(commands.Cog):
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
        name="roles",
        description="Get a list of all roles in this server."
    )
    async def roles(self, interaction: nextcord.Interaction):
        user_id = interaction.user.id
        is_blacklisted, reason = self.check_blacklist(user_id)
        
        if is_blacklisted:
            embed = self.create_blacklist_embed(reason)
            await interaction.send(embed=embed, ephemeral=True)
            return

        guild = interaction.guild
        roles = guild.roles[1:]
        roles = reversed(roles)

        role_mentions = [role.mention for role in roles if role.name != "@everyone"]
        roles_str = ", ".join(role_mentions)

        if len(roles_str) > 4000:
            roles_str = roles_str[:4000] + "..."

        embed = nextcord.Embed(
            title=f"📋 Roles in {guild.name}",
            description=roles_str or "No roles found.",
            color=nextcord.Color.blurple()
        )
        embed.set_footer(
            text="© Ryujin Bot (2023-2025) | Information System",
            icon_url=self.RYUJIN_LOGO
        )
        
        if guild.icon:
            embed.set_author(
                name=guild.name,
                icon_url=guild.icon.url
            )
        else:
            embed.set_author(
                name="Ryujin",
                icon_url=self.RYUJIN_LOGO
            ) 
        await self.bot.maybe_send_ad(interaction)
        await interaction.send(embed=embed, ephemeral=True)

def setup(bot):
    bot.add_cog(RolesCog(bot))
