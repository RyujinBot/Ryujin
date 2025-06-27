import nextcord
from nextcord.ext import commands
import platform
import psutil
from datetime import datetime

class BotStatsCog(commands.Cog):
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
        name="bot_stats",
        description="Display detailed statistics about the bot.",
    )
    async def bot_stats(self, interaction: nextcord.Interaction):
        user_id = interaction.user.id
        is_blacklisted, reason = self.check_blacklist(user_id)
        
        if is_blacklisted:
            embed = self.create_blacklist_embed(reason)
            await interaction.send(embed=embed, ephemeral=True)
            return

        total_servers = len(self.bot.guilds)
        total_members = sum(len(guild.members) for guild in self.bot.guilds)
        current_time = datetime.now()
        uptime = current_time - self.bot.start_time
        latency_ms = round(self.bot.latency * 1000, 2)
        
        days = uptime.days
        hours, remainder = divmod(uptime.seconds, 3600)
        minutes, seconds = divmod(remainder, 60)
        uptime_str = f"{days}d {hours}h {minutes}m {seconds}s"

        process = psutil.Process()
        memory_usage = process.memory_info().rss / 1024 / 1024

        description = (
            f"🌐 **Servers:** {total_servers:,}\n"
            f"👥 **Total Members:** {total_members:,}\n"
            f"⏰ **Uptime:** {uptime_str}\n"
            f"📶 **Latency:** {latency_ms}ms\n"
            f"💾 **Memory Usage:** {memory_usage:.1f} MB\n"
            f"🔄 **Bot Version:** 0.6b\n"
            f"👨‍💻 **Bot Developer:** moongetsu\n\n"
            f"**Python Version:** {platform.python_version()}\n"
            f"**Nextcord Version:** {nextcord.__version__}"
        )
        
        embed = nextcord.Embed(
            title="📊 Ryujin Statistics",
            description=description,
            color=0x2a2a2a,
        )
        embed.set_author(
            name="Ryujin",
            icon_url=self.RYUJIN_LOGO
        )
        embed.set_footer(
            text="© Ryujin Bot (2023-2025) | Information System",
            icon_url=self.RYUJIN_LOGO
        )
        await self.bot.maybe_send_ad(interaction)
        await interaction.send(embed=embed, ephemeral=True)

def setup(bot):
    bot.add_cog(BotStatsCog(bot)) 