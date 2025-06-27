import nextcord
from nextcord.ext import commands
from datetime import datetime
import json
import os

class AfkCog(commands.Cog):
    def __init__(self, bot):
        self.bot = bot
        self.RYUJIN_LOGO = "https://cdn.discordapp.com/avatars/1059400568805785620/63a77f852ea29f37961f458c53fb5a97.png"
        self.afk_file = "config/afk.json"
        self.afk_users = self.load_afk_data()

    def load_afk_data(self):
        """Load AFK data from JSON file"""
        if os.path.exists(self.afk_file):
            try:
                with open(self.afk_file, 'r') as f:
                    return json.load(f)
            except (json.JSONDecodeError, FileNotFoundError):
                return {}
        return {}

    def save_afk_data(self):
        """Save AFK data to JSON file"""
        os.makedirs(os.path.dirname(self.afk_file), exist_ok=True)
        with open(self.afk_file, 'w') as f:
            json.dump(self.afk_users, f, indent=4)

    def check_blacklist(self, user_id):
        """Check if user is blacklisted"""
        if hasattr(self.bot, 'blacklist') and user_id in self.bot.blacklist:
            return True, self.bot.blacklist[user_id]
        return False, None

    def create_blacklist_embed(self, reason):
        """Create blacklist embed"""
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
        name="afk",
        description="Set yourself as AFK (Away From Keyboard)."
    )
    async def afk(
        self, 
        interaction: nextcord.Interaction, 
        reason: str = nextcord.SlashOption(
            description="Reason for being AFK (optional)",
            required=False,
            default="No reason provided"
        )
    ):
        """Set AFK status"""
        user_id = interaction.user.id
        is_blacklisted, blacklist_reason = self.check_blacklist(user_id)
        
        if is_blacklisted:
            embed = self.create_blacklist_embed(blacklist_reason)
            await interaction.send(embed=embed, ephemeral=True)
            return

        # Set AFK status
        current_time = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        self.afk_users[str(user_id)] = {
            "reason": reason,
            "timestamp": current_time,
            "guild_id": str(interaction.guild.id) if interaction.guild else None
        }
        self.save_afk_data()

        embed = nextcord.Embed(
            title="🟡 AFK Status Set",
            description=f"You are now **AFK**\n\n📝 **Reason:** {reason}\n⏰ **Set at:** {current_time}",
            color=0xFFD700
        )
        embed.set_author(
            name=f"{interaction.user.display_name}",
            icon_url=interaction.user.display_avatar.url
        )
        embed.set_footer(
            text="© Ryujin Bot (2023-2025) | AFK System",
            icon_url=self.RYUJIN_LOGO
        )

        await self.bot.maybe_send_ad(interaction)
        await interaction.send(embed=embed, ephemeral=True)

    @commands.Cog.listener()
    async def on_message(self, message):
        """Handle AFK removal when user sends a message"""
        if message.author.bot:
            return

        user_id = str(message.author.id)
        
        # Check if user is AFK and remove AFK status
        if user_id in self.afk_users:
            afk_data = self.afk_users[user_id]
            del self.afk_users[user_id]
            self.save_afk_data()

            embed = nextcord.Embed(
                title="🟢 Welcome Back!",
                description=f"Your AFK status has been removed.\n\n⏰ **You were AFK for:** {afk_data['reason']}",
                color=0x00FF00
            )
            embed.set_author(
                name=f"{message.author.display_name}",
                icon_url=message.author.display_avatar.url
            )
            embed.set_footer(
                text="© Ryujin Bot (2023-2025) | AFK System",
                icon_url=self.RYUJIN_LOGO
            )

            await message.channel.send(embed=embed, delete_after=10)

        # Check for mentions of AFK users
        for mention in message.mentions:
            mentioned_user_id = str(mention.id)
            if mentioned_user_id in self.afk_users:
                afk_data = self.afk_users[mentioned_user_id]
                
                embed = nextcord.Embed(
                    title="🟡 User is AFK",
                    description=f"{mention.mention} is currently **AFK**\n\n📝 **Reason:** {afk_data['reason']}\n⏰ **Since:** {afk_data['timestamp']}",
                    color=0xFFD700
                )
                embed.set_author(
                    name=f"{mention.display_name}",
                    icon_url=mention.display_avatar.url
                )
                embed.set_footer(
                    text="© Ryujin Bot (2023-2025) | AFK System",
                    icon_url=self.RYUJIN_LOGO
                )

                await message.channel.send(embed=embed, delete_after=15)

    @nextcord.slash_command(
        name="afk_list",
        description="Show all AFK users in the current server."
    )
    async def afk_list(self, interaction: nextcord.Interaction):
        """Show AFK users list"""
        user_id = interaction.user.id
        is_blacklisted, reason = self.check_blacklist(user_id)
        
        if is_blacklisted:
            embed = self.create_blacklist_embed(reason)
            await interaction.send(embed=embed, ephemeral=True)
            return

        guild_id = str(interaction.guild.id)
        afk_users_in_guild = []

        for user_id_str, afk_data in self.afk_users.items():
            if afk_data.get("guild_id") == guild_id:
                try:
                    user = await self.bot.fetch_user(int(user_id_str))
                    afk_users_in_guild.append({
                        "user": user,
                        "data": afk_data
                    })
                except:
                    continue

        if not afk_users_in_guild:
            embed = nextcord.Embed(
                title="📋 AFK Users",
                description="No users are currently AFK in this server.",
                color=0x2a2a2a
            )
        else:
            description = ""
            for afk_user in afk_users_in_guild:
                user = afk_user["user"]
                data = afk_user["data"]
                description += f"👤 **{user.display_name}**\n📝 {data['reason']}\n⏰ {data['timestamp']}\n\n"

            embed = nextcord.Embed(
                title="📋 AFK Users",
                description=description,
                color=0x2a2a2a
            )

        embed.set_footer(
            text="© Ryujin Bot (2023-2025) | AFK System",
            icon_url=self.RYUJIN_LOGO
        )

        await self.bot.maybe_send_ad(interaction)
        await interaction.send(embed=embed, ephemeral=True)

def setup(bot):
    bot.add_cog(AfkCog(bot)) 