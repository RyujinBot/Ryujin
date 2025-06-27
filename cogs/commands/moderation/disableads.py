import nextcord
from nextcord.ext import commands

class DisableAdsCog(commands.Cog):
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
        name="disableads",
        description="Disable promotional messages in this server",
    )
    async def disableads(self, interaction: nextcord.Interaction):
        user_id = interaction.user.id
        is_blacklisted, blacklist_reason = self.check_blacklist(user_id)
        
        if is_blacklisted:
            embed = self.create_blacklist_embed(blacklist_reason)
            await interaction.send(embed=embed, ephemeral=True)
            return

        if not (interaction.user.id == 977190163736322088 or 
                interaction.user == interaction.guild.owner or 
                interaction.user.guild_permissions.administrator):
            await interaction.send(
                "Only the server owner or administrators can disable ads.",
                ephemeral=True
            )
            return

        cursor = self.bot.connection.cursor()
        cursor.execute("SELECT server_id FROM disableads_servers WHERE server_id = %s", (interaction.guild.id,))
        result = cursor.fetchone()
        
        if result:
            embed = nextcord.Embed(
                title="Already Disabled",
                description="Promotional messages are already disabled in this server!",
                color=0x2a2a2a
            )
        else:
            cursor.execute("INSERT INTO disableads_servers (server_id) VALUES (%s)", (interaction.guild.id,))
            self.bot.connection.commit()
            
            embed = nextcord.Embed(
                title="Ads Disabled", 
                description="Promotional messages have been disabled for this server!",
                color=0x2a2a2a
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

def setup(bot):
    bot.add_cog(DisableAdsCog(bot)) 