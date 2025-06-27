import nextcord
from nextcord.ext import commands
from nextcord import SlashOption

class SlowmodeCog(commands.Cog):
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
        name="slowmode",
        description="Set slowmode for a channel.",
        default_member_permissions=nextcord.Permissions(manage_channels=True)
    )
    async def slowmode(
        self,
        interaction: nextcord.Interaction,
        seconds: int = SlashOption(
            name="seconds",
            description="The slowmode duration in seconds (0 to disable).",
            required=True
        ),
        channel: nextcord.TextChannel = SlashOption(
            name="channel",
            description="The channel to apply slowmode. Defaults to current channel.",
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

        if seconds < 0 or seconds > 21600:
            return await interaction.send("❌ Slowmode must be between 0 and 21600 seconds (6 hours).", ephemeral=True)

        try:
            await target_channel.edit(slowmode_delay=seconds)

            embed = nextcord.Embed(
                title="🐢 Slowmode Updated",
                description=f"Slowmode in {target_channel.mention} is now set to `{seconds}` seconds.",
                color=nextcord.Color.blurple()
            )
            embed.set_footer(text="© Ryujin Bot (2023-2025) | Moderation System", icon_url=self.RYUJIN_LOGO)

            if interaction.guild.icon:
                embed.set_author(name=interaction.guild.name, icon_url=interaction.guild.icon.url)
            else:
                embed.set_author(name="Ryujin", icon_url=self.RYUJIN_LOGO)

            await self.bot.maybe_send_ad(interaction)
            await interaction.send(embed=embed, ephemeral=True)

        except Exception as e:
            await interaction.send(f"❌ Failed to update slowmode: `{e}`", ephemeral=True)

    @nextcord.slash_command(
        name="remove_slowmode",
        description="Remove slowmode from a channel.",
        default_member_permissions=nextcord.Permissions(manage_channels=True)
    )
    async def remove_slowmode(
        self,
        interaction: nextcord.Interaction,
        channel: nextcord.TextChannel = SlashOption(
            name="channel",
            description="The channel to remove slowmode. Defaults to current channel.",
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

        try:
            await target_channel.edit(slowmode_delay=0)

            embed = nextcord.Embed(
                title="🧯 Slowmode Removed",
                description=f"Slowmode has been disabled in {target_channel.mention}.",
                color=nextcord.Color.green()
            )
            embed.set_footer(text="© Ryujin Bot (2023-2025) | Moderation System", icon_url=self.RYUJIN_LOGO)

            if interaction.guild.icon:
                embed.set_author(name=interaction.guild.name, icon_url=interaction.guild.icon.url)
            else:
                embed.set_author(name="Ryujin", icon_url=self.RYUJIN_LOGO)

            await self.bot.maybe_send_ad(interaction)
            await interaction.send(embed=embed, ephemeral=True)

        except Exception as e:
            await interaction.send(f"❌ Failed to remove slowmode: `{e}`", ephemeral=True)

def setup(bot):
    bot.add_cog(SlowmodeCog(bot))
