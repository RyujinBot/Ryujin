import nextcord
from nextcord.ext import commands
from nextcord import SlashOption

class LockCog(commands.Cog):
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
        name="lock",
        description="Locks a channel for @everyone.",
        default_member_permissions=nextcord.Permissions(manage_channels=True)
    )
    async def lock(
        self,
        interaction: nextcord.Interaction,
        channel: nextcord.TextChannel = SlashOption(
            name="channel",
            description="The channel to lock. If not provided, the current channel will be used.",
            required=False
        )
    ):
        user_id = interaction.user.id
        is_blacklisted, blacklist_reason = self.check_blacklist(user_id)
        
        if is_blacklisted:
            embed = self.create_blacklist_embed(blacklist_reason)
            await interaction.send(embed=embed, ephemeral=True)
            return

        if not interaction.user.guild_permissions.manage_channels:
            return await interaction.send("❌ You don't have permission to use this command.", ephemeral=True)

        await interaction.response.defer(ephemeral=True)
        target_channel = channel or interaction.channel
        guild = interaction.guild
        everyone_role = guild.default_role

        try:
            overwrite = target_channel.overwrites_for(everyone_role)
            overwrite.send_messages = False
            await target_channel.set_permissions(everyone_role, overwrite=overwrite)

            embed = nextcord.Embed(
                title="🔒 Channel Locked",
                description=f"{target_channel.mention} has been locked for `@everyone`.",
                color=nextcord.Color.red()
            )
            embed.set_footer(text="© Ryujin Bot (2023-2025) | Moderation System", icon_url=self.RYUJIN_LOGO)

            if guild.icon:
                embed.set_author(name=guild.name, icon_url=guild.icon.url)
            else:
                embed.set_author(name="Ryujin", icon_url=self.RYUJIN_LOGO)

            await self.bot.maybe_send_ad(interaction)
            await interaction.send(embed=embed, ephemeral=True)

        except Exception as e:
            await interaction.send(f"❌ Failed to lock the channel: `{e}`", ephemeral=True)

    @nextcord.slash_command(
        name="unlock",
        description="Unlocks a channel for @everyone.",
        default_member_permissions=nextcord.Permissions(manage_channels=True)
    )
    async def unlock(
        self,
        interaction: nextcord.Interaction,
        channel: nextcord.TextChannel = SlashOption(
            name="channel",
            description="The channel to unlock. If not provided, the current channel will be used.",
            required=False
        )
    ):
        user_id = interaction.user.id
        is_blacklisted, blacklist_reason = self.check_blacklist(user_id)
        
        if is_blacklisted:
            embed = self.create_blacklist_embed(blacklist_reason)
            await interaction.send(embed=embed, ephemeral=True)
            return

        if not interaction.user.guild_permissions.manage_channels:
            return await interaction.send("❌ You don't have permission to use this command.", ephemeral=True)

        await interaction.response.defer(ephemeral=True)
        target_channel = channel or interaction.channel
        guild = interaction.guild
        everyone_role = guild.default_role

        try:
            overwrite = target_channel.overwrites_for(everyone_role)
            overwrite.send_messages = True
            await target_channel.set_permissions(everyone_role, overwrite=overwrite)

            embed = nextcord.Embed(
                title="🔓 Channel Unlocked",
                description=f"{target_channel.mention} has been unlocked for `@everyone`.",
                color=nextcord.Color.green()
            )
            embed.set_footer(
                text="© Ryujin Bot (2023-2025) | Moderation System", 
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

        except Exception as e:
            await interaction.send(f"❌ Failed to unlock the channel: `{e}`", ephemeral=True)

def setup(bot):
    bot.add_cog(LockCog(bot))