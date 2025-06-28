import nextcord
from nextcord.ext import commands
import time
import platform
import psutil
from datetime import datetime

class PingCog(commands.Cog):
    def __init__(self, bot):
        self.bot = bot
        self.RYUJIN_LOGO = "https://cdn.discordapp.com/avatars/1059400568805785620/63a77f852ea29f37961f458c53fb5a97.png"

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

    def get_latency_color(self, latency):
        """Get color based on latency"""
        if latency < 50:
            return 0x00FF00
        elif latency < 100:
            return 0xFFFF00
        elif latency < 200:
            return 0xFFA500
        else:
            return 0xFF0000

    def get_latency_status(self, latency):
        """Get status text based on latency"""
        if latency < 50:
            return "🟢 Excellent"
        elif latency < 100:
            return "🟡 Good"
        elif latency < 200:
            return "🟠 Fair"
        else:
            return "🔴 Poor"

    @nextcord.slash_command(
        name="ping",
        description="Check bot latency and response time! 🏓"
    )
    async def ping(
        self,
        interaction: nextcord.Interaction
    ):
        if self.check_blacklist(interaction.user.id):
            embed = self.create_blacklist_embed(self.bot.blacklist[interaction.user.id])
            await interaction.response.send_message(embed=embed, ephemeral=True)
            return

        start_time = time.time()
        
        bot_latency = round(self.bot.latency * 1000, 2)
        
        await interaction.response.send_message("🏓 **Pong!** Measuring latency...")
        
        api_latency = round((time.time() - start_time) * 1000, 2)
        
        cpu_percent = psutil.cpu_percent()
        memory = psutil.virtual_memory()
        memory_percent = memory.percent
        
        color = self.get_latency_color(bot_latency)
        status = self.get_latency_status(bot_latency)
        
        embed = nextcord.Embed(
            title="🏓 **Pong!**",
            description="Here's my current latency and system status!",
            color=color
        )
        
        embed.add_field(
            name="📡 Bot Latency",
            value=f"```{bot_latency}ms```",
            inline=True
        )
        
        embed.add_field(
            name="⚡ API Latency",
            value=f"```{api_latency}ms```",
            inline=True
        )
        
        embed.add_field(
            name="📊 Status",
            value=f"```{status}```",
            inline=True
        )
        
        embed.add_field(
            name="🖥️ System Info",
            value=f"**CPU:** {cpu_percent}%\n**RAM:** {memory_percent}%\n**Platform:** {platform.system()}",
            inline=True
        )
        
        embed.add_field(
            name="🤖 Bot Info",
            value=f"**Python:** {platform.python_version()}\n**Nextcord:** {nextcord.__version__}\n**Servers:** {len(self.bot.guilds)}",
            inline=True
        )
        
        embed.add_field(
            name="⏰ Response Time",
            value=f"<t:{int(datetime.now().timestamp())}:R>",
            inline=True
        )
        
        if bot_latency < 50:
            comparison = "🚀 **Lightning fast!** Your connection is excellent!"
        elif bot_latency < 100:
            comparison = "⚡ **Very good!** Your connection is solid!"
        elif bot_latency < 200:
            comparison = "📡 **Acceptable!** Your connection is working fine."
        else:
            comparison = "🐌 **Slow connection!** Consider checking your internet."
        
        embed.add_field(
            name="💡 Connection Quality",
            value=comparison,
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

        await interaction.edit_original_message(content=None, embed=embed)
        
        await self.bot.maybe_send_ad(interaction)

    @nextcord.slash_command(
        name="pong",
        description="Respond with ping! 🏓"
    )
    async def pong(
        self,
        interaction: nextcord.Interaction
    ):
        if self.check_blacklist(interaction.user.id):
            embed = self.create_blacklist_embed(self.bot.blacklist[interaction.user.id])
            await interaction.response.send_message(embed=embed, ephemeral=True)
            return

        embed = nextcord.Embed(
            title="🏓 **Ping!**",
            description="You said pong, so I say ping!",
            color=0x2a2a2a
        )
        
        embed.add_field(
            name="🎯 Response",
            value="**Ping!** 🏓",
            inline=False
        )
        
        embed.add_field(
            name="⏰ Response Time",
            value=f"<t:{int(datetime.now().timestamp())}:R>",
            inline=True
        )
        
        embed.add_field(
            name="👤 Requested By",
            value=f"{interaction.user.mention}",
            inline=True
        )
        
        embed.set_footer(
            text="© Ryujin Bot (2023-2025) | Fun System",
            icon_url=self.RYUJIN_LOGO
        )
        embed.set_author(
            name="Ryujin",
            icon_url=self.RYUJIN_LOGO
        )

        await interaction.response.send_message(embed=embed)
        
        await self.bot.maybe_send_ad(interaction)

    @nextcord.slash_command(
        name="latency",
        description="Get detailed latency information! 📊"
    )
    async def latency(
        self,
        interaction: nextcord.Interaction
    ):
        if self.check_blacklist(interaction.user.id):
            embed = self.create_blacklist_embed(self.bot.blacklist[interaction.user.id])
            await interaction.response.send_message(embed=embed, ephemeral=True)
            return

        start_time = time.time()
        
        bot_latency = round(self.bot.latency * 1000, 2)
        
        await interaction.response.send_message("📊 **Measuring detailed latency...**")
        
        api_latency = round((time.time() - start_time) * 1000, 2)
        
        cpu_percent = psutil.cpu_percent()
        memory = psutil.virtual_memory()
        memory_percent = memory.percent
        memory_used = round(memory.used / (1024**3), 2)
        memory_total = round(memory.total / (1024**3), 2)
        
        disk = psutil.disk_usage('/')
        disk_percent = round((disk.used / disk.total) * 100, 2)
        disk_used = round(disk.used / (1024**3), 2)
        disk_total = round(disk.total / (1024**3), 2)
        
        color = self.get_latency_color(bot_latency)
        status = self.get_latency_status(bot_latency)
        
        embed = nextcord.Embed(
            title="📊 **Detailed Latency Report**",
            description="Comprehensive system and network information",
            color=color
        )
        
        embed.add_field(
            name="🌐 Network Latency",
            value=f"**Bot Latency:** {bot_latency}ms\n**API Latency:** {api_latency}ms\n**Status:** {status}",
            inline=False
        )
        
        embed.add_field(
            name="🖥️ System Resources",
            value=f"**CPU Usage:** {cpu_percent}%\n**RAM Usage:** {memory_percent}% ({memory_used}GB/{memory_total}GB)\n**Disk Usage:** {disk_percent}% ({disk_used}GB/{disk_total}GB)",
            inline=False
        )
        
        embed.add_field(
            name="🤖 Bot Statistics",
            value=f"**Servers:** {len(self.bot.guilds)}\n**Users:** {sum(len(guild.members) for guild in self.bot.guilds)}\n**Channels:** {sum(len(guild.channels) for guild in self.bot.guilds)}",
            inline=True
        )
        
        embed.add_field(
            name="🔧 Technical Info",
            value=f"**Python:** {platform.python_version()}\n**Nextcord:** {nextcord.__version__}\n**Platform:** {platform.system()} {platform.release()}",
            inline=True
        )
        
        if bot_latency < 50 and cpu_percent < 50 and memory_percent < 70:
            performance = "🟢 **Excellent Performance**"
        elif bot_latency < 100 and cpu_percent < 70 and memory_percent < 85:
            performance = "🟡 **Good Performance**"
        elif bot_latency < 200 and cpu_percent < 85 and memory_percent < 95:
            performance = "🟠 **Fair Performance**"
        else:
            performance = "🔴 **Poor Performance**"
        
        embed.add_field(
            name="📈 Performance Status",
            value=performance,
            inline=False
        )
        
        embed.add_field(
            name="⏰ Report Time",
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

        await interaction.edit_original_message(content=None, embed=embed)
        
        await self.bot.maybe_send_ad(interaction)

def setup(bot):
    bot.add_cog(PingCog(bot)) 