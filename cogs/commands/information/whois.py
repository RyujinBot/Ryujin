import nextcord
from nextcord.ext import commands

class WhoisCog(commands.Cog):
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
        name="whois",
        description="Display detailed information about a user."
    )
    async def whois(
        self, 
        interaction: nextcord.Interaction, 
        user: nextcord.Member = nextcord.SlashOption(
            description="User to get info for (defaults to you)",
            required=False
        )
    ):
        user_id = interaction.user.id
        is_blacklisted, reason = self.check_blacklist(user_id)
        
        if is_blacklisted:
            embed = self.create_blacklist_embed(reason)
            await interaction.send(embed=embed, ephemeral=True)
            return

        if user is None:
            user = interaction.user
        
        created_at = user.created_at.strftime("%B %d, %Y at %H:%M UTC")
        
        joined_at = user.joined_at.strftime("%B %d, %Y at %H:%M UTC") if user.joined_at else "Unknown"
        
        roles = [role.mention for role in user.roles if role.name != "@everyone"]
        roles.reverse()
        
        permissions = []
        if user.guild_permissions.administrator:
            permissions.append("Administrator")
        if user.guild_permissions.manage_guild:
            permissions.append("Manage Server")
        if user.guild_permissions.manage_channels:
            permissions.append("Manage Channels")
        if user.guild_permissions.manage_roles:
            permissions.append("Manage Roles")
        if user.guild_permissions.manage_messages:
            permissions.append("Manage Messages")
        
        description = (
            f"👤 **User Information**\n\n"
            f"🏷️ **Name:** {user.display_name}\n"
            f"📝 **Username:** {user.name}\n"
            f"🆔 **ID:** {user.id}\n"
            f"📅 **Created:** {created_at}\n"
            f"📥 **Joined:** {joined_at}\n"
            f"🤖 **Bot:** {'Yes' if user.bot else 'No'}\n\n"
        )
        
        if user.nick:
            description += f"📛 **Nickname:** {user.nick}\n"
        
        if user.top_role.name != "@everyone":
            description += f"👑 **Top Role:** {user.top_role.mention}\n"
        
        if permissions:
            description += f"🔑 **Key Permissions:** {', '.join(permissions)}\n"
        
        description += f"\n🎭 **Roles ({len(roles)}):**\n"
        if roles:
            if len(roles) > 10:
                description += f"{', '.join(roles[:10])} and {len(roles) - 10} more..."
            else:
                description += ', '.join(roles)
        else:
            description += "No roles"
        
        embed = nextcord.Embed(
            title=f"👤 {user.display_name}",
            description=description,
            color=user.color if user.color != nextcord.Color.default() else 0x2a2a2a
        )
        
        if user.display_avatar:
            embed.set_thumbnail(url=user.display_avatar.url)
        
        embed.set_footer(
            text="© Ryujin Bot (2023-2025) | Information System",
            icon_url=self.RYUJIN_LOGO
        )
        
        await self.bot.maybe_send_ad(interaction)
        await interaction.send(embed=embed, ephemeral=True)

def setup(bot):
    bot.add_cog(WhoisCog(bot)) 