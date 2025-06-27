import nextcord
from nextcord.ext import commands

class RoleInfoCog(commands.Cog):
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
        name="roleinfo",
        description="Get information about a role."
    )
    async def roleinfo(
        self, 
        interaction: nextcord.Interaction, 
        role: nextcord.Role = nextcord.SlashOption(
            description="Role to get info for",
            required=True
        )
    ):
        user_id = interaction.user.id
        is_blacklisted, reason = self.check_blacklist(user_id)
        
        if is_blacklisted:
            embed = self.create_blacklist_embed(reason)
            await interaction.send(embed=embed, ephemeral=True)
            return

        created_at = role.created_at.strftime("%B %d, %Y at %H:%M UTC")
        
        member_count = len(role.members)
        
        permissions = []
        if role.permissions.administrator:
            permissions.append("Administrator")
        if role.permissions.manage_guild:
            permissions.append("Manage Server")
        if role.permissions.manage_channels:
            permissions.append("Manage Channels")
        if role.permissions.manage_roles:
            permissions.append("Manage Roles")
        if role.permissions.manage_messages:
            permissions.append("Manage Messages")
        if role.permissions.manage_webhooks:
            permissions.append("Manage Webhooks")
        if role.permissions.manage_nicknames:
            permissions.append("Manage Nicknames")
        if role.permissions.kick_members:
            permissions.append("Kick Members")
        if role.permissions.ban_members:
            permissions.append("Ban Members")
        if role.permissions.view_audit_log:
            permissions.append("View Audit Log")
        if role.permissions.view_channel:
            permissions.append("View Channels")
        if role.permissions.send_messages:
            permissions.append("Send Messages")
        if role.permissions.embed_links:
            permissions.append("Embed Links")
        if role.permissions.attach_files:
            permissions.append("Attach Files")
        if role.permissions.add_reactions:
            permissions.append("Add Reactions")
        if role.permissions.use_external_emojis:
            permissions.append("Use External Emojis")
        if role.permissions.connect:
            permissions.append("Connect")
        if role.permissions.speak:
            permissions.append("Speak")
        if role.permissions.stream:
            permissions.append("Stream")
        if role.permissions.use_voice_activity:
            permissions.append("Use Voice Activity")
        if role.permissions.priority_speaker:
            permissions.append("Priority Speaker")
        if role.permissions.mute_members:
            permissions.append("Mute Members")
        if role.permissions.deafen_members:
            permissions.append("Deafen Members")
        if role.permissions.move_members:
            permissions.append("Move Members")
        
        description = (
            f"🎭 **Role Information**\n\n"
            f"🏷️ **Name:** {role.name}\n"
            f"🆔 **ID:** {role.id}\n"
            f"📅 **Created:** {created_at}\n"
            f"👥 **Members:** {member_count:,}\n"
            f"🎨 **Color:** {str(role.color) if role.color != nextcord.Color.default() else 'Default'}\n"
            f"📍 **Position:** {role.position}\n"
            f"🔒 **Hoisted:** {'Yes' if role.hoist else 'No'}\n"
            f"🔗 **Mentionable:** {'Yes' if role.mentionable else 'No'}\n"
            f"🤖 **Managed:** {'Yes' if role.managed else 'No'}\n"
        )
        
        if role.description:
            description += f"📝 **Description:** {role.description}\n"
        
        if permissions:
            description += f"\n🔑 **Key Permissions:**\n{', '.join(permissions[:10])}"
            if len(permissions) > 10:
                description += f" and {len(permissions) - 10} more..."
        else:
            description += f"\n🔑 **Key Permissions:** No special permissions"
        
        embed = nextcord.Embed(
            title=f"🎭 {role.name}",
            description=description,
            color=role.color if role.color != nextcord.Color.default() else 0x2a2a2a
        )
        
        if role.icon:
            embed.set_thumbnail(url=role.icon.url)
        
        embed.set_footer(
            text="© Ryujin Bot (2023-2025) | Information System",
            icon_url=self.RYUJIN_LOGO
        )

        embed.set_author(
            name="Ryujin",
            icon_url=self.RYUJIN_LOGO
        )

        await self.bot.maybe_send_ad(interaction)
        await interaction.send(embed=embed, ephemeral=True)

def setup(bot):
    bot.add_cog(RoleInfoCog(bot)) 