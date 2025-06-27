import nextcord
from nextcord.ext import commands

class ShowGuildsCog(commands.Cog):
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
        name="show_guilds",
        description="Shows all the guilds that Ryujin is in!",
    )
    async def show_guilds(self, interaction: nextcord.Interaction):
        user_id = interaction.user.id
        is_blacklisted, reason = self.check_blacklist(user_id)
        
        if is_blacklisted:
            embed = self.create_blacklist_embed(reason)
            await interaction.send(embed=embed, ephemeral=True)
            return

        if interaction.user.id == 977190163736322088:
            guilds = list(self.bot.guilds)
            guilds.sort(key=lambda guild: guild.member_count, reverse=True)

            chunked_guilds = [guilds[i:i + 25] for i in range(0, len(guilds), 25)]

            for index, guild_chunk in enumerate(chunked_guilds):
                fields = []
                
                for guild in guild_chunk:
                    truncated_name = guild.name[:25]
                    if len(guild.name) > 25:
                        truncated_name += "..."
                    
                    fields.append((truncated_name, f"{guild.member_count} members\nOwner: **{guild.owner}**"))
                
                embed = nextcord.Embed(
                    title=f"Info about the guilds that Ryujin is in (Part {index + 1})",
                    description=f"<@1060316037997936751> is in **{len(guilds)}** guilds."
                )
                embed.set_author(name="Ryujin", icon_url=self.RYUJIN_LOGO)
                embed.set_footer(
                    text="© Ryujin Bot (2023-2025) | Development System",
                    icon_url=self.RYUJIN_LOGO
                )
                
                for name, value in fields:
                    embed.add_field(name=name, value=value)
                
                await self.bot.maybe_send_ad(interaction)
                await interaction.send(embed=embed, ephemeral=True)
        else:
            await interaction.send("This command is working only for `moongetsu`.", ephemeral=True)

def setup(bot):
    bot.add_cog(ShowGuildsCog(bot)) 