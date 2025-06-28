import nextcord
from nextcord.ext import commands
import re
from datetime import datetime

class SayCog(commands.Cog):
    def __init__(self, bot):
        self.bot = bot
        self.RYUJIN_LOGO = "https://cdn.discordapp.com/avatars/1059400568805785620/63a77f852ea29f37961f458c53fb5a97.png"
        
        self.restricted_patterns = [
            r'https?://',
            r'www\.',
            r'<@!?\d+>',
            r'<@&\d+>',
            r'<#\d+>',
            r'<@&\d+>',
            r'<a:\w+:\d+>',
            r'<:\w+:\d+>',
            r'```[\s\S]*```',
            r'`[^`]*`',
            r'@everyone',
            r'@here',
            r'@role',
        ]

    def check_blacklist(self, user_id):
        """Check if user is blacklisted"""
        return user_id in self.bot.blacklist

    def create_blacklist_embed(self, reason):
        """Create blacklist embed"""
        embed = nextcord.Embed(
            title="You are blacklisted!",
            description=f"**You can't use Ryujin's functions anymore because you have been blacklisted for `{reason}`.**",
            color=nextcord.Color.red()
        )
        embed.set_footer(text="© Ryujin Bot (2023-2025) | Blacklist System")
        embed.set_author(
            name="Ryujin",
            icon_url=self.RYUJIN_LOGO
        )
        return embed

    def check_restricted_content(self, text):
        """Check if text contains restricted content"""
        for pattern in self.restricted_patterns:
            if re.search(pattern, text, re.IGNORECASE):
                return True, pattern
        return False, None

    @nextcord.slash_command(
        name="say",
        description="Make the bot say something! 🗣️"
    )
    async def say(
        self,
        interaction: nextcord.Interaction,
        message: str = nextcord.SlashOption(
            description="What should the bot say?",
            required=True
        ),
        channel: nextcord.TextChannel = nextcord.SlashOption(
            description="Channel to send the message in (optional)",
            required=False
        )
    ):
        if self.check_blacklist(interaction.user.id):
            embed = self.create_blacklist_embed(self.bot.blacklist[interaction.user.id])
            await interaction.response.send_message(embed=embed, ephemeral=True)
            return

        target_channel = channel or interaction.channel
        
        if not target_channel.permissions_for(interaction.user).send_messages:
            await interaction.response.send_message(
                "❌ You don't have permission to send messages in that channel!",
                ephemeral=True
            )
            return

        if not target_channel.permissions_for(interaction.guild.me).send_messages:
            await interaction.response.send_message(
                "❌ I don't have permission to send messages in that channel!",
                ephemeral=True
            )
            return

        is_restricted, pattern = self.check_restricted_content(message)
        if is_restricted:
            embed = nextcord.Embed(
                title="❌ Restricted Content Detected",
                description="Your message contains restricted content that cannot be sent.",
                color=nextcord.Color.red()
            )
            embed.add_field(
                name="🚫 Restricted Pattern",
                value=f"```{pattern}```",
                inline=False
            )
            embed.add_field(
                name="💡 Allowed Content",
                value="• Plain text messages\n• Emojis (not custom ones)\n• Basic formatting\n• Numbers and symbols",
                inline=False
            )
            embed.add_field(
                name="🚫 Not Allowed",
                value="• Links and URLs\n• User/Role/Channel mentions\n• Code blocks\n• @everyone/@here\n• Custom emojis",
                inline=False
            )
            embed.set_footer(
                text="© Ryujin Bot (2023-2025) | Fun System",
                icon_url=self.RYUJIN_LOGO
            )
            embed.set_author(
                name=f"Ryujin",
                icon_url=self.RYUJIN_LOGO
            )
            await interaction.response.send_message(embed=embed, ephemeral=True)
            return

        if len(message) > 2000:
            await interaction.response.send_message(
                "❌ Message is too long! Maximum 2000 characters allowed.",
                ephemeral=True
            )
            return

        if not message.strip():
            await interaction.response.send_message(
                "❌ Message cannot be empty!",
                ephemeral=True
            )
            return

        try:
            await target_channel.send(message)
            
            embed = nextcord.Embed(
                title="✅ Message Sent Successfully!",
                description="Your message has been sent!",
                color=0x00FF00
            )
            embed.add_field(
                name="📝 Message Content",
                value=f"```{message}```",
                inline=False
            )
            embed.add_field(
                name="📺 Channel",
                value=f"<#{target_channel.id}>",
                inline=True
            )
            embed.add_field(
                name="👤 Sent By",
                value=f"{interaction.user.mention}",
                inline=True
            )
            embed.add_field(
                name="📊 Message Length",
                value=f"```{len(message)} characters```",
                inline=True
            )
            embed.add_field(
                name="⏰ Sent Time",
                value=f"<t:{int(datetime.now().timestamp())}:R>",
                inline=False
            )
            embed.set_footer(
                text="© Ryujin Bot (2023-2025) | Fun System",
                icon_url=self.RYUJIN_LOGO
            )
            embed.set_author(
                name=f"{interaction.user.name}",
                icon_url=interaction.user.display_avatar.url
            )

            await interaction.response.send_message(embed=embed, ephemeral=True)
            
            await self.bot.maybe_send_ad(interaction)

        except Exception as e:
            error_embed = nextcord.Embed(
                title="❌ Error Sending Message",
                description=f"An error occurred while sending your message: `{str(e)}`",
                color=nextcord.Color.red()
            )
            embed.set_footer(
                text="© Ryujin Bot (2023-2025) | Fun System",
                icon_url=self.RYUJIN_LOGO
            )
            await interaction.response.send_message(embed=error_embed, ephemeral=True)

    @nextcord.slash_command(
        name="say_embed",
        description="Make the bot say something in an embed! 📋"
    )
    async def say_embed(
        self,
        interaction: nextcord.Interaction,
        title: str = nextcord.SlashOption(
            description="Title of the embed",
            required=True
        ),
        description: str = nextcord.SlashOption(
            description="Description/content of the embed",
            required=True
        ),
        color: str = nextcord.SlashOption(
            description="Color of the embed (hex code like #FF0000)",
            required=False,
            default="#2a2a2a"
        ),
        channel: nextcord.TextChannel = nextcord.SlashOption(
            description="Channel to send the embed in (optional)",
            required=False
        )
    ):
        if self.check_blacklist(interaction.user.id):
            embed = self.create_blacklist_embed(self.bot.blacklist[interaction.user.id])
            await interaction.response.send_message(embed=embed, ephemeral=True)
            return

        target_channel = channel or interaction.channel
        
        if not target_channel.permissions_for(interaction.user).send_messages:
            await interaction.response.send_message(
                "❌ You don't have permission to send messages in that channel!",
                ephemeral=True
            )
            return

        if not target_channel.permissions_for(interaction.guild.me).send_messages:
            await interaction.response.send_message(
                "❌ I don't have permission to send messages in that channel!",
                ephemeral=True
            )
            return

        title_restricted, title_pattern = self.check_restricted_content(title)
        desc_restricted, desc_pattern = self.check_restricted_content(description)
        
        if title_restricted or desc_restricted:
            embed = nextcord.Embed(
                title="❌ Restricted Content Detected",
                description="Your embed contains restricted content that cannot be sent.",
                color=nextcord.Color.red()
            )
            if title_restricted:
                embed.add_field(
                    name="🚫 Title Issue",
                    value=f"Pattern: `{title_pattern}`",
                    inline=False
                )
            if desc_restricted:
                embed.add_field(
                    name="🚫 Description Issue",
                    value=f"Pattern: `{desc_pattern}`",
                    inline=False
                )
            embed.set_footer(
                text="© Ryujin Bot (2023-2025) | Fun System",
                icon_url=self.RYUJIN_LOGO
            )
            embed.set_author(
                name=f"Ryujin",
                icon_url=self.RYUJIN_LOGO
            )
            await interaction.response.send_message(embed=embed, ephemeral=True)
            return

        try:
            color_int = int(color.replace('#', ''), 16)
        except ValueError:
            await interaction.response.send_message(
                "❌ Invalid color format! Use hex format like #FF0000",
                ephemeral=True
            )
            return

        if len(title) > 256:
            await interaction.response.send_message(
                "❌ Title is too long! Maximum 256 characters allowed.",
                ephemeral=True
            )
            return

        if len(description) > 4096:
            await interaction.response.send_message(
                "❌ Description is too long! Maximum 4096 characters allowed.",
                ephemeral=True
            )
            return

        try:
            embed = nextcord.Embed(
                title=title,
                description=description,
                color=color_int
            )
            embed.set_footer(
                text=f"Requested by {interaction.user.name}",
                icon_url=interaction.user.display_avatar.url
            )
            embed.set_author(
                name="Ryujin",
                icon_url=self.RYUJIN_LOGO
            )

            await target_channel.send(embed=embed)
            
            success_embed = nextcord.Embed(
                title="✅ Embed Sent Successfully!",
                description="Your embed has been sent!",
                color=0x00FF00
            )
            success_embed.add_field(
                name="📋 Embed Title",
                value=f"```{title}```",
                inline=False
            )
            success_embed.add_field(
                name="📝 Embed Description",
                value=f"```{description[:100]}{'...' if len(description) > 100 else ''}```",
                inline=False
            )
            success_embed.add_field(
                name="🎨 Color",
                value=f"```{color}```",
                inline=True
            )
            success_embed.add_field(
                name="📺 Channel",
                value=f"<#{target_channel.id}>",
                inline=True
            )
            success_embed.add_field(
                name="👤 Sent By",
                value=f"{interaction.user.mention}",
                inline=True
            )
            success_embed.set_footer(
                text="© Ryujin Bot (2023-2025) | Fun System",
                icon_url=self.RYUJIN_LOGO
            )
            success_embed.set_author(
                name=f"Ryujin",
                icon_url=self.RYUJIN_LOGO
            )
            await interaction.response.send_message(embed=success_embed, ephemeral=True)
            
            await self.bot.maybe_send_ad(interaction)

        except Exception as e:
            error_embed = nextcord.Embed(
                title="❌ Error Sending Embed",
                description=f"An error occurred while sending your embed: `{str(e)}`",
                color=nextcord.Color.red()
            )
            error_embed.set_footer(
                text="© Ryujin Bot (2023-2025) | Fun System",
                icon_url=self.RYUJIN_LOGO
            )
            error_embed.set_author(
                name=f"Ryujin",
                icon_url=self.RYUJIN_LOGO
            )
            await interaction.response.send_message(embed=error_embed, ephemeral=True)

def setup(bot):
    bot.add_cog(SayCog(bot)) 