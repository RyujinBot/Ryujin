import nextcord
from nextcord.ext import commands
from datetime import datetime, timedelta

class BanCog(commands.Cog):
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

    def parse_duration(self, duration_str):
        """Parse duration string (e.g., '1d', '2h', '30m') and return timedelta"""
        if not duration_str:
            return None
        
        duration_str = duration_str.lower()
        if duration_str == "permanent" or duration_str == "perm":
            return None
        
        try:
            if duration_str.endswith('d'):
                days = int(duration_str[:-1])
                return timedelta(days=days)
            elif duration_str.endswith('h'):
                hours = int(duration_str[:-1])
                return timedelta(hours=hours)
            elif duration_str.endswith('m'):
                minutes = int(duration_str[:-1])
                return timedelta(minutes=minutes)
            elif duration_str.endswith('s'):
                seconds = int(duration_str[:-1])
                return timedelta(seconds=seconds)
            else:
                # Default to hours if no unit specified
                hours = int(duration_str)
                return timedelta(hours=hours)
        except ValueError:
            return None

    @nextcord.slash_command(
        name="ban",
        description="Ban a member from the server with optional duration and reason.",
        default_member_permissions=nextcord.Permissions(ban_members=True)
    )
    async def ban(
        self,
        interaction: nextcord.Interaction,
        user: nextcord.Member = nextcord.SlashOption(
            name="user",
            description="The user to ban",
            required=True
        ),
        duration: str = nextcord.SlashOption(
            name="duration",
            description="Ban duration (e.g., 1d, 2h, 30m, permanent)",
            required=False
        ),
        reason: str = nextcord.SlashOption(
            name="reason",
            description="Reason for the ban",
            required=False
        )
    ):
        user_id = interaction.user.id
        is_blacklisted, blacklist_reason = self.check_blacklist(user_id)
        
        if is_blacklisted:
            embed = self.create_blacklist_embed(blacklist_reason)
            await interaction.send(embed=embed, ephemeral=True)
            return

        # Check permissions
        if not interaction.user.guild_permissions.ban_members:
            await interaction.send(
                "❌ You don't have permission to use this command.",
                ephemeral=True
            )
            return

        if not interaction.guild.me.guild_permissions.ban_members:
            await interaction.send(
                "❌ I don't have permission to use this command.",
                ephemeral=True
            )
            return

        # Check role hierarchy
        if user.top_role >= interaction.user.top_role:
            await interaction.send(
                "❌ You can't use this command due to role hierarchy.",
                ephemeral=True
            )
            return

        if user.top_role >= interaction.guild.me.top_role:
            await interaction.send(
                "❌ I can't ban this user due to role hierarchy.",
                ephemeral=True
            )
            return

        # Parse duration
        duration_delta = self.parse_duration(duration) if duration else None
        is_permanent = duration_delta is None
        
        # Prepare reason
        ban_reason = reason or "No reason provided"
        if duration and not is_permanent:
            ban_reason += f" (Duration: {duration})"

        try:
            # Send DM to user before banning (if possible)
            try:
                dm_embed = nextcord.Embed(
                    title="🔨 You have been banned",
                    description=f"You have been banned from **{interaction.guild.name}**\n\nReason: {ban_reason}\nBanned by: {interaction.user.mention} ({interaction.user.name})\nDuration: {duration if not is_permanent and duration_delta else 'Permanent'}",
                    color=nextcord.Color.red()
                )
                
                dm_embed.set_footer(
                    text="© Ryujin Bot (2023-2025) | Moderation System",
                    icon_url=self.RYUJIN_LOGO
                )
                
                await user.send(embed=dm_embed)
                dm_sent = True
            except:
                dm_sent = False

            # Ban the user
            await user.ban(reason=f"{interaction.user.name}: {ban_reason}")
            
            # Create success embed
            embed = nextcord.Embed(
                title="🔨 User Banned",
                description=f"**{user.mention}** has been banned from the server.\n\nUser: {user.mention} ({user.name})\nBanned by: {interaction.user.mention} ({interaction.user.name})\nReason: {ban_reason}\nDuration: {duration if not is_permanent and duration_delta else 'Permanent'}\n{f'Expires: <t:{int((datetime.now() + duration_delta).timestamp())}:R>' if not is_permanent and duration_delta else ''}\nDM Status: {'✅ DM sent to user' if dm_sent else '❌ Could not send DM (DMs closed)'}",
                color=nextcord.Color.red()
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
                "❌ I don't have permission to ban this user.",
                ephemeral=True
            )
        except Exception as e:
            await interaction.send(
                f"❌ An error occurred while banning the user: `{e}`",
                ephemeral=True
            )

def setup(bot):
    bot.add_cog(BanCog(bot)) 