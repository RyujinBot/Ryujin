import nextcord
from nextcord.ext import commands

class UnbanCog(commands.Cog):
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
        name="unban",
        description="Unban a user from the server using their user ID.",
        default_member_permissions=nextcord.Permissions(ban_members=True)
    )
    async def unban(
        self,
        interaction: nextcord.Interaction,
        user_id: str = nextcord.SlashOption(
            name="user_id",
            description="The ID of the user to unban",
            required=True
        ),
        reason: str = nextcord.SlashOption(
            name="reason",
            description="Reason for the unban",
            required=False
        )
    ):
        user_id_int = interaction.user.id
        is_blacklisted, blacklist_reason = self.check_blacklist(user_id_int)
        
        if is_blacklisted:
            embed = self.create_blacklist_embed(blacklist_reason)
            await interaction.send(embed=embed, ephemeral=True)
            return

        # Check permissions
        if not interaction.user.guild_permissions.ban_members:
            await interaction.send(
                "❌ You don't have permission to unban members.",
                ephemeral=True
            )
            return

        if not interaction.guild.me.guild_permissions.ban_members:
            await interaction.send(
                "❌ I don't have permission to unban members.",
                ephemeral=True
            )
            return

        # Validate user ID
        try:
            user_id_to_unban = int(user_id)
        except ValueError:
            await interaction.send(
                "❌ Invalid user ID. Please provide a valid numeric user ID.",
                ephemeral=True
            )
            return

        # Check if user is actually banned
        try:
            ban_entry = await interaction.guild.fetch_ban(nextcord.Object(id=user_id_to_unban))
        except nextcord.NotFound:
            await interaction.send(
                "❌ This user is not banned from this server.",
                ephemeral=True
            )
            return
        except Exception as e:
            await interaction.send(
                f"❌ Error checking ban status: `{e}`",
                ephemeral=True
            )
            return

        # Prepare reason
        unban_reason = reason or "No reason provided"

        try:
            # Unban the user
            await interaction.guild.unban(nextcord.Object(id=user_id_to_unban), reason=f"{interaction.user.name}: {unban_reason}")
            
            # Try to get user info
            try:
                user = await self.bot.fetch_user(user_id_to_unban)
                user_mention = user.mention
                user_name = user.name
            except:
                user_mention = f"<@{user_id_to_unban}>"
                user_name = f"Unknown User ({user_id_to_unban})"
            
            # Create success embed
            description = f"**{user_mention}** has been unbanned from the server.\n\n"
            description += f"**User:** {user_mention} ({user_name})\n"
            description += f"**Unbanned by:** {interaction.user.mention} ({interaction.user.name})\n"
            description += f"**Reason:** {unban_reason}\n"
            
            if ban_entry.reason:
                description += f"**Original Ban Reason:** {ban_entry.reason}"
            
            embed = nextcord.Embed(
                title="🔓 User Unbanned",
                description=description,
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
                "❌ I don't have permission to unban this user.",
                ephemeral=True
            )
        except Exception as e:
            await interaction.send(
                f"❌ An error occurred while unbanning the user: `{e}`",
                ephemeral=True
            )

def setup(bot):
    bot.add_cog(UnbanCog(bot)) 