import nextcord
from nextcord.ext import commands
import random
import datetime
import uuid
from tiktok_downloader import snaptik
from datetime import datetime, timedelta
import os
import platform
import sys
import asyncio
import re
from re import search
import colorama
import configparser
from colorama import Fore, Back, Style
import requests
from io import BytesIO
import json
from PIL import Image, ImageDraw, ImageFont
import io
from bs4 import BeautifulSoup
from pytube.exceptions import RegexMatchError
import time
import psutil
import logging
import aiohttp
# import discord
from pytube import YouTube
from pytube.innertube import _default_clients
from nextcord import SlashOption
# import nightcore as nc
import yt_dlp
from discord import File
import glob
# import instaloader
import urllib.parse
import shazamio
from shazamio import Shazam
import subprocess
# import imageio
import numpy as np
import traceback

# Import utils modules
from cogs.utils.db import initialize_database, get_blacklist, add_to_blacklist, get_removebg_channels
from cogs.utils.embeds import create_info_embed, create_ads_embed, create_blacklist_embed, create_servers_embed, SupportButtons
from cogs.utils.config import load_bot_config, load_removebg_config, load_messages_config, save_messages_config, count_presets_in_categories
from cogs.utils.helpers import handle_pagination, AnotherButtonEdit, AnotherButton, GenerateHashtagsModal

_default_clients["ANDROID_MUSIC"] = _default_clients["ANDROID_CREATOR"]
log_file_name = f"logs/bot_logs_{datetime.now().strftime('%Y-%m-%d_%H-%M-%S')}.log"
logging.basicConfig(filename=log_file_name, level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')

RYUJIN_LOGO = "https://cdn.discordapp.com/avatars/1059400568805785620/63a77f852ea29f37961f458c53fb5a97.png"

# Initialize database and get blacklist
connection = initialize_database()
blacklist = {}
if connection:
    blacklist = get_blacklist(connection)
else:
    print("Warning: Database connection failed. Bot will run without database features.")

# Load bot configuration
bot_config = load_bot_config()
TOKEN = bot_config['token']
STATS_CHANNEL = bot_config['stats_channel']
INFO_CHANNEL = bot_config['info_channel']
WELCOME_LEAVE_CHANNEL = bot_config['welcome_leave_channel']

# Load other configurations
api_keys = load_removebg_config()
PREFIX = "+"

intents = nextcord.Intents.default()
intents.message_content = True
bot = commands.Bot(command_prefix="!", intents=intents)

# Add bot attributes that cogs need
bot.blacklist = blacklist
bot.connection = connection
bot.RYUJIN_LOGO = RYUJIN_LOGO

# Make maybe_send_ad available as a bot method
async def maybe_send_ad(interaction: nextcord.Interaction):
    """Sends an ad with 20% probability if ads are not disabled"""
    if not connection:
        return
        
    cursor = connection.cursor()

    cursor.execute("SELECT server_id FROM disableads_servers WHERE server_id = %s", (str(interaction.guild.id),))
    if cursor.fetchone():
        return

    system_channels = []
    SYSTEM_CONFIG = {
        "Remove Background": {
            "table": "removebg"
        },
        "Anime Search": {
            "table": "animesearch"
        },
        "TikTok Downloader": {
            "table": "tiktokdl"
        },
        "YouTube Video Downloader": {
            "table": "youtubedl"
        },
        "YouTube Audio Downloader": {
            "table": "youtubedlaudio"
        },
        "Instagram Downloader": {
            "table": "instagramdl"
        },
        "Song Search": {
            "table": "songsearch"
        },
        "Font Search": {
            "table": "fontsearch"
        }
    }
    for system in SYSTEM_CONFIG:
        table = SYSTEM_CONFIG[system]["table"]
        cursor.execute(f"SELECT channel_id FROM {table} WHERE server_id = %s", (str(interaction.guild.id),))
        result = cursor.fetchone()
        if result:
            system_channels.append(int(result[0]))

    if random.random() < 0.2 and system_channels:
        embed = create_ads_embed()
        view = SupportButtons()
        
        channel_id = random.choice(system_channels)
        channel = interaction.guild.get_channel(channel_id)
        if channel:
            await channel.send(embed=embed, view=view)

bot.maybe_send_ad = maybe_send_ad

@bot.event
async def on_ready():
    """Event triggered when the bot is ready"""
    bot.start_time = datetime.now()

    print("\n" + "═"*100)
    print(f"{'RYUJIN BOT STARTUP':^100}")
    print("═"*100 + "\n")

    # Load cogs first
    print("Loading cogs...")
    await load_cogs()
    print("Cogs loaded successfully!\n")

    # Define paths to avoid f-string backslash issues
    overlays_path = "resources/overlays"
    sfx_path = "resources/sfx"
    edit_audio_path = "resources/edit audios"
    
    startup_info = [
        ('🤖 Bot Information', [
            f'✅ Connected as {bot.user.name} (ID: {bot.user.id})',
            f'✅ Running Python {platform.python_version()}',
            f'✅ Nextcord {nextcord.__version__}',
            f'✅ Operating System: {platform.system()} {platform.release()} ({os.name})'
        ])
    ]

    for section_name, items in startup_info:
        print(f"{section_name}")
        print("─" * 50)
        for item in items:
            print(item)
        print()

    print("═"*100 + "\n")

    print("Bot startup completed successfully!")
    for section_name, items in startup_info:
        for item in items:
            logging.info(item)

    # Start background tasks
    bot.loop.create_task(change_status())
    bot.loop.create_task(update_info_message())
    bot.loop.create_task(update_servers_message())
    
    # Sync slash commands
    print("🔄 Syncing slash commands with Discord...")
    try:
        await bot.sync_all_application_commands()
        print("✅ Slash commands synced successfully!")
    except Exception as e:
        print(f"❌ Failed to sync slash commands: {e}")

@bot.event
async def on_guild_join(guild):
    """Event triggered when the bot joins a new server"""
    channel = bot.get_channel(1061417513579196516)
    embed = nextcord.Embed(
        title="Ryujin has been added to a new server! 👋",
        description=f"**{guild.name}** has added <@1060316037997936751> to their server!\n\n**Server Information:**\n• Members: {guild.member_count}\n• Created: <t:{int(guild.created_at.timestamp())}:R>",
        color=0x2a2a2a
    )
    embed.set_thumbnail(url=guild.icon.url if guild.icon else RYUJIN_LOGO)
    embed.set_author(
        name="Ryujin Bot",
        icon_url=RYUJIN_LOGO
    )
    embed.set_footer(
        text="© Ryujin Bot (2023-2025) | Bot Events",
        icon_url=RYUJIN_LOGO
    )
    await channel.send(embed=embed)

@bot.event
async def on_guild_remove(guild):
    """Event triggered when the bot leaves a server"""
    channel = bot.get_channel(1061417513579196516)
    embed = nextcord.Embed(
        title="Ryujin has been removed from a server! 😢",
        description=f"**{guild.name}** has removed <@1060316037997936751> from their server.\nWas Added: <t:{int(guild.me.joined_at.timestamp())}:R>",
        color=0xff0000
    )
    embed.set_thumbnail(url=guild.icon.url if guild.icon else RYUJIN_LOGO)
    embed.set_author(
        name="Ryujin Bot",
        icon_url=RYUJIN_LOGO
    )
    embed.set_footer(
        text="© Ryujin Bot (2023-2025) | Bot Events",
        icon_url=RYUJIN_LOGO 
    )
    await channel.send(embed=embed)

@bot.event
async def on_message(message):
    try:
        if message.author == bot.user:
            return

        server_id = str(message.guild.id)
        
        cursor = connection.cursor()
        
        system_channels = []
        SYSTEM_CONFIG = {
            "Remove Background": {
                "table": "removebg"
            },
            "Anime Search": {
                "table": "animesearch" 
            },
            "TikTok Downloader": {
                "table": "tiktokdl"
            },
            "YouTube Video Downloader": {
                "table": "youtubedl"
            },
            "YouTube Audio Downloader": {
                "table": "youtubedlaudio"
            },
            "Instagram Downloader": {
                "table": "instagramdl"
            },
            "Song Search": {
                "table": "songsearch"
            },
            "Font Search": {
                "table": "fontsearch"
            }
        }

        channel_configs = {}
        for system in SYSTEM_CONFIG:
            table = SYSTEM_CONFIG[system]["table"]
            cursor.execute(f"SELECT channel_id FROM {table} WHERE server_id = %s", (str(message.guild.id),))
            result = cursor.fetchone()
            if result:
                channel_configs[table] = int(result[0])
                system_channels.append(int(result[0]))

        cursor.close()

        is_just_chat = (
            not message.attachments and 
            not any(url in message.content.lower() for url in [
                "https://www.youtube.com/",
                "https://youtu.be/", 
                "https://youtube.com/shorts/",
                "https://www.tiktok.com/",
                "https://vm.tiktok.com/",
                "https://vt.tiktok.com/",
                "https://www.instagram.com/",
                "https://instagram.com/"
            ])
        )

        if "removebg" in channel_configs and message.channel.id == channel_configs["removebg"]:
            if not message.attachments:
                await message.delete()
                warning = await message.channel.send("**❌ This channel is only for removing backgrounds from images. Please attach an image!**")
                await asyncio.sleep(5)
                await warning.delete()
                return

        if is_just_chat and message.channel.id in [
            channel_configs.get("youtubedl"),
            channel_configs.get("youtubedlaudio"), 
            channel_configs.get("tiktokdl"),
            channel_configs.get("instagramdl")
        ]:
            await message.delete()
            warning = await message.channel.send("**❌ This channel is only for downloading content. Please do not chat here!**")
            await asyncio.sleep(5)
            await warning.delete()
            return

        if "youtubedl" in channel_configs and message.channel.id == channel_configs["youtubedl"]:
            if message.content.startswith("https://www.youtube.com/") or message.content.startswith("https://youtu.be/") or message.content.startswith("https://youtube.com/shorts/"):
                video_url = message.content

                start_time = time.time()
                logging.info(f"{message.author} sent '{message.content}' in '{message.guild}'")
                logging.info(f"The bot is downloading the video from {video_url}")

                download_path_video = await download_youtube_video(video_url, server_id, channel_configs["youtubedl"], message)
                if download_path_video:
                    end_time = time.time()
                    duration = end_time - start_time
                    logging.info(f"The bot has downloaded the video in {duration:.2f} seconds. Sending response to {message.author} in '{message.guild}'.")
                    await message.channel.send(f"**Your video has been downloaded in `{duration:.2f}` seconds. 🧐**", file=nextcord.File(download_path_video))
                else:
                    logging.error("Failed to download video.")

        if "youtubedlaudio" in channel_configs and message.channel.id == channel_configs["youtubedlaudio"]:
            if message.content.startswith("https://www.youtube.com/") or message.content.startswith("https://youtu.be/"):
                audio_url = message.content
        
                start_time = time.time()
                logging.info(f"{message.author} sent '{message.content}' in '{message.guild}'")
                logging.info(f"The bot is downloading the audio from {audio_url}")
        
                download_path_audio = await download_youtube_audio(audio_url, server_id, channel_configs["youtubedlaudio"], message)
                if download_path_audio:
                    end_time = time.time()
                    duration = end_time - start_time
                    logging.info(f"The bot has downloaded the audio in {duration:.2f} seconds. Sending response to {message.author} in '{message.guild}'.")
                    await message.channel.send(f"**Your audio has been downloaded in `{duration:.2f}` seconds. 🎵**", file=nextcord.File(download_path_audio))
                else:
                    logging.error("Failed to download audio.")

        if "tiktokdl" in channel_configs and message.channel.id == channel_configs["tiktokdl"]:
            if message.content.startswith("https://www.tiktok.com/") or message.content.startswith("https://vm.tiktok.com/") or message.content.startswith("https://vt.tiktok.com/"):
                tiktok_url = message.content

                start_time = time.time()
                logging.info(f"{message.author} sent '{message.content}' in '{message.guild}'")
                logging.info(f"The bot is downloading the TikTok video from {tiktok_url}")

                download_paths = await download_tiktok_video(tiktok_url, server_id, channel_configs["tiktokdl"], message)
                if download_paths:
                    end_time = time.time()
                    duration = end_time - start_time
                    logging.info(f"The bot has downloaded the TikTok video in {duration:.2f} seconds. Sending response to {message.author} in '{message.guild}'.")

                    files = [nextcord.File(path) for path in download_paths]
                    await message.channel.send(f"**Your TikTok video has been downloaded in `{duration:.2f}` seconds.**", files=files)
                else:
                    logging.error("Failed to download TikTok video.")

        if "instagramdl" in channel_configs and message.channel.id == channel_configs["instagramdl"]:
            if message.content.startswith("https://www.instagram.com/") or message.content.startswith("https://instagram.com/"):
                instagram_url = message.content

                start_time = time.time()
                logging.info(f"{message.author} sent '{message.content}' in '{message.guild}'")
                logging.info(f"The bot is downloading the Instagram content from {instagram_url}")

                download_paths = await download_instagram_content(instagram_url, server_id, channel_configs["instagramdl"], message)
                if download_paths:
                    end_time = time.time()
                    duration = end_time - start_time
                    logging.info(f"The bot has downloaded the Instagram content in {duration:.2f} seconds. Sending response to {message.author} in '{message.guild}'.")

                    files = [nextcord.File(path) for path in download_paths]
                    await message.channel.send(f"**Your Instagram content has been downloaded in `{duration:.2f}` seconds.**", files=files)
                else:
                    logging.error("Failed to download Instagram content.")

        if "removebg" in channel_configs and message.channel.id == channel_configs["removebg"]:
            user_id = message.author.id
            if user_id in blacklist:
                embed = nextcord.Embed(
                    title="You are blacklisted!",
                    description=f"**You can't use Ryujin's functions anymore because you have been blacklisted for `{blacklist[user_id]}`.**",
                    color=nextcord.Color.red()
                )
                embed.set_footer(text="© Ryujin Bot (2023-2025) | Info System (0.6b)")
                embed.set_author(
                    name="Ryujin",
                    icon_url="https://images-ext-2.discordapp.net/external/LEy12yVHJziqiqnjHzdlmAGVx-rL7xsKzu3A57CfV3M/%3Fsize%3D1024/https/cdn.discordapp.com/avatars/1059400568805785620/63a77f852ea29f37961f458c53fb5a97.png?width=676&height=676"
                )
                blacklist_msg = await message.channel.send(embed=embed)
                await asyncio.sleep(10)
                await blacklist_msg.delete()
                logging.warning(f"{message.author} is blacklisted. Unable to process Remove Background request.")
                return

            if message.attachments:
                image_url = message.attachments[0].url
                processing_msg = await message.channel.send("**🔄 Processing your image...**")

                try:
                    async with aiohttp.ClientSession() as session:
                        async with session.get(image_url) as response:
                            if response.status == 200:
                                image_data = await response.read()
                                
                                files = {'image': ('image.png', image_data)}
                                logging.info(f"Sending image to remove-bg API for {message.author}")
                                print(f"[DEBUG] Sending request to remove-bg API for user {message.author} ({message.author.id})")
                                print(f"[DEBUG] Image size: {len(image_data)} bytes")
                                
                                async with session.post('http://191.96.94.248:5080/remove-bg', files=files) as api_response:
                                    print(f"[DEBUG] API Response Status: {api_response.status}")
                                    if api_response.status == 200:
                                        result_image = await api_response.read()
                                        print(f"[DEBUG] Received processed image: {len(result_image)} bytes")
                                        logging.info(f"Successfully received processed image from API for {message.author}")
                                        
                                        await processing_msg.delete()
                                        await message.channel.send(
                                            "**✅ Background removed successfully!**",
                                            file=nextcord.File(BytesIO(result_image), "removebg.png")
                                        )
                                        logging.info(f"Remove Background request processed successfully. Image sent to {message.author} in '{message.guild}'.")
                                        print(f"[DEBUG] Successfully sent processed image to user {message.author}")
                                    else:
                                        try:
                                            error_data = await api_response.json()
                                            error_message = error_data.get('error', 'Unknown error occurred')
                                            print(f"[DEBUG] API Error Response: {error_data}")
                                        except:
                                            error_message = f"API returned status code {api_response.status}"
                                            print(f"[DEBUG] Failed to parse API error response")
                                        logging.error(f"API error: {error_message}")
                                        print(f"[DEBUG] API Error for user {message.author}: {error_message}")
                                        raise Exception(f"API error: {error_message}")

                except Exception as e:
                    logging.error(f"Error removing background: {e}")
                    await processing_msg.delete()
                    error_msg = await message.channel.send("**❌ Failed to remove background. The image might be too complex or in an unsupported format. Please try with a different image.**")
                    await asyncio.sleep(10)
                    await error_msg.delete()
                    await message.delete()
            else:
                no_image_msg = await message.channel.send("**❌ Please attach an image to remove its background.**")
                await asyncio.sleep(10)
                await no_image_msg.delete()
                await message.delete()

            await bot.process_commands(message)
        
        if "animesearch" in channel_configs and message.channel.id == channel_configs["animesearch"]:
            if message.attachments:
                attachment = message.attachments[0]
                if any(attachment.filename.lower().endswith(ext) for ext in ['.png', '.jpg', '.jpeg', '.gif', '.webp']):
                    try:
                        encoded_url = urllib.parse.quote_plus(attachment.url)
                        async with aiohttp.ClientSession() as session:
                            async with session.get(f"https://api.trace.moe/search?anilistInfo&url={encoded_url}") as response:
                                if response.status == 200:
                                    result = await response.json()
                                    
                                    if result['result'] and len(result['result']) > 0:
                                        best_match = result['result'][0]
                                        anilist_info = best_match['anilist']
                                        
                                        embed = nextcord.Embed(
                                            title="✨ Anime Found!",
                                            description="Here's what I found about your image:",
                                            color=0x2a2a2a
                                        )
                                        
                                        titles = (
                                            f"English: {anilist_info['title']['english']}\n"
                                            f"Romaji: {anilist_info['title']['romaji']}\n"
                                            f"Native: {anilist_info['title']['native']}"
                                        )
                                        embed.add_field(
                                            name="📺 Anime Title",
                                            value=f"```{titles}```",
                                            inline=False
                                        )
                                        
                                        episode = best_match.get('episode', 'Unknown')
                                        embed.add_field(
                                            name="🎬 Episode",
                                            value=f"```{episode}```",
                                            inline=True
                                        )
                                        
                                        similarity = best_match['similarity'] * 100
                                        embed.add_field(
                                            name="🎯 Match Accuracy",
                                            value=f"```{similarity:.2f}%```",
                                            inline=True
                                        )
                                        
                                        if 'from' in best_match and 'to' in best_match:
                                            from_seconds = best_match['from']
                                            to_seconds = best_match['to']
                                            
                                            from_m = int(from_seconds // 60)
                                            from_s = int(from_seconds % 60)
                                            
                                            to_m = int(to_seconds // 60)
                                            to_s = int(to_seconds % 60)
                                            
                                            timestamp = f"{from_m:02d}:{from_s:02d} - {to_m:02d}:{to_s:02d}"
                                            embed.add_field(
                                                name="⏱️ Timestamp", 
                                                value=f"```{timestamp}```",
                                                inline=True
                                            )
                                        
                                        embed.add_field(
                                            name="📝 Important Note",
                                            value=f"```Please note that this anime identification system may not always be 100% accurate. Results are based on image matching algorithms and may occasionally provide incorrect matches. The image shown below is your uploaded image for reference. For best results, try to use clear, high-quality screenshots directly from the anime.```",
                                            inline=False
                                        )

                                        embed.set_image(url=attachment.url)
                                        
                                        embed.set_footer(
                                            text="© Ryujin Bot (2023-2025) | Anime Search (Powered by trace.moe & AniList)",
                                            icon_url=RYUJIN_LOGO
                                        )
                                        
                                        embed.set_author(
                                            name="Ryujin",
                                            icon_url=RYUJIN_LOGO
                                        )

                                        await message.reply(embed=embed)
                                    else:
                                        error_embed = nextcord.Embed(
                                            title="❌ No Match Found",
                                            description="Sorry, I couldn't find any matching anime for this image.",
                                            color=0xed4245
                                        )
                                        await message.channel.send(embed=error_embed)
                                else:
                                    raise Exception(f"API returned status {response.status}")
                            
                    except Exception as e:
                        error_embed = nextcord.Embed(
                            title="❌ Error",
                            description="Sorry, there was an error processing your request. Please try again later.",
                            color=0xff0000
                        )

                        embed.set_footer(
                            text="© Ryujin Bot (2023-2025) | Anime Search System (Powered by trace.moe & AniList)",
                            icon_url=RYUJIN_LOGO
                        )
                        print(f"Error in anime search: {e}")
                        await message.channel.send(embed=error_embed)

    except Exception as e:
        logging.exception(f"An error occurred: {e}")
        print(f"An error occurred: {e}")

    if "songsearch" in channel_configs and message.channel.id == channel_configs["songsearch"]:
        try:
            url = None
            if message.content.startswith(("https://www.youtube.com/", "https://youtu.be/", "https://youtube.com/shorts/")):
                ydl_opts = {
                    'format': 'bestaudio/best',
                    'outtmpl': 'temp/%(title)s.%(ext)s',
                    'postprocessors': [{
                        'key': 'FFmpegExtractAudio',
                        'preferredcodec': 'mp3',
                        'preferredquality': '192',
                    }],
                }
                url = message.content
                with yt_dlp.YoutubeDL(ydl_opts) as ydl:
                    info = ydl.extract_info(url, download=True)
                    file_path = ydl.prepare_filename(info).replace(".webm", ".mp3").replace(".m4a", ".mp3")

            elif message.content.startswith(("https://www.tiktok.com/", "https://vm.tiktok.com/", "https://vt.tiktok.com/")):
                video_objects = snaptik(message.content)
                if video_objects:
                    unique_id = str(uuid.uuid4())[:8]
                    file_path = f"temp/tiktok_{unique_id}.mp3"
                    
                    temp_video = f"temp/tiktok_{unique_id}.mp4"
                    video_objects[0].download(temp_video)
                    
                    subprocess.run(['ffmpeg', '-i', temp_video, '-q:a', '0', '-map', 'a', file_path])
                    os.remove(temp_video)
                else:
                    await message.channel.send("**❌ Could not download TikTok audio!**")
                    return

            elif message.attachments:
                audio_attachment = None
                for attachment in message.attachments:
                    if attachment.filename.lower().endswith(('.mp3', '.wav', '.m4a', '.ogg', '.mp4', '.webm')):
                        audio_attachment = attachment
                        break
                
                if not audio_attachment:
                    await message.delete()
                    warning = await message.channel.send("**❌ This channel is only for identifying songs. Please upload an audio file or share a video link!**")
                    await asyncio.sleep(5)
                    await warning.delete()
                    return

                file_path = f"temp/{audio_attachment.filename}"
                await audio_attachment.save(file_path)
            
            else:
                await message.delete()
                warning = await message.channel.send("**❌ Please upload an audio file or share a supported video link (YouTube or TikTok)!**")
                await asyncio.sleep(5)
                await warning.delete()
                return

            try:
                shazam = Shazam()
                result = await shazam.recognize(file_path)

                if not result or 'track' not in result:
                    error_embed = nextcord.Embed(
                        title="❌ No Match Found",
                        description="Sorry, I couldn't identify any song from this file.",
                        color=0xed4245
                    )
                    error_embed.set_footer(
                        text="© Ryujin Bot (2023-2025) | Song Finder System",
                        icon_url=RYUJIN_LOGO
                    )
                    error_embed.set_author(
                        name="Ryujin",
                        icon_url=RYUJIN_LOGO
                    )
                    await message.channel.send(embed=error_embed)
                    return

                track = result['track']
                
                embed = nextcord.Embed(
                    title="🎵 Song Found!",
                    description=f"Here's what I found about this video/audio/link:",
                    color=0x2a2a2a
                )

                embed.add_field(
                    name="Title",
                    value=f"```{track.get('title', 'Unknown')}```",
                    inline=True
                )
                embed.add_field(
                    name="Artist", 
                    value=f"```{track.get('subtitle', 'Unknown Artist')}```",
                    inline=True
                )

                if 'genres' in track:
                    embed.add_field(
                        name="Genre",
                        value=f"```{track['genres'].get('primary', 'Unknown')}```",
                        inline=True
                    )

                links = []
                if 'share' in track:
                    if 'spotify' in track['share']:
                        links.append(f"```[Spotify]({track['share']['spotify']})```")
                    if 'apple_music' in track['share']:
                        links.append(f"```[Apple Music]({track['share']['apple_music']})```")
                    if 'youtube' in track['share']:
                        links.append(f"```[YouTube]({track['share']['youtube']})```")

                if links:
                    embed.add_field(
                        name="Listen On",
                        value=" • ".join(links),
                        inline=False
                    )

                if 'images' in track and 'coverart' in track['images']:
                    embed.set_image(url=track['images']['coverart'])

                embed.add_field(
                    name="📝 Note",
                    value="```Please note that this song identification system may not always be 100% accurate. Results are based on audio matching algorithms and may occasionally provide incorrect matches.```",
                    inline=False
                )
                
                embed.set_footer(
                    text="© Ryujin Bot (2023-2025) | Song Finder System",
                    icon_url=RYUJIN_LOGO
                )
                embed.set_author(
                    name="Ryujin",
                    icon_url=RYUJIN_LOGO
                )

                await message.channel.send(embed=embed)

            finally:
                if os.path.exists(file_path):
                    os.remove(file_path)

        except Exception as e:
            error_embed = nextcord.Embed(
                title="❌ Error",
                description=f"An error occurred while processing your request: {str(e)}",
                color=0xff0000
            )
            embed.set_footer(
                text="© Ryujin Bot (2023-2025) | Song Finder System",
                icon_url=RYUJIN_LOGO
            )
            embed.set_author(
                name="Ryujin",
                icon_url=RYUJIN_LOGO
            )
            await message.channel.send(embed=error_embed)

    if "fontsearch" in channel_configs and message.channel.id == channel_configs["fontsearch"]:
        try:
            if not message.attachments:
                await message.delete()
                warning = await message.channel.send("**❌ This channel is only for identifying fonts. Please upload an image!**")
                await asyncio.sleep(5)
                await warning.delete()
                return

            attachment = message.attachments[0]
            
            if not attachment.filename.lower().endswith(('.png', '.jpg', '.jpeg')):
                await message.delete()
                warning = await message.channel.send("**❌ Please upload a valid image file (PNG, JPG, JPEG)!**")
                await asyncio.sleep(5)
                await warning.delete()
                return

            image_data = await attachment.read()
            
            url = "https://api.whatfontis.com/v2/fonts"
            headers = {
                "Authorization": "Bearer YOUR_API_KEY"
            }
            files = {
                "file": ("image.jpg", image_data, "image/jpeg")
            }

            async with aiohttp.ClientSession() as session:
                async with session.post(url, headers=headers, data=files) as response:
                    if response.status == 200:
                        data = await response.json()
                        
                        embed = nextcord.Embed(
                            title="🔍 Font Search Results",
                            description="Here are the closest matching fonts I found:",
                            color=0x2b2d31
                        )

                        for i, font in enumerate(data['fonts'][:5], 1):
                            embed.add_field(
                                name=f"Match #{i}: {font['name']}",
                                value=f"Family: {font['family']}\nFoundry: {font['foundry']}\nLicense: {font['license']}",
                                inline=False
                            )

                        embed.add_field(
                            name="📝 Note",
                            value="```Please note that font identification may not always be 100% accurate. Results are based on image matching algorithms and may occasionally provide incorrect matches.```",
                            inline=False
                        )

                        embed.set_image(url=attachment.url)
                        
                        embed.set_footer(
                            text="© Ryujin Bot (2023-2025) | Font Search System",
                            icon_url=RYUJIN_LOGO
                        )

                        embed.set_author(
                            name="Ryujin",
                            icon_url=RYUJIN_LOGO
                        )

                        await message.reply(embed=embed)
                    else:
                        raise Exception(f"API returned status {response.status}")

        except Exception as e:
            error_embed = nextcord.Embed(
                title="❌ Error",
                description="Sorry, there was an error processing your request. Please try again later.",
                color=0xff0000
            )
            error_embed.set_footer(
                text="© Ryujin Bot (2023-2025) | Font Search System",
                icon_url=RYUJIN_LOGO
            )
            await message.channel.send(embed=error_embed)
        
async def download_tiktok_video(tiktok_url, server_id, configured_channel_id, message):
    try:
        if message.channel.id != configured_channel_id:
            return None

        video_objects = snaptik(tiktok_url)
        
        if video_objects:
            unique_id = str(uuid.uuid4())[:8]
            
            tiktok_directory = os.path.join("temp")
            if not os.path.exists(tiktok_directory):
                os.makedirs(tiktok_directory)
            
            concatenated_video_path = os.path.join(tiktok_directory, f'video_{unique_id}.mp4')
            
            with open(concatenated_video_path, 'wb') as output_file:
                for i, video_object in enumerate(video_objects):
                    video_part_path = os.path.join(tiktok_directory, f'video_{unique_id}_{i}.mp4')
                    video_object.download(video_part_path)
                    with open(video_part_path, 'rb') as input_file:
                        output_file.write(input_file.read())
                    os.remove(video_part_path)
            
            ydl_opts = {
                'format': 'bestaudio/best',
                'outtmpl': f'{tiktok_directory}/audio_{unique_id}.%(ext)s',
                'postprocessors': [{
                    'key': 'FFmpegExtractAudio',
                    'preferredcodec': 'mp3',
                    'preferredquality': '192',
                }],
                'quiet': True,
                'no_warnings': True
            }

            with yt_dlp.YoutubeDL(ydl_opts) as ydl:
                info = ydl.extract_info(tiktok_url, download=True)
                audio_path = ydl.prepare_filename(info).rsplit(".", 1)[0] + ".mp3"
            
            files = []
            if os.path.exists(concatenated_video_path):
                files.append(concatenated_video_path)
            if os.path.exists(audio_path):
                files.append(audio_path)
                
            return files
        else:
            logging.error("Failed to get video object from snaptik.")
            return None
    except Exception as e:
        logging.error(f"Error: {e}")
        return None

async def download_instagram_content(instagram_url, server_id, configured_channel_id, message):
    try:
        if message.channel.id != configured_channel_id:
            return None

        L = instaloader.Instaloader(
            dirname_pattern="temp/instagramdl",
            filename_pattern="{shortcode}",
            download_video_thumbnails=False,
            download_geotags=False,
            download_comments=False,
            save_metadata=False
        )
        
        shortcode = instagram_url.split("/")[-2]
        
        post = instaloader.Post.from_shortcode(L.context, shortcode)
            
        temp_dir = "temp/instagramdl"
        if not os.path.exists(temp_dir):
            os.makedirs(temp_dir)
        
        downloaded_files = []

        if post.typename == "GraphSidecar":
            for i, node in enumerate(post.get_sidecar_nodes()):
                if node.is_video:
                    video_path = os.path.join(temp_dir, f"{shortcode}_{i}.mp4")
                    video_response = requests.get(node.video_url)
                    if video_response.status_code == 200:
                        with open(video_path, 'wb') as f:
                            f.write(video_response.content)
                        downloaded_files.append(video_path)
                else:
                    image_path = os.path.join(temp_dir, f"{shortcode}_{i}.jpg")
                    response = requests.get(node.display_url)
                    if response.status_code == 200:
                        with open(image_path, 'wb') as f:
                            f.write(response.content)
                        downloaded_files.append(image_path)
        else:
            if post.is_video:
                video_path = os.path.join(temp_dir, f"{shortcode}.mp4")
                video_response = requests.get(post.video_url)
                if video_response.status_code == 200:
                    with open(video_path, 'wb') as f:
                        f.write(video_response.content)
                    downloaded_files.append(video_path)
            else:
                image_path = os.path.join(temp_dir, f"{shortcode}.jpg")
                response = requests.get(post.url)
                if response.status_code == 200:
                    with open(image_path, 'wb') as f:
                        f.write(response.content)
                    downloaded_files.append(image_path)

        for file in os.listdir(temp_dir):
            file_path = os.path.join(temp_dir, file)
            if file_path not in downloaded_files:
                try:
                    os.remove(file_path)
                except:
                    pass

        return downloaded_files 
        
    except Exception as e:
        logging.error(f"Error downloading Instagram content: {e}")
        await message.channel.send(f"**Error downloading Instagram content: {str(e)}**")
        return None

async def download_youtube_video(url, server_id, configured_channel_id, message, is_nitro_user=False):
    try:
        if message.channel.id != int(configured_channel_id):
            return None

        start_time = time.time()
        logging.info(f"The bot is downloading video from {url}")

        server_boost_count = message.guild.premium_subscription_count

        if server_boost_count >= 7:
            discord_size_limit = 50 * 1024 * 1024
            ydl_opts = {
                'format': 'bestvideo[height<=1080][ext=webm]+bestaudio[ext=webm]/best[ext=webm]/best',
                'merge_output_format': 'webm',
                'postprocessor_args': [
                    '-c:v', 'copy',
                    '-c:a', 'copy'
                ],
                'outtmpl': 'temp/1080p_%(title)s.webm'
            }
        else:
            discord_size_limit = 8 * 1024 * 1024
            ydl_opts = {
                'format': 'bestvideo[height<=720][ext=webm]+bestaudio[ext=webm]/best[ext=webm]/best',
                'merge_output_format': 'webm',
                'postprocessor_args': [
                    '-c:v', 'copy',
                    '-c:a', 'copy'
                ],
                'outtmpl': 'temp/720p_%(title)s.webm'
            }

        with yt_dlp.YoutubeDL(ydl_opts) as ydl:
            info_dict = ydl.extract_info(url, download=False)
            if info_dict.get('duration') > 1800:
                logging.warning("Video duration exceeds 30 minutes. Skipping download.")
                print("Video duration exceeds 30 minutes. Skipping download.")
                return None
                
            result = ydl.download([url])
            video_file = ydl.prepare_filename(info_dict)

        end_time = time.time()
        duration = end_time - start_time

        logging.info(f"The bot has downloaded the video in {duration:.2f} seconds. Path: {video_file}")
        print(f"Video downloaded in {duration:.2f} seconds.")

        if os.path.getsize(video_file) > discord_size_limit:
            error_message = f"**Sorry, the video you are trying to download is too large (>{discord_size_limit / (1024 * 1024)} MB) and I can't send it... 🥺**"
            logging.error(error_message)
            await message.channel.send(error_message)
            return None

        await message.channel.send(file=discord.File(video_file))

        os.remove(video_file)
        logging.info(f"Deleted file: {video_file}")

        return video_file

    except Exception as e:
        error_message = f"**Sorry, I can't download the video that you just sent... 🥺 (Error: `{e}`)**"
        logging.error(error_message)
        await message.channel.send(error_message)
        return None

async def download_youtube_audio(url, server_id, configured_channel_id, message):
    try:
        if message.channel.id != configured_channel_id:
            return None

        start_time = time.time()
        logging.info(f"The bot is downloading audio from {url}")

        ydl_opts = {
            'format': 'bestaudio/best',
            'outtmpl': 'temp/%(title)s.%(ext)s',
            'postprocessors': [{
                'key': 'FFmpegExtractAudio',
                'preferredcodec': 'mp3',
                'preferredquality': '192',
            }],
        }

        os.makedirs('temp', exist_ok=True)

        with yt_dlp.YoutubeDL(ydl_opts) as ydl:
            info_dict = ydl.extract_info(url, download=True)
            download_path_audio_mp3 = ydl.prepare_filename(info_dict).replace(".webm", ".mp3").replace(".m4a", ".mp3")

        end_time = time.time()
        duration = end_time - start_time

        if not os.path.exists(download_path_audio_mp3):
            logging.error(f"Expected file {download_path_audio_mp3} does not exist.")
            raise FileNotFoundError(f"Expected file {download_path_audio_mp3} does not exist.")

        logging.info(f"The bot has downloaded the audio in {duration:.2f} seconds. Path: {download_path_audio_mp3}")
        print(f"Audio downloaded in {duration:.2f} seconds.")

        with open(download_path_audio_mp3, 'rb') as audio_file:
            await message.channel.send(file=File(audio_file, filename=os.path.basename(download_path_audio_mp3)))

        os.remove(download_path_audio_mp3)

        return download_path_audio_mp3

    except Exception as e:
        error_message = f"**Sorry, I can't download the audio from the video that you just sent... 🥺 (Error: `{e}`)**"
        logging.error(error_message)
        print(error_message)
        await message.channel.send(error_message)
        return None

async def change_status():
    """Rotate bot status"""
    while True:
        dev_status_1 = nextcord.Activity(name="🛠️ Beta Mode: Testing new features!", type=nextcord.ActivityType.playing)
        dev_status_2 = nextcord.Activity(name="🐞 Reporting bugs? DM @moongetsu1", type=nextcord.ActivityType.watching)
        dev_status_3 = nextcord.Activity(name="🔄 Restarting often? That's normal in dev!", type=nextcord.ActivityType.listening)
        dev_status_4 = nextcord.Activity(name="💡 Suggest features in #🧠〢suggestions", type=nextcord.ActivityType.watching)
        dev_status_5 = nextcord.Activity(name="⚙️ Version: DEV-BETA", type=nextcord.ActivityType.playing)
        statuses = [dev_status_1, dev_status_2, dev_status_3, dev_status_4, dev_status_5]
        for status in statuses:
            await bot.change_presence(status=nextcord.Status.dnd, activity=status)
            await asyncio.sleep(10)

async def update_info_message():
    """Update the info message in the designated channel"""
    message_config = load_messages_config()

    while True:
        try:
            info_channel = bot.get_channel(int(message_config["Info"]["channel_id"]))
            if not info_channel:
                print(f"❌ Info channel not found: {message_config['Info']['channel_id']}")
                await asyncio.sleep(60)
                continue
                
            info_embed = create_info_embed(bot)
            
            if not message_config["Info"]["message_id"]:
                message = await info_channel.send(embed=info_embed)
                message_config["Info"]["message_id"] = str(message.id)
                save_messages_config(message_config)
            else:
                try:
                    message = await info_channel.fetch_message(int(message_config["Info"]["message_id"]))
                    await message.edit(embed=info_embed)
                except (nextcord.NotFound, nextcord.HTTPException):
                    message = await info_channel.send(embed=info_embed)
                    message_config["Info"]["message_id"] = str(message.id)
                    save_messages_config(message_config)
            
            await asyncio.sleep(60)
        except Exception as e:
            print(f"Error in info message update loop: {e}")
            await asyncio.sleep(60)

async def update_servers_message():
    """Update the servers message in the designated channel"""
    message_config = load_messages_config()
        
    while True:
        try:
            servers_channel = bot.get_channel(int(message_config["Servers"]["channel_id"]))
            if not servers_channel:
                print(f"❌ Servers channel not found: {message_config['Servers']['channel_id']}")
                await asyncio.sleep(300)
                continue
            
            sorted_guilds = sorted(bot.guilds, key=lambda g: g.member_count, reverse=True)
            
            pages = []
            for i in range(0, len(sorted_guilds), 50):
                page_guilds = sorted_guilds[i:i+50]
                embed = create_servers_embed(page_guilds, i//50, -(-len(sorted_guilds)//50))
                pages.append(embed)

            if not message_config["Servers"]["message_id"]:
                message = await servers_channel.send(embed=pages[0])
                message_config["Servers"]["message_id"] = str(message.id)
                save_messages_config(message_config)
            else:
                try:
                    message = await servers_channel.fetch_message(int(message_config["Servers"]["message_id"]))
                    await message.edit(embed=pages[0])
                except (nextcord.NotFound, nextcord.HTTPException):
                    message = await servers_channel.send(embed=pages[0])
                    message_config["Servers"]["message_id"] = str(message.id)
                    save_messages_config(message_config)

            if len(pages) > 1:
                await handle_pagination(message, pages, bot)

            await asyncio.sleep(300)
        except Exception as e:
            print(f"Error in servers message update loop: {e}")
            await asyncio.sleep(60)

# Load cogs
async def load_cogs():
    """Load all cogs from the cogs directory"""
    print("🔍 Starting cog loading process...")
    
    for folder in os.listdir("cogs/commands"):
        if os.path.isdir(f"cogs/commands/{folder}"):
            print(f"\n📁 Processing folder: {folder}")
            for file in os.listdir(f"cogs/commands/{folder}"):
                if file.endswith(".py") and not file.startswith("__"):
                    try:
                        extension_name = f"cogs.commands.{folder}.{file[:-3]}"
                        print(f"  🔄 Attempting to load: {extension_name}")
                        bot.load_extension(extension_name)
                        print(f"  ✅ Successfully loaded: {extension_name}")
                    except Exception as e:
                        print(f"  ✗ Failed to load: {extension_name}")
                        print(f"    Error: {e}")
                        import traceback
                        traceback.print_exc()

bot.run(TOKEN)