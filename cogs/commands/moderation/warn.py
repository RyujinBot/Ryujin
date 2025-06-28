import nextcord
from nextcord.ext import commands
from cogs.utils.db import add_warning, get_warning_count

class WarnCog(commands.Cog):
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
        name="warn",
        description="Warn a member for breaking the rules.",
        default_member_permissions=nextcord.Permissions(manage_messages=True)
    )
    async def warn(
        self,
        interaction: nextcord.Interaction,
        user: nextcord.Member = nextcord.SlashOption(
            name="user",
            description="The user to warn",
            required=True
        ),
        reason: str = nextcord.SlashOption(
            name="reason",
            description="Reason for the warning",
            required=True
        )
    ):
        user_id = interaction.user.id
        is_blacklisted, blacklist_reason = self.check_blacklist(user_id)
        
        if is_blacklisted:
            embed = self.create_blacklist_embed(blacklist_reason)
            await interaction.send(embed=embed, ephemeral=True)
            return

        if not interaction.user.guild_permissions.manage_messages:
            await interaction.send(
                "❌ You don't have permission to use this command.",
                ephemeral=True
            )
            return

        if user.top_role >= interaction.user.top_role:
            await interaction.send(
                "❌ You can't use this command due to role hierarchy.",
                ephemeral=True
            )
            return

        if user.id == interaction.user.id:
            await interaction.send(
                "❌ You can't warn yourself.",
                ephemeral=True
            )
            return

        if user.id == self.bot.user.id:
            await interaction.send(
                "❌ You can't warn the bot.",
                ephemeral=True
            )
            return

        try:
            warning_id = await add_warning(
                self.bot.connection,
                interaction.guild.id,
                user.id,
                interaction.user.id,
                reason
            )

            if warning_id is None:
                await interaction.send(
                    "❌ Failed to add warning to database.",
                    ephemeral=True
                )
                return

            total_warnings = await get_warning_count(
                self.bot.connection,
                interaction.guild.id,
                user.id
            )

            try:
                dm_embed = nextcord.Embed(
                    title="⚠️ You have been warned",
                    description=f"You have received a warning in **{interaction.guild.name}**\n\n"
                              f"**Reason:** {reason}\n"
                              f"**Warned by:** {interaction.user.mention} ({interaction.user.name})\n"
                              f"**Warning ID:** #{warning_id}\n"
                              f"**Total Warnings:** {total_warnings}",
                    color=nextcord.Color.yellow()
                )
                
                dm_embed.set_footer(
                    text="© Ryujin Bot (2023-2025) | Moderation System",
                    icon_url=self.RYUJIN_LOGO
                )
                
                await user.send(embed=dm_embed)
                dm_sent = True
            except:
                dm_sent = False

            embed = nextcord.Embed(
                title="⚠️ User Warned",
                description=f"**{user.mention}** has been warned.\n\n"
                          f"**User:** {user.mention} ({user.name})\n"
                          f"**Warned by:** {interaction.user.mention} ({interaction.user.name})\n"
                          f"**Reason:** {reason}\n"
                          f"**Warning ID:** #{warning_id}\n"
                          f"**Total Warnings:** {total_warnings}\n"
                          f"**DM Status:** {'✅ DM sent to user' if dm_sent else '❌ Could not send DM (DMs closed)'}",
                color=nextcord.Color.yellow()
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

        except Exception as e:
            await interaction.send(
                f"❌ An error occurred while warning the user: `{e}`",
                ephemeral=True
            )

def setup(bot):
    bot.add_cog(WarnCog(bot)) 