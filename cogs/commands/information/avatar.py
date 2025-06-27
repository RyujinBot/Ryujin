import nextcord
from nextcord.ext import commands

class AvatarCog(commands.Cog):
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
        name="avatar",
        description="Display a user's avatar."
    )
    async def avatar(
        self, 
        interaction: nextcord.Interaction, 
        user: nextcord.Member = nextcord.SlashOption(
            description="User to get avatar for (defaults to you)",
            required=False
        )
    ):
        user_id = interaction.user.id
        is_blacklisted, reason = self.check_blacklist(user_id)
        
        if is_blacklisted:
            embed = self.create_blacklist_embed(reason)
            await interaction.send(embed=embed, ephemeral=True)
            return

        if user is None:
            user = interaction.user
        
        embed = nextcord.Embed(
            title=f"🖼️ {user.display_name}'s Avatar",
            color=0x2a2a2a
        )
        
        avatar_url = user.display_avatar.url
        
        embed.set_image(url=avatar_url)
        
        embed.set_footer(
            text="© Ryujin Bot (2023-2025) | Information System",
            icon_url=self.RYUJIN_LOGO
        )

        embed.set_author(
            name=user.display_name,
            icon_url=avatar_url
        )

        view = nextcord.ui.View()
        
        png_button = nextcord.ui.Button(
            label="PNG", 
            style=nextcord.ButtonStyle.primary,
            emoji="📥",
            url=avatar_url
        )
        view.add_item(png_button)

        jpg_button = nextcord.ui.Button(
            label="JPG",
            style=nextcord.ButtonStyle.primary, 
            emoji="📥",
            url=avatar_url.replace('.png', '.jpg')
        )
        view.add_item(jpg_button)

        webp_button = nextcord.ui.Button(
            label="WebP",
            style=nextcord.ButtonStyle.primary,
            emoji="📥", 
            url=avatar_url.replace('.png', '.webp')
        )
        view.add_item(webp_button)

        await self.bot.maybe_send_ad(interaction)
        await interaction.send(embed=embed, view=view, ephemeral=True)

def setup(bot):
    bot.add_cog(AvatarCog(bot)) 