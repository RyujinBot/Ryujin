import nextcord
from nextcord.ext import commands
import random

class RandomEditCog(commands.Cog):
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
        name="random_edit",
        description="Sends a random edit. Good command if you don't have ideas what to edit.",
    )
    async def random_edit(self, interaction: nextcord.Interaction):
        user_id = interaction.user.id
        is_blacklisted, reason = self.check_blacklist(user_id)
        
        if is_blacklisted:
            embed = self.create_blacklist_embed(reason)
            await interaction.send(embed=embed, ephemeral=True)
            return

        with open("edits.txt", "r") as f:
            lines = f.read().strip().split("\n")
        
        link = random.choice(lines)
        button_view = AnotherButtonEdit()
        await self.bot.maybe_send_ad(interaction)
        await interaction.send(link, ephemeral=True, view=button_view)

class AnotherButtonEdit(nextcord.ui.View):
    def __init__(self):
        super().__init__()
        self.add_item(nextcord.ui.Button(
            style=nextcord.ButtonStyle.gray,
            label="Another Edit 👀",
            custom_id="another_edit"
        ))

    @nextcord.ui.button(
        style=nextcord.ButtonStyle.gray,
        label="Another Edit",
        custom_id="another_edit"
    )
    async def another_edit(self, button: nextcord.ui.Button, interaction: nextcord.Interaction):
        with open("edits.txt", "r") as f:
            lines = f.read().strip().split("\n")
        new_link = random.choice(lines)
        await interaction.response.edit_message(content=new_link, view=self)
        # Note: maybe_send_ad is not available in this context, so we'll skip it

def setup(bot):
    bot.add_cog(RandomEditCog(bot)) 