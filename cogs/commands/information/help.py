import nextcord
from nextcord.ext import commands
from datetime import datetime

class HelpCog(commands.Cog):
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
        name="help",
        description="Shows all Ryujin's commands!",
    )
    async def help(self, interaction: nextcord.Interaction):
        user_id = interaction.user.id
        is_blacklisted, reason = self.check_blacklist(user_id)
        
        if is_blacklisted:
            embed = self.create_blacklist_embed(reason)
            await interaction.send(embed=embed, ephemeral=True)
            return

        commands_dict = {
            "Information": [
                ("info", "Shows information about the bot"),
                ("help", "Shows all Ryujin's commands"),
                ("resources", "Shows all the available editing resources"),
                ("bug", "Sends the server support link to report a bug"),
                ("donate", "Support the development of Ryujin"),
                ("bot_stats", "Display detailed statistics about the bot")
            ],
            "Media Tools": [
                ("overlay", "Sends a random overlay"),
                ("edit_audio <style>", "Sends a random edit audio for each style"),
                ("audios_categories", "Shows all the available audio categories"),
                ("random_edit", "Sends a random edit. Good command if you don't have ideas what to edit"),
                ("compress_file <file>", "Compress a file to reduce its size while maintaining quality"),
                ("resize_video <video> <width> <height>", "Resize a video to a specific resolution while maintaining aspect ratio"),
                ("sfx <category>", "Sends a random SFX from a specific category"),
                ("sfx_categories", "See the SFX categories")
            ],
            "After Effects": [
                ("preset <type>", "Sends a random preset for After Effects from a specific category"),
                ("presets_categories", "Sends all the available preset categories for After Effects"), 
                ("projects_list", "Shows all the available project files for After Effects"),
                ("project_file <name>", "Get a project file with preview"),
                ("scripts_list", "Shows all the available scripts for After Effects"),
                ("script <number>", "Sends a script for After Effects"),
                ("extensions_list", "Shows all the available extensions for After Effects"),
                ("extension <number>", "Sends a extension for After Effects")
            ],
            "Social & Community": [
                ("trending", "See what's trending in AMV Community"),
                ("generatetags", "Generate hashtags based on character name and anime")
            ],
            "Media Processing": [
                ("nightcore <song>", "Converts an uploaded audio file into a Nightcore version"),
                ("spedup <song>", "Converts an uploaded audio file into a Sped Up version"),
                ("slowed <song>", "Converts an uploaded audio file into a Slowed version"),
                ("convert <from_format> <to_format> <file>", "Convert a file from one format to another"),
                ("cut_audio <audio> <start_time> <end_time>", "Cut an audio file to a specific duration")
            ],
            "Moderation": [
                ("managesystem", "Setup, change, or remove a system channel (YouTube, Instagram, TikTok Downloader, Remove Background & Anime Search)"),
                ("disableads", "Disable promotional messages in this server"),
            ]
        }

        embed = nextcord.Embed(
            title="Ryujin Command Guide",
            description="Here's everything I can help you with:",
            color=0x2a2a2a
        )

        for category, cmds in commands_dict.items():
            formatted_commands = "\n".join(f"`/{cmd}` • {desc}" for cmd, desc in cmds)
            embed.add_field(
                name=f"━━ {category} ━━",
                value=formatted_commands,
                inline=False
            )

        embed.set_footer(
            text="© Ryujin Bot (2023-2025) | Information System (0.6b)",
            icon_url=self.RYUJIN_LOGO
        )
        embed.set_author(
            name="Ryujin",
            icon_url=self.RYUJIN_LOGO
        )
        await self.bot.maybe_send_ad(interaction)
        await interaction.send(embed=embed, ephemeral=True)

def setup(bot):
    bot.add_cog(HelpCog(bot))