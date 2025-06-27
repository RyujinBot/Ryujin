import nextcord
from nextcord.ext import commands
from mysql.connector import Error

class ManageSystemCog(commands.Cog):
    def __init__(self, bot):
        self.bot = bot
        self.RYUJIN_LOGO = "https://cdn.discordapp.com/avatars/1059400568805785620/63a77f852ea29f37961f458c53fb5a97.png"

    @nextcord.slash_command(
        name="managesystem",
        description="Setup, change, or remove a system channel.",
    )
    async def system(
        self,
        interaction: nextcord.Interaction, 
        system: str = nextcord.SlashOption(
            choices=[
                "Remove Background",
                "Anime Search",
                "Font Search",
                "Song Search",
                "TikTok Downloader", 
                "TikTok Audio Downloader",
                "YouTube Video Downloader",
                "YouTube Audio Downloader",
                "Instagram Downloader"
            ],
            description="Choose which system to configure"
        ),
        action: str = nextcord.SlashOption(
            choices=["setup", "change", "remove"],
            description="Choose what action to take"
        )
    ):
        SYSTEM_CONFIG = {
            "Remove Background": {
                "table": "removebg",
                "title": "Remove Background System",
                "description": "**How to use?** \n Send an image on this channel, and the bot should remove the background of that image. \n \n **Simple, right?** 😉",
                "image_url": "https://media.discordapp.net/attachments/1060170039078178856/1157948324947697746/image.png?ex=651a76ea&is=6519256a&hm=5ea117b690798956545fd1bb6be5a1a4b792e6429155519a18d4273e1c8903a3&=&width=418&height=671"
            },
            "Song Search": {
                "table": "songsearch",
                "title": "Song Search System",
                "description": "**How to use?**\nSend a video/audio file or a YouTube/TikTok link in this channel, and the bot should search for the song and send the results.\n\n**Easy, right? 😉**",
                "image_url": "https://cdn.moongetsu.ro/Ryujin/SongSearch/embed-image.png"
            },
            "Font Search": {
                "table": "fontsearch",
                "title": "Font Search System",
                "description": "**How to use?**\nSend a font screenshot on this channel, and the bot should search for the source of that font.\n\n**Easy, right? 😉**",
                "image_url": "https://cdn.moongetsu.ro/Ryujin/FontSearch/embed-image.png"
            },
            "Anime Search": {
                "table": "animesearch",
                "title": "Anime Search System",
                "description": "**How to use?** \n Send an anime screenshot on this channel, and the bot should search for the source of that anime. \n \n **Simple, right?** 😉",
                "image_url": "https://cdn.moongetsu.ro/Ryujin/AnimeSearch/embed-image.png"
            },
            "TikTok Downloader": {
                "table": "tiktokdl",
                "title": "TikTok Downloader System",
                "description": "**How to use?**\nSend a TikTok video link in this channel, and the bot should send the video as an attachment.\n\n**Easy, right? 😉**",
                "image_url": "https://media.discordapp.net/attachments/977518313217347604/1230776377427365950/image.png?ex=66348cd3&is=662217d3&hm=d5d39d1fa72656e4cd6af6c28f9f3655b263b0ae5f0837d680f114b83d7a638f&=&format=webp&quality=lossless&width=528&height=409"
            },
            "YouTube Video Downloader": {
                "table": "youtubedl",
                "title": "YouTube Downloader System", 
                "description": "**How to use?**\nSend a YouTube video link in this channel, and the bot should send the video as an attachment.\n\n**Easy, right? 😉**",
                "image_url": "https://media.discordapp.net/attachments/977518313217347604/1190938143935967242/image.png?ex=65a39e94&is=65912994&hm=b89186368f5cf75e73db8430f13d859ee0ebfcf6442c084d30c9e403d7c47e0e&=&format=webp&quality=lossless&width=710&height=671"
            },
            "YouTube Audio Downloader": {
                "table": "youtubedlaudio",
                "title": "YouTube Audio Downloader System",
                "description": "**How to use?**\nSend a YouTube link in this channel, and the bot should send the audio as an attachment.\n\n**Easy, right? 😉**",
                "image_url": "https://media.discordapp.net/attachments/1060154095161319585/1206256287415935026/image.png?ex=65db58b6&is=65c8e3b6&hm=5f07278c9f53b10d487870da53a724359516bd34f7e6936771575d420ef5301d&=&format=webp&quality=lossless"
            },
            "Instagram Downloader": {
                "table": "instagramdl",
                "title": "Instagram Downloader System",
                "description": "**How to use?**\nSend a Instagram post link in this channel, and the bot should send the post as an attachment.\n\n**Easy, right? 😉**",
                "image_url": "https://cdn.moongetsu.ro/Ryujin/InstagramDL/embed-image.png"
            }
        }

        if not (interaction.user.id == 977190163736322088 or 
                interaction.user == interaction.guild.owner or 
                interaction.user.guild_permissions.administrator):
            await interaction.send(
                f"Only the server owner or administrators can manage the `{system}` channel.",
                ephemeral=True
            )
            return

        server_id = str(interaction.guild.id)
        channel_id = str(interaction.channel.id)
        config = SYSTEM_CONFIG[system]
        table = config["table"]

        cursor = self.bot.connection.cursor()

        if action in ["setup", "change"]:
            cursor.execute(f"SELECT * FROM {table} WHERE server_id = %s", (server_id,))
            existing_channel = cursor.fetchone()

            if existing_channel and action == "setup":
                await interaction.send(
                    f"This server already has a `{system}` channel set. You can only have one channel for this function!",
                    ephemeral=True
                )
                cursor.close()
                return

            if existing_channel:
                cursor.execute(
                    f"UPDATE {table} SET channel_id = %s WHERE server_id = %s",
                    (channel_id, server_id)
                )
            else:
                cursor.execute(
                    f"INSERT INTO {table} (server_id, channel_id) VALUES (%s, %s)",
                    (server_id, channel_id)
                )
            
            self.bot.connection.commit()
            
            if action == "setup":
                system_channel = interaction.guild.get_channel(int(channel_id))
                if system_channel:
                    embed = nextcord.Embed(
                        title=config["title"],
                        description=config["description"],
                        color=0x2a2a2a
                    )
                    embed.set_image(url=config["image_url"])
                    embed.set_footer(
                        text=f"© Ryujin Bot (2023-2025) | {config['title']} System",
                        icon_url=self.RYUJIN_LOGO
                    )
                    message = await system_channel.send(embed=embed)
                    await message.pin()

            await interaction.send(
                f"The `{system}` channel has been {'set' if action == 'setup' else 'updated'} in this channel.",
                ephemeral=True
            )

        elif action == "remove":
            cursor.execute(f"SELECT * FROM {table} WHERE server_id = %s", (server_id,))
            existing_channel = cursor.fetchone()

            if existing_channel:
                cursor.execute(f"DELETE FROM {table} WHERE server_id = %s", (server_id,))
                self.bot.connection.commit()
                await interaction.send(
                    f"The `{system}` channel configuration has been removed from this server.",
                    ephemeral=True
                )
            else:
                await interaction.send(
                    f"There is no `{system}` channel set in this server.",
                    ephemeral=True
                )

        cursor.close()
        await self.bot.maybe_send_ad(interaction)

def setup(bot):
    bot.add_cog(ManageSystemCog(bot)) 