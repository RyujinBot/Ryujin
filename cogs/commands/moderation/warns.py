import nextcord
from nextcord.ext import commands
from cogs.utils.db import get_user_warnings, get_warning_count
from datetime import datetime

class WarnsCog(commands.Cog):
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
        name="warns",
        description="Display all warnings for a member.",
        default_member_permissions=nextcord.Permissions(manage_messages=True)
    )
    async def warns(
        self,
        interaction: nextcord.Interaction,
        user: nextcord.Member = nextcord.SlashOption(
            name="user",
            description="The user to check warnings for",
            required=True
        )
    ):
        user_id = interaction.user.id
        is_blacklisted, blacklist_reason = self.check_blacklist(user_id)
        
        if is_blacklisted:
            embed = self.create_blacklist_embed(blacklist_reason)
            await interaction.send(embed=embed, ephemeral=True)
            return

        # Check permissions
        if not interaction.user.guild_permissions.manage_messages:
            await interaction.send(
                "❌ You don't have permission to use this command.",
                ephemeral=True
            )
            return

        try:
            # Get user's warnings
            warnings = await get_user_warnings(
                self.bot.connection,
                interaction.guild.id,
                user.id
            )

            # Get total warning count
            total_warnings = await get_warning_count(
                self.bot.connection,
                interaction.guild.id,
                user.id
            )

            if not warnings:
                # No warnings
                embed = nextcord.Embed(
                    title="📋 Warning History",
                    description=f"**User:** {user.mention} ({user.name})\n"
                              f"**Total Warnings:** 0\n"
                              f"**Status:** ✅ Clean record",
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
                return

            # Create warning list
            warning_list = []
            for warning in warnings:
                warning_id, moderator_id, reason, warn_date = warning
                
                # Try to get moderator name
                try:
                    moderator = await self.bot.fetch_user(moderator_id)
                    moderator_name = moderator.name
                except:
                    moderator_name = f"Unknown User ({moderator_id})"
                
                # Format date
                if isinstance(warn_date, str):
                    # If it's already a string, try to parse it
                    try:
                        warn_date = datetime.fromisoformat(warn_date.replace('Z', '+00:00'))
                    except:
                        warn_date = "Unknown date"
                
                if isinstance(warn_date, datetime):
                    date_str = f"<t:{int(warn_date.timestamp())}:R>"
                else:
                    date_str = str(warn_date)
                
                warning_list.append(f"**#{warning_id}** | {moderator_name} | {date_str}\n└ {reason}")

            # Set status based on warning count
            if total_warnings == 0:
                status = "✅ Clean record"
            elif total_warnings == 1:
                status = "⚠️ 1 warning"
            elif total_warnings <= 3:
                status = f"⚠️ {total_warnings} warnings"
            else:
                status = f"🚨 {total_warnings} warnings (High risk)"

            # Create warnings text (limit to 10 most recent)
            warnings_text = "\n\n".join(warning_list[:10])
            if len(warning_list) > 10:
                warnings_text += f"\n\n*... and {len(warning_list) - 10} more warnings*"

            # Create embed
            embed = nextcord.Embed(
                title="📋 Warning History",
                description=f"**User:** {user.mention} ({user.name})\n"
                          f"**Total Warnings:** {total_warnings}\n"
                          f"**Status:** {status}\n\n"
                          f"**Recent Warnings:**\n{warnings_text}",
                color=nextcord.Color.orange() if total_warnings > 0 else nextcord.Color.green()
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
                f"❌ An error occurred while fetching warnings: `{e}`",
                ephemeral=True
            )

def setup(bot):
    bot.add_cog(WarnsCog(bot)) 