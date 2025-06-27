import nextcord
from nextcord.ext import commands

class ServerInfoCog(commands.Cog):
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
        name="server_info",
        description="Display detailed information about the current server."
    )
    async def server_info(self, interaction: nextcord.Interaction):
        user_id = interaction.user.id
        is_blacklisted, reason = self.check_blacklist(user_id)
        
        if is_blacklisted:
            embed = self.create_blacklist_embed(reason)
            await interaction.send(embed=embed, ephemeral=True)
            return

        guild = interaction.guild
        
        created_at = guild.created_at.strftime("%B %d, %Y")
        
        total_members = guild.member_count
        bot_count = len([m for m in guild.members if m.bot])
        human_count = total_members - bot_count
        
        text_channels = len(guild.text_channels)
        voice_channels = len(guild.voice_channels)
        categories = len(guild.categories)
        
        role_count = len(guild.roles)
        
        boost_level = guild.premium_tier
        boost_count = guild.premium_subscription_count
        
        verification_levels = {
            nextcord.VerificationLevel.low: "Low",
            nextcord.VerificationLevel.medium: "Medium", 
            nextcord.VerificationLevel.high: "High",
            nextcord.VerificationLevel.highest: "Highest"
        }
        verification = verification_levels.get(guild.verification_level, "Unknown")
        
        features = []
        if guild.features:
            features = [feature.replace('_', ' ').title() for feature in guild.features]
        
        description = (
            f"📊 **Server Information**\n\n"
            f"🏷️ **Name:** {guild.name}\n"
            f"🆔 **ID:** {guild.id}\n"
            f"📅 **Created:** {created_at}\n"
            f"🌍 **Region:** {guild.region if hasattr(guild, 'region') else 'N/A'}\n\n"
            
            f"👥 **Members:** {total_members:,}\n"
            f"👤 **Humans:** {human_count:,}\n"
            f"🤖 **Bots:** {bot_count:,}\n"
            f"📈 **Boost Level:** {boost_level}\n"
            f"🚀 **Boosts:** {boost_count}\n\n"
            
            f"📝 **Channels:** {text_channels + voice_channels}\n"
            f"💬 **Text:** {text_channels}\n"
            f"🔊 **Voice:** {voice_channels}\n"
            f"📁 **Categories:** {categories}\n"
            f"🎭 **Roles:** {role_count}\n"
            f"🔒 **Verification:** {verification}\n"
        )
        
        if features:
            description += f"\n✨ **Features:** {', '.join(features[:5])}"
            if len(features) > 5:
                description += f" and {len(features) - 5} more..."
        
        embed = nextcord.Embed(
            title=f"📊 {guild.name}",
            description=description,
            color=0x2a2a2a
        )
        
        if guild.icon:
            embed.set_thumbnail(url=guild.icon.url)
        
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
    bot.add_cog(ServerInfoCog(bot)) 