import nextcord
from nextcord.ext import commands
from nextcord import SlashOption
import logging

class Channel(commands.Cog):
    def __init__(self, bot):
        self.bot = bot

    def check_blacklist(self, user_id):
        if hasattr(self.bot, 'blacklist'):
            return user_id in self.bot.blacklist, self.bot.blacklist.get(user_id)
        return False, None

    def create_blacklist_embed(self, reason):
        embed = nextcord.Embed(
            title="You are blacklisted!",
            description=f"**You can't use Ryujin's functions anymore because you have been blacklisted for `{reason}`.**",
            color=nextcord.Color.red()
        )
        embed.set_footer(text="© Ryujin Bot (2023-2025) | Blacklist System")
        embed.set_author(name="Ryujin", icon_url=self.bot.RYUJIN_LOGO)
        return embed

    @nextcord.slash_command(
        name="channel",
        description="Create or delete a channel with advanced options. 📋",
        default_member_permissions=nextcord.Permissions(manage_channels=True)
    )
    async def channel(
        self,
        interaction: nextcord.Interaction,
        action: str = SlashOption(
            name="action",
            description="Action to perform (create/delete)",
            required=True,
            choices={"create": "create", "delete": "delete"}
        ),
        name: str = SlashOption(
            name="name",
            description="Name for the new channel (for create)",
            required=False
        ),
        channel: nextcord.TextChannel = SlashOption(
            name="channel",
            description="Channel to delete (for delete)",
            required=False
        ),
        channel_type: str = SlashOption(
            name="type",
            description="Type of channel to create (for create)",
            required=False,
            choices={"text": "text", "voice": "voice", "announcement": "announcement", "stage": "stage", "forum": "forum"}
        ),
        category: nextcord.CategoryChannel = SlashOption(
            name="category",
            description="Category to place the channel in (for create)",
            required=False
        ),
        topic: str = SlashOption(
            name="topic",
            description="Topic/description for the channel (for create)",
            required=False
        ),
        nsfw: bool = SlashOption(
            name="nsfw",
            description="Whether the channel is NSFW (for create)",
            required=False,
            default=False
        ),
        slowmode: int = SlashOption(
            name="slowmode",
            description="Slowmode delay in seconds (0-21600) (for create)",
            required=False,
            default=0
        ),
        user_limit: int = SlashOption(
            name="user_limit",
            description="User limit for voice channels (0-99, 0=no limit) (for create)",
            required=False,
            default=0
        ),
        bitrate: int = SlashOption(
            name="bitrate",
            description="Bitrate for voice channels in kbps (8-96) (for create)",
            required=False,
            default=64
        ),
        position: int = SlashOption(
            name="position",
            description="Position of the channel (for create)",
            required=False
        ),
        reason: str = SlashOption(
            name="reason",
            description="Reason for creating/deleting the channel",
            required=False
        )
    ):
        is_blacklisted, blacklist_reason = self.check_blacklist(interaction.user.id)
        if is_blacklisted:
            embed = self.create_blacklist_embed(blacklist_reason)
            await interaction.send(embed=embed, ephemeral=True)
            return

        if not interaction.user.guild_permissions.manage_channels:
            await interaction.send("❌ You don't have permission to use this command.", ephemeral=True)
            return

        if action == "create":
            if not name:
                await interaction.send("❌ You must provide a name for the new channel.", ephemeral=True)
                return
                
            if not channel_type:
                await interaction.send("❌ You must specify a channel type (text, voice, announcement, stage, forum).", ephemeral=True)
                return

            if len(name) < 1 or len(name) > 100:
                await interaction.send("❌ Channel name must be between 1 and 100 characters.", ephemeral=True)
                return

            if slowmode < 0 or slowmode > 21600:
                await interaction.send("❌ Slowmode must be between 0 and 21600 seconds (6 hours).", ephemeral=True)
                return

            if user_limit < 0 or user_limit > 99:
                await interaction.send("❌ User limit must be between 0 and 99 (0 = no limit).", ephemeral=True)
                return

            if bitrate < 8 or bitrate > 96:
                await interaction.send("❌ Bitrate must be between 8 and 96 kbps.", ephemeral=True)
                return

            try:
                channel_kwargs = {
                    "name": name,
                    "reason": reason or f"Channel created by {interaction.user}"
                }

                if category:
                    channel_kwargs["category"] = category
                if topic:
                    channel_kwargs["topic"] = topic
                if nsfw is not None:
                    channel_kwargs["nsfw"] = nsfw
                if position is not None:
                    channel_kwargs["position"] = position

                if channel_type == "text":
                    channel_obj = await interaction.guild.create_text_channel(**channel_kwargs)
                    if slowmode > 0:
                        await channel_obj.edit(slowmode_delay=slowmode)
                elif channel_type == "voice":
                    channel_kwargs["bitrate"] = bitrate * 1000
                    if user_limit > 0:
                        channel_kwargs["user_limit"] = user_limit
                    channel_obj = await interaction.guild.create_voice_channel(**channel_kwargs)
                elif channel_type == "announcement":
                    channel_obj = await interaction.guild.create_news_channel(**channel_kwargs)
                    if slowmode > 0:
                        await channel_obj.edit(slowmode_delay=slowmode)
                elif channel_type == "stage":
                    channel_kwargs["bitrate"] = bitrate * 1000
                    if user_limit > 0:
                        channel_kwargs["user_limit"] = user_limit
                    channel_obj = await interaction.guild.create_stage_instance(**channel_kwargs)
                elif channel_type == "forum":
                    channel_obj = await interaction.guild.create_forum_channel(**channel_kwargs)
                    if slowmode > 0:
                        await channel_obj.edit(slowmode_delay=slowmode)

                embed = nextcord.Embed(
                    title="✅ Channel Created Successfully",
                    description=f"Successfully created {channel_type} channel **{name}**",
                    color=nextcord.Color.green()
                )
                embed.add_field(name="Channel", value=f"{channel_obj.mention} ({channel_obj.name})", inline=True)
                embed.add_field(name="Type", value=f"{channel_type.title()}", inline=True)
                embed.add_field(name="Created by", value=f"{interaction.user.mention}", inline=True)
                embed.add_field(name="ID", value=f"`{channel_obj.id}`", inline=True)
                embed.add_field(name="Position", value=f"{channel_obj.position}", inline=True)
                embed.add_field(name="Created at", value=f"<t:{int(channel_obj.created_at.timestamp())}:R>", inline=True)

                if category:
                    embed.add_field(name="Category", value=f"{category.mention} ({category.name})", inline=True)
                if topic:
                    embed.add_field(name="Topic", value=f"```{topic[:100]}{'...' if len(topic) > 100 else ''}```", inline=False)
                if nsfw:
                    embed.add_field(name="NSFW", value="✅ Yes", inline=True)
                if slowmode > 0:
                    embed.add_field(name="Slowmode", value=f"{slowmode} seconds", inline=True)
                if channel_type == "voice" and user_limit > 0:
                    embed.add_field(name="User Limit", value=f"{user_limit} users", inline=True)
                if channel_type == "voice":
                    embed.add_field(name="Bitrate", value=f"{bitrate} kbps", inline=True)

                embed.set_footer(text="© Ryujin Bot (2023-2025) | Moderation System")
                embed.set_author(name="Ryujin", icon_url=self.bot.RYUJIN_LOGO)

                await interaction.send(embed=embed, ephemeral=True)
                await self.bot.maybe_send_ad(interaction)

            except Exception as e:
                await interaction.send(f"❌ Failed to create channel: `{e}`", ephemeral=True)

        elif action == "delete":
            if not channel:
                await interaction.send("❌ You must select a channel to delete.", ephemeral=True)
                return

            if channel == interaction.guild.system_channel:
                await interaction.send("❌ Cannot delete the system channel.", ephemeral=True)
                return

            if channel == interaction.guild.rules_channel:
                await interaction.send("❌ Cannot delete the rules channel.", ephemeral=True)
                return

            if channel == interaction.guild.public_updates_channel:
                await interaction.send("❌ Cannot delete the public updates channel.", ephemeral=True)
                return

            try:
                channel_name = channel.name
                channel_id = channel.id
                channel_type = channel.type.name
                channel_position = channel.position
                member_count = len(channel.members) if hasattr(channel, 'members') else 0

                await channel.delete(reason=reason or f"Channel deleted by {interaction.user}")

                embed = nextcord.Embed(
                    title="✅ Channel Deleted Successfully",
                    description=f"Successfully deleted channel **{channel_name}**",
                    color=nextcord.Color.green()
                )
                embed.add_field(name="Channel Name", value=f"{channel_name}", inline=True)
                embed.add_field(name="Type", value=f"{channel_type.title()}", inline=True)
                embed.add_field(name="Deleted by", value=f"{interaction.user.mention}", inline=True)
                embed.add_field(name="Channel ID", value=f"`{channel_id}`", inline=True)
                embed.add_field(name="Position", value=f"{channel_position}", inline=True)
                if member_count > 0:
                    embed.add_field(name="Members Affected", value=f"{member_count} members", inline=True)

                embed.set_footer(text="© Ryujin Bot (2023-2025) | Moderation System")
                embed.set_author(name="Ryujin", icon_url=self.bot.RYUJIN_LOGO)

                await interaction.send(embed=embed, ephemeral=True)
                await self.bot.maybe_send_ad(interaction)

            except Exception as e:
                await interaction.send(f"❌ Failed to delete channel: `{e}`", ephemeral=True)

        else:
            await interaction.send("❌ Invalid action. Use 'create' or 'delete'!", ephemeral=True)

def setup(bot):
    bot.add_cog(Channel(bot)) 