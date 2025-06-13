import nextcord
from nextcord.ext import commands
import random
import datetime
import uuid
from tiktok_downloader import snaptik
from datetime import datetime, timedelta
import mysql.connector
from mysql.connector import Error
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
import discord
from pytube import YouTube
from pytube.innertube import _default_clients
from nextcord import SlashOption
import nightcore as nc
import yt_dlp
from discord import File
import glob
import instaloader
import urllib.parse
import shazamio
from shazamio import Shazam
import subprocess
from googleapiclient.discovery import build
import imageio
import numpy as np
import traceback

_default_clients["ANDROID_MUSIC"] = _default_clients["ANDROID_CREATOR"]
log_file_name = f"logs/bot_logs_{datetime.now().strftime('%Y-%m-%d_%H-%M-%S')}.log"
logging.basicConfig(filename=log_file_name, level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')

RYUJIN_LOGO = "https://cdn.discordapp.com/avatars/1059400568805785620/63a77f852ea29f37961f458c53fb5a97.png"
def create_db_connection():
    try:
        connection = mysql.connector.connect(
            host='censored',
            user='censored', 
            password='censored',
            database='censored'
        )
        return connection if connection.is_connected() else None
    except Error as e:
        print(f"Error: {e}")
        return None

def create_table(connection, table_name, schema):
    try:
        cursor = connection.cursor()
        cursor.execute(schema)
        connection.commit()
        cursor.close()
    except Error as e:
        print(f"Error: {e}")

TABLE_SCHEMAS = {
    'blacklist': """
        CREATE TABLE IF NOT EXISTS blacklist (
            user_id BIGINT PRIMARY KEY,
            reason VARCHAR(255)
        )
    """,
    'removebg': """
        CREATE TABLE IF NOT EXISTS removebg (
            server_id VARCHAR(255) PRIMARY KEY,
            channel_id VARCHAR(255)
        )
    """,
    'tiktokdl': """
        CREATE TABLE IF NOT EXISTS tiktokdl (
            server_id VARCHAR(255) PRIMARY KEY,
            channel_id VARCHAR(255)
        )
    """,
    'youtubedl': """
        CREATE TABLE IF NOT EXISTS youtubedl (
            server_id VARCHAR(255) PRIMARY KEY,
            channel_id VARCHAR(255)
        )
    """,
    'youtubedlaudio': """
        CREATE TABLE IF NOT EXISTS youtubedlaudio (
            server_id VARCHAR(255) PRIMARY KEY,
            channel_id VARCHAR(255)
        )
    """,
    'user_favorites': """
        CREATE TABLE IF NOT EXISTS user_favorites (
            id INT AUTO_INCREMENT PRIMARY KEY,
            user_id VARCHAR(255),
            amv_id VARCHAR(255),
            source VARCHAR(255)
        )
    """,
    'user_profiles': """
        CREATE TABLE IF NOT EXISTS user_profiles (
            user_id VARCHAR(255) PRIMARY KEY,
            username VARCHAR(255),
            avatar_url VARCHAR(255),
            editing_software VARCHAR(255),
            editing_style VARCHAR(255),
            amvs TEXT,
            youtube_link VARCHAR(255),
            tiktok_link VARCHAR(255),
            instagram_link VARCHAR(255)
        )
    """,
    'user_ratings': """
        CREATE TABLE IF NOT EXISTS user_ratings (
            user_id VARCHAR(255),
            rater_id VARCHAR(255),
            rating FLOAT,
            PRIMARY KEY (user_id, rater_id)
        )
    """,
    'instagramdl': """
        CREATE TABLE IF NOT EXISTS instagramdl (
            server_id VARCHAR(255) PRIMARY KEY,
            channel_id VARCHAR(255)
        )
    """,
    'animesearch': """
        CREATE TABLE IF NOT EXISTS animesearch (
            server_id VARCHAR(255) PRIMARY KEY,
            channel_id VARCHAR(255)
        )
    """,
    'disableads_servers': """
        CREATE TABLE IF NOT EXISTS disableads_servers (
            server_id VARCHAR(255) PRIMARY KEY
        )
    """,
    'removebgapi': """
        CREATE TABLE IF NOT EXISTS removebgapi (
            api_key VARCHAR(255) PRIMARY KEY
        )
    """,
    'songsearch': """
        CREATE TABLE IF NOT EXISTS songsearch (
            server_id VARCHAR(255) PRIMARY KEY,
            channel_id VARCHAR(255)
        )
    """,
    'fontsearch': """
        CREATE TABLE IF NOT EXISTS fontsearch (
            server_id VARCHAR(255) PRIMARY KEY,
            channel_id VARCHAR(255)
        )
    """
}

async def add_to_blacklist(connection, user_id, reason):
    try:
        cursor = connection.cursor()
        cursor.execute(
            "INSERT INTO blacklist (user_id, reason) VALUES (%s, %s) ON DUPLICATE KEY UPDATE reason = VALUES(reason)",
            (user_id, reason)
        )
        connection.commit()
        cursor.close()
    except Error as e:
        print(f"Error: {e}")

def get_blacklist(connection):
    try:
        cursor = connection.cursor()
        cursor.execute("SELECT user_id, reason FROM blacklist")
        blacklist = {int(row[0]): row[1] for row in cursor.fetchall()}
        cursor.close()
        return blacklist
    except Error as e:
        print(f"Error: {e}")
        return {}

connection = create_db_connection()
if connection:
    for table_name, schema in TABLE_SCHEMAS.items():
        create_table(connection, table_name, schema)
    blacklist = get_blacklist(connection)

with open('config/ryujin.json') as json_file:
    data = json.load(json_file)
    for p in data['settings']:
        TOKEN = p['token']
        STATS_CHANNEL = p['stats-channel']
        INFO_CHANNEL = p['info-channel']
        WELCOME_LEAVE_CHANNEL = p['welcome-leave-channel']

with open("config/presets.json", "r") as presets_file:
    presets_data = json.load(presets_file)
    
def load_project_data():
    with open("config/project_files.json", "r") as json_file:
        return json.load(json_file)

def load_script_data():
    with open("config/scripts.json", "r") as json_file:
        return json.load(json_file)

def load_extension_data():
    with open("config/extensions.json", "r") as json_file:
        return json.load(json_file)

def load_presets_data():
    with open("config/presets.json", "r") as presets_file:
        return json.load(presets_file)

def count_presets_in_categories():
    presets_data = load_presets_data()
    presetscategories = presets_data.get("presetscategories", {})
    category_counts = {}
    for category_name, folder_name in presetscategories.items():
        folder_path = os.path.join("resources/presets", folder_name)
        assets = [f for f in os.listdir(folder_path) if f.endswith(".ffx")]
        category_counts[category_name] = len(assets)
    
    return category_counts

config = configparser.ConfigParser()

config_path = os.path.join("config", "removebg-api.json")
with open(config_path, "r") as config_file:
    config = json.load(config_file)
    api_keys = config.get("api_keys", [])

project_files = load_project_data()
script_files = load_script_data()
extension_files = load_extension_data()
PREFIX = "+"

intents = nextcord.Intents.default()
intents.message_content = True
bot = commands.Bot(command_prefix="!", intents=intents)

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
        await maybe_send_ad(interaction)

class AnotherButton(nextcord.ui.View):
    def __init__(self):
        super().__init__()

    @nextcord.ui.button(label=f"Another One 👀", style=nextcord.ButtonStyle.gray)
    async def create_ronde(self, button: nextcord.ui.Button, interaction: nextcord.Interaction):
        global current_overlay
        assets = [f for f in os.listdir("resources/overlays") if f.endswith(".mp4")]
        new_overlay = random.choice(assets)
        while new_overlay == current_overlay:
            new_overlay = random.choice(assets)
        current_overlay = new_overlay
        file_path = os.path.join("resources/overlays", current_overlay)
        await interaction.response.edit_message(file=nextcord.File(file_path))        

def generate_hashtags(character, anime):
    base_tags = [
        "anime", "amv", "edit", "animeedit",
        f"{anime.replace(' ', '').lower()}",
        f"{anime.replace(' ', '').lower()}edit",
        f"{character.replace(' ', '').lower()}" if character else "",
        f"{character.replace(' ', '').lower()}shortamv" if character else "",
        f"{character.replace(' ', '').lower()}shortedit" if character else "",
        f"{character.replace(' ', '').lower()}shortedit" if character else "",
        f"{character.replace(' ', '').lower()}edit" if character else "",
        f"{character.replace(' ', '').lower()}amv" if character else "",
        f"{character.replace(' ', '').lower()}editamv" if character else "",
        f"{anime.replace(' ', '').lower()}shortedit"
        f"{anime.replace(' ', '').lower()}shortamv"
        f"{anime.replace(' ', '').lower()}editamv"
        f"{anime.replace(' ', '').lower()}shorteditamv"
        f"{anime.replace(' ', '').lower()}amv"
        f"{anime.replace(' ', '').lower()}edit"
    ]
    additional_tags = [
        "aftereffects", "4k", "fanedit", "animeart",
        "animemusicvideo", "manga", "otaku", "weeb",
        "animelover", "animeworld", "animefan", "animevideo",
        "cosplay", "animecosplay", "animelife", "animeforever",
        "animegirls", "animeboys", "japan", "kawaii",
        "aesthetic", "amvedit", "editanime", "animelove",
        "mangalove", "mangafan", "mangacollector", "animevibes",
        "animefreak", "animedaily", "animeislife", "animestyle",
        "animefans", "animefandom", "amvedit", "animeartwork",
        "amazinganime", "animeaddict", "animescenes", "animeclips",
        "animetiktok", "animeedits", "animeamv", "animecompilation",
        "animetags", "animeinspiration", "animeinspo", "animequotes",
        "animeparody", "animefunny", "animecomedy", "animedrama",
        "animelover", "animepassion", "animefanatic", "animechannel",
        "animemusic", "animecollector", "animeculture", "animefanart",
        "animecollection", "animeinstagram", "anime4life", "animelifestyle",
        "animefilms", "animecommunity", "animeillustration", "animeposter",
        "animeposterart", "animedrawing", "animepaintings", "animeartist",
        "animeedits", "animegraphics", "animegif", "animefanedit",
        "animegifedit", "animefanedit", "animegif", "amvedit", "amvcommunity", "amvartist", "amvedits", "amvediting", "amvworld", "amvfans", 
        "amvlife", "amv4life", "amvforever", "amvscene", "amvclip", "amvs", "amvlove", "amvanime", 
        "amvmaker", "amvcreations", "amveditor", "amvproduction", "amvstudio", "amvcreator", "amvteam", 
        "amvstyle", "amvanimation", "amvmusic", "amvproject", "amvclips", "amvvideo", "amvfan", 
        "amvchannel", "amvshots", "amvaddict", "amvpassion", "amvobsession", "amvguru", "amvstagram", 
        "amvinstagram", "amvtiktok", "amvtube", "amvcreation", "amvking", "amvqueen", "amvlegend"
    ]
    
    random_additional = random.sample(additional_tags, min(30, len(additional_tags)))
    all_tags = base_tags + random_additional
    return ["#" + tag for tag in all_tags if tag]

class GenerateHashtagsModal(nextcord.ui.Modal):
    def __init__(self, bot) -> None:
        super().__init__("Generate Hastags #️⃣")

        self.character_name = nextcord.ui.TextInput(
            label="Character Name",
            style=nextcord.TextInputStyle.paragraph,
            placeholder="E.G: Ichigo Kurosaki (or you can leave this empty). 🤔",
            required=False,
            max_length=1500,
        )
        self.add_item(self.character_name)

        self.anime_name = nextcord.ui.TextInput(
            label="Anime Name",
            style=nextcord.TextInputStyle.paragraph,
            placeholder="E.G: Bleach. 🤔",
            required=True,
            max_length=1500,
        )
        self.add_item(self.anime_name)

    async def callback(self, interaction: nextcord.Interaction): 
        character_name = self.character_name.value.strip()
        anime_name = self.anime_name.value.strip()

        hashtags = generate_hashtags(character_name, anime_name)

        embed = nextcord.Embed(
            title="Hashtags Generator",
            description="",
            color=0x2a2a2a
        )

        embed.add_field(name="Here are your Hashtags! 😉", value="```\n" + " ".join(hashtags) + "\n```", inline=False)
        embed.set_footer(
            text="© Ryujin Bot (2023-2025) | Hashtags Generator System",
            icon_url=RYUJIN_LOGO
        )

        await interaction.response.send_message(embed=embed, ephemeral=True)

async def change_status():
    while True:
        total_guilds = len(bot.guilds)
        total_members = sum(guild.member_count for guild in bot.guilds)
        guilds_status = f"in {total_guilds} servers 🌐"
        members_status = f"at {total_members} members 🚀"
        new_status = f"🆕 Instagram Downloader & Anime Search"
        activity_guilds = nextcord.Activity(name=guilds_status, type=nextcord.ActivityType.watching)
        activity_members = nextcord.Activity(name=members_status, type=nextcord.ActivityType.watching)
        new_command = nextcord.Activity(name=new_status, type=nextcord.ActivityType.playing)
        await bot.change_presence(status=nextcord.Status.online, activity=activity_guilds)
        await asyncio.sleep(10)
        await bot.change_presence(status=nextcord.Status.online, activity=activity_members)
        await asyncio.sleep(10)
        await bot.change_presence(status=nextcord.Status.online, activity=new_command)
        await asyncio.sleep(10)

def count_files(folder):
    count = 0
    for root, _, files in os.walk(folder):
        count += len(files)
    return count

def get_removebg_channels(connection):
    try:
        cursor = connection.cursor()
        cursor.execute("SELECT server_id, channel_id FROM removebg")
        channels = cursor.fetchall()
        cursor.close()
        return channels
    except Error as e:
        print(f"Error: {e}")
        return []

@bot.event
async def on_ready():
    bot.start_time = datetime.now()

    print("\n" + "═"*100)
    print(f"{'RYUJIN BOT STARTUP':^100}")
    print("═"*100 + "\n")

    startup_info = [
        ('🤖 Bot Information', [
            f'✓ Connected as {bot.user.name} (ID: {bot.user.id})',
            f'✓ Running Python {platform.python_version()}',
            f'✓ Nextcord {nextcord.__version__}',
            f'✓ Operating System: {platform.system()} {platform.release()} ({os.name})'
        ]),
        ('📊 Resource Statistics', [
            f'✓ Overlays: {len(os.listdir("resources/overlays"))}',
            f'✓ SFX Categories: {len(os.listdir("resources/sfx"))}', 
            f'✓ Edit Audio Categories: {len(os.listdir("resources/edit audios"))}',
            f'✓ Preset Categories: {len(presets_data.get("presetscategories", {}))}',
            f'✓ Total Edits: {len(open("edits.txt").read().strip().split("\n"))}'
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

    with open('config/messages.json', 'r') as f:
        message_config = json.load(f)

    async def update_info_message():
        while True:
            try:
                info_channel = bot.get_channel(int(message_config["Info"]["channel_id"]))
                info_embed = create_info_embed()
                
                if not message_config["Info"]["message_id"]:
                    message = await info_channel.send(embed=info_embed)
                    message_config["Info"]["message_id"] = str(message.id)
                    with open('config/messages.json', 'w') as f:
                        json.dump(message_config, f, indent=4)
                else:
                    try:
                        message = await info_channel.fetch_message(int(message_config["Info"]["message_id"]))
                        await message.edit(embed=info_embed)
                    except (nextcord.NotFound, nextcord.HTTPException):
                        message = await info_channel.send(embed=info_embed)
                        message_config["Info"]["message_id"] = str(message.id)
                        with open('config/messages.json', 'w') as f:
                            json.dump(message_config, f, indent=4)
                
                await asyncio.sleep(60)
            except Exception as e:
                print(f"Error in info message update loop: {e}")
                await asyncio.sleep(60)

    bot.loop.create_task(change_status())
    bot.loop.create_task(update_info_message())
    bot.loop.create_task(update_servers_message())

async def handle_pagination(message, pages):
    current_page = 0
    
    while True:
        try:
            await message.clear_reactions()
            await message.add_reaction("◀️")
            await message.add_reaction("▶️")

            def check(reaction, user):
                return not user.bot and str(reaction.emoji) in ["◀️", "▶️"] and reaction.message.id == message.id

            try:
                reaction, user = await bot.wait_for('reaction_add', timeout=300.0, check=check)
                
                if str(reaction.emoji) == "▶️" and current_page < len(pages) - 1:
                    current_page += 1
                    await message.edit(embed=pages[current_page])
                elif str(reaction.emoji) == "◀️" and current_page > 0:
                    current_page -= 1
                    await message.edit(embed=pages[current_page])

                await message.remove_reaction(reaction, user)
            except asyncio.TimeoutError:
                await message.clear_reactions()
                break

        except Exception as e:
            print(f"Error handling reactions: {e}")
            await asyncio.sleep(5)

async def update_servers_message():
    with open('config/messages.json', 'r') as f:
        message_config = json.load(f)
        
    while True:
        try:
            servers_channel = bot.get_channel(int(message_config["Servers"]["channel_id"]))
            
            sorted_guilds = sorted(bot.guilds, key=lambda g: g.member_count, reverse=True)
            
            pages = []
            for i in range(0, len(sorted_guilds), 50):
                page_guilds = sorted_guilds[i:i+50]
                embed = nextcord.Embed(title="Ryujin Servers", color=0x2a2a2a)
                
                description = ""
                for guild in page_guilds:
                    clean_name = (guild.name)
                    clean_name = clean_name.strip()
                    description += f"`{clean_name}` (**{guild.member_count:,}** Members)\n"
                
                embed.description = description
                embed.set_footer(
                    text=f"Page {i//50 + 1}/{-(-len(sorted_guilds)//50)} • Total Servers: {len(sorted_guilds):,}",
                    icon_url=RYUJIN_LOGO
                )
                embed.set_image(url="https://media.discordapp.net/attachments/977518313217347604/1060480442656116797/download.png")
                embed.set_author(
                    name="Ryujin",
                    icon_url=RYUJIN_LOGO
                )
                pages.append(embed)

            if not message_config["Servers"]["message_id"]:
                message = await servers_channel.send(embed=pages[0])
                message_config["Servers"]["message_id"] = str(message.id)
                with open('config/messages.json', 'w') as f:
                    json.dump(message_config, f, indent=4)
            else:
                try:
                    message = await servers_channel.fetch_message(int(message_config["Servers"]["message_id"]))
                    await message.edit(embed=pages[0])
                except (nextcord.NotFound, nextcord.HTTPException):
                    message = await servers_channel.send(embed=pages[0])
                    message_config["Servers"]["message_id"] = str(message.id)
                    with open('config/messages.json', 'w') as f:
                        json.dump(message_config, f, indent=4)

            if len(pages) > 1:
                await handle_pagination(message, pages)

            await asyncio.sleep(300)
        except Exception as e:
            print(f"Error in servers message update loop: {e}")
            await asyncio.sleep(60)

def create_info_embed():
    """Creates a consistent info embed for both the info command and channel"""
    info = nextcord.Embed(
        title="About Ryujin Bot",
        description="Your ultimate editing companion!",
        color=0x2a2a2a
    )

    guilds_count = len(bot.guilds)
    total_members = sum(g.member_count for g in bot.guilds)
    uptime = datetime.now() - bot.start_time if hasattr(bot, 'start_time') else None
    uptime_str = str(uptime).split('.')[0] if uptime else "N/A"

    info.add_field(
        name="📊 Stats",
        value=f"**Total Servers:** {guilds_count}\n**Total Users:** {total_members}\n**Uptime:** {uptime_str}",
        inline=False
    )

    info.add_field(
        name="🎯 Features",
        value="• YouTube Downloader\n• TikTok Downloader\n• Instagram Downloader\n• Anime Search\n• Remove Background\n• And more coming soon!",
        inline=False
    )

    info.add_field(
        name="🔗 Important Links",
        value="[Add to Server](https://discord.com/api/oauth2/authorize?client_id=1060316037997936751&permissions=8&scope=bot)\n[Support Server](https://discord.gg/FSjRSaJ4bt)",
        inline=False
    )

    info.add_field(
        name="👨‍💻 Credits",
        value="Created by <@977190163736322088>\nMade with ❤️ for the editing community",
        inline=False
    )

    info.set_image(url="https://media.discordapp.net/attachments/977518313217347604/1060480442656116797/download.png")
    info.set_footer(
        text="© Ryujin Bot (2023-2025) | Info System",
        icon_url=RYUJIN_LOGO
    )
    info.set_author(
        name="Ryujin",
        icon_url=RYUJIN_LOGO
    )

    return info

def create_ads_embed():
    """Creates the promotional embed with support buttons"""
    embed = nextcord.Embed(
        title="Support Ryujin Bot",
        description="Help us keep Ryujin Bot running and get exclusive features! 🌟",
        color=0x2a2a2a
    )
    
    embed.add_field(
        name="Why Support Us?",
        value="• Keep the bot running 24/7\n• Get new features faster\n• Support the development\n• Get exclusive role in the support server",
        inline=False
    )

    embed.add_field(
        name="How to Support?",
        value="• Donate to the project\n• Invite the bot to your server\n• Join the support server\n• Share the bot with your friends",
        inline=False
    )

    embed.add_field(
        name="Why the bot has these ads?",
        value="The bot has these ads because it costs a lot of money to keep it running 24/7. The ads help us keep the bot running and get new features faster.",
        inline=False
    )

    embed.set_author(
        name="Ryujin",
        icon_url=RYUJIN_LOGO
    )
    
    embed.set_footer(
        text="© Ryujin Bot (2023-2025) | Ads System",
        icon_url=RYUJIN_LOGO
    )
    
    return embed

async def maybe_send_ad(interaction: nextcord.Interaction):
    """Sends an ad with 20% probability if ads are not disabled"""
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

class SupportButtons(nextcord.ui.View):
    def __init__(self):
        super().__init__(timeout=None)
        
        self.add_item(nextcord.ui.Button(
            style=nextcord.ButtonStyle.gray,
            label="Support Server",
            url="https://discord.gg/FSjRSaJ4bt"
        ))
        self.add_item(nextcord.ui.Button(
            style=nextcord.ButtonStyle.gray,
            label="Support Project",
            url="https://ko-fi.com/ryujinsupport"
        ))

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

# Info Command
@bot.slash_command(
    name="info",
    description="See the information about the bot.",
)
async def info(Interaction):
    if Interaction.user.id in blacklist:
        embed = nextcord.Embed(
            title="You are blacklisted!",
            description=f"**You can't use Ryujin's commands anymore because you have been blacklisted for `{blacklist[Interaction.user.id]}`.**",
            color=nextcord.Color.red()
        )
        embed.set_footer(text="© Ryujin Bot (2023-2025) | Blacklist System")
        await Interaction.send(embed=embed, ephemeral=True)
        return

    await Interaction.send(embed=create_info_embed(), ephemeral=True)
    await maybe_send_ad(Interaction)
# Resources Command
@bot.slash_command(
    name="resources",
    description="See the editing resources that the bot has.",
)
async def resources(Interaction):
    user_id = Interaction.user.id
    if user_id in blacklist:
        embed = nextcord.Embed(
            title="You are blacklisted!",
            description=f"**You can't use Ryujin's commands anymore because you have been blacklisted for `{blacklist[user_id]}`.**",
            color=nextcord.Color.red()
        )
        embed.set_footer(
            text="© Ryujin Bot (2023-2025) | Blacklist System",
            icon_url="https://images-ext-2.discordapp.net/external/LEy12yVHJziqiqnjHzdlmAGVx-rL7xsKzu3A57CfV3M/%3Fsize%3D1024/https/cdn.discordapp.com/avatars/1059400568805785620/63a77f852ea29f37961f458c53fb5a97.png?width=676&height=676"
        )
        embed.set_author(
            name="Ryujin",
            icon_url="https://images-ext-2.discordapp.net/external/LEy12yVHJziqiqnjHzdlmAGVx-rL7xsKzu3A57CfV3M/%3Fsize%3D1024/https/cdn.discordapp.com/avatars/1059400568805785620/63a77f852ea29f37961f458c53fb5a97.png?width=676&height=676"
        )
        await Interaction.send(embed=embed, ephemeral=True)
        return
    overlays = len([f for f in os.listdir("resources/overlays") if f.endswith(".mp4")])
    edit_audios_categories = len(os.listdir("resources/edit audios"))
    with open("edits.txt", "r") as f:
        edits = len(f.read().strip().split("\n"))
    stats = nextcord.Embed(title="Resources", description="**Number of resouces that `Ryujin Editing Bot` has:**")
    stats.add_field(name="Overlays", value=overlays)
    stats.add_field(name="Edit audios categories", value=edit_audios_categories)
    stats.add_field(name="Edits", value=edits)
    stats.set_footer(
        text="© Ryujin Bot (2023-2025) | Resources System",
        icon_url="https://images-ext-2.discordapp.net/external/LEy12yVHJziqiqnjHzdlmAGVx-rL7xsKzu3A57CfV3M/%3Fsize%3D1024/https/cdn.discordapp.com/avatars/1059400568805785620/63a77f852ea29f37961f458c53fb5a97.png?width=676&height=676"
    )
    stats.set_author(name="Ryujin", icon_url="https://images-ext-2.discordapp.net/external/LEy12yVHJziqiqnjHzdlmAGVx-rL7xsKzu3A57CfV3M/%3Fsize%3D1024/https/cdn.discordapp.com/avatars/1059400568805785620/63a77f852ea29f37961f458c53fb5a97.png?width=676&height=676")
    await Interaction.send(embed=stats)
    await maybe_send_ad(Interaction)
# Show Guilds Command
@bot.slash_command(
    name="show_guilds",
    description="Shows all the guilds that Ryujin is in!",
)
async def show_guilds(Interaction):
    if Interaction.user.id == 977190163736322088:
        guilds = list(bot.guilds)
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
            embed.set_author(name="Ryujin", icon_url="https://images-ext-2.discordapp.net/external/LEy12yVHJziqiqnjHzdlmAGVx-rL7xsKzu3A57CfV3M/%3Fsize%3D1024/https/cdn.discordapp.com/avatars/1059400568805785620/63a77f852ea29f37961f458c53fb5a97.png?width=676&height=676")
            embed.set_footer(
                text="© Ryujin Bot (2023-2025) | Info System",
                icon_url="https://images-ext-2.discordapp.net/external/LEy12yVHJziqiqnjHzdlmAGVx-rL7xsKzu3A57CfV3M/%3Fsize%3D1024/https/cdn.discordapp.com/avatars/1059400568805785620/63a77f852ea29f37961f458c53fb5a97.png?width=676&height=676"
            )
            
            for name, value in fields:
                embed.add_field(name=name, value=value)
            
            await Interaction.send(embed=embed, ephemeral=True)
            await maybe_send_ad(Interaction)
    else:
        await Interaction.send("This command is working only for `moongetsu`.", ephemeral=True)

# Manage System Command
@bot.slash_command(
    name="managesystem",
    description="Setup, change, or remove a system channel.",
)
async def system(
    Interaction, 
    system: str = SlashOption(
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
    action: str = SlashOption(
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

    if not (Interaction.user.id == 977190163736322088 or 
            Interaction.user == Interaction.guild.owner or 
            Interaction.user.guild_permissions.administrator):
        await Interaction.send(
            f"Only the server owner or administrators can manage the `{system}` channel.",
            ephemeral=True
        )
        return

    server_id = str(Interaction.guild.id)
    channel_id = str(Interaction.channel.id)
    config = SYSTEM_CONFIG[system]
    table = config["table"]

    cursor = connection.cursor()

    if action in ["setup", "change"]:
        cursor.execute(f"SELECT * FROM {table} WHERE server_id = %s", (server_id,))
        existing_channel = cursor.fetchone()

        if existing_channel and action == "setup":
            await Interaction.send(
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
        
        connection.commit()
        
        if action == "setup":
            system_channel = Interaction.guild.get_channel(int(channel_id))
            if system_channel:
                embed = nextcord.Embed(
                    title=config["title"],
                    description=config["description"],
                    color=0x2a2a2a
                )
                embed.set_image(url=config["image_url"])
                embed.set_footer(
                    text=f"© Ryujin Bot (2023-2025) | {config['title']} System",
                    icon_url="https://images-ext-2.discordapp.net/external/LEy12yVHJziqiqnjHzdlmAGVx-rL7xsKzu3A57CfV3M/%3Fsize%3D1024/https/cdn.discordapp.com/avatars/1059400568805785620/63a77f852ea29f37961f458c53fb5a97.png?width=676&height=676"
                )
                message = await system_channel.send(embed=embed)
                await message.pin()

        await Interaction.send(
            f"The `{system}` channel has been {'set' if action == 'setup' else 'updated'} in this channel.",
            ephemeral=True
        )

    elif action == "remove":
        cursor.execute(f"SELECT * FROM {table} WHERE server_id = %s", (server_id,))
        existing_channel = cursor.fetchone()

        if existing_channel:
            cursor.execute(f"DELETE FROM {table} WHERE server_id = %s", (server_id,))
            connection.commit()
            await Interaction.send(
                f"The `{system}` channel configuration has been removed from this server.",
                ephemeral=True
            )
        else:
            await Interaction.send(
                f"There is no `{system}` channel set in this server.",
                ephemeral=True
            )

    cursor.close()
    await maybe_send_ad(Interaction)

# Help Command
@bot.slash_command(
    name="help",
    description="Shows all Ryujin's commands!",
)
async def help(Interaction):
    user_id = Interaction.user.id
    if user_id in blacklist:
        embed = nextcord.Embed(
            title="You are blacklisted!",
            description=f"**You can't use Ryujin's commands anymore because you have been blacklisted for `{blacklist[user_id]}`.**",
            color=nextcord.Color.red()
        )
        embed.set_footer(
            text="© Ryujin Bot (2023-2025) | Blacklist System",
            icon_url="https://images-ext-2.discordapp.net/external/LEy12yVHJziqiqnjHzdlmAGVx-rL7xsKzu3A57CfV3M/%3Fsize%3D1024/https/cdn.discordapp.com/avatars/1059400568805785620/63a77f852ea29f37961f458c53fb5a97.png?width=676&height=676"
        )
        embed.set_author(
            name="Ryujin",
            icon_url="https://images-ext-2.discordapp.net/external/LEy12yVHJziqiqnjHzdlmAGVx-rL7xsKzu3A57CfV3M/%3Fsize%3D1024/https/cdn.discordapp.com/avatars/1059400568805785620/63a77f852ea29f37961f458c53fb5a97.png?width=676&height=676"
        )
        await Interaction.send(embed=embed, ephemeral=True)
        return

    commands = {
        "Information": [
            ("info", "Shows information about the bot"),
            ("help", "Shows all Ryujin's commands"),
            ("resources", "Shows all the available editing resources"),
            ("bug", "Sends the server support link to report a bug"),
            ("donate", "Support the development of Ryujin")
        ],
        "Media Tools": [
            ("overlay", "Sends a random overlay"),
            ("edit_audio <style>", "Sends a random edit audio for each style"),
            ("audios_categories", "Shows all the available audio categories"),
            ("random_edit", "Sends a random edit. Good command if you don't have ideas what to edit"),
            ("compress_file <file>", "Compress a file to reduce its size while maintaining quality"),
            ("resize_video <video> <width> <height>", "Resize a video to a specific resolution while maintaining aspect ratio")
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
            ("convert <from_format> <to_format> <file>", "Convert a file from one format to another")
        ],
        "Setup": [
            ("managesystem", "Setup, change, or remove a system channel (YouTube, Instagram, TikTok Downloader, Remove Background & Anime Search)")
        ]
    }

    embed = nextcord.Embed(
        title="Ryujin Command Guide",
        description="Here's everything I can help you with:",
        color=0x2a2a2a
    )

    for category, cmds in commands.items():
        formatted_commands = "\n".join(f"`/{cmd}` • {desc}" for cmd, desc in cmds)
        embed.add_field(
            name=f"━━ {category} ━━",
            value=formatted_commands,
            inline=False
        )
    
    embed.set_footer(
        text="© Ryujin Bot (2023-2025) | Info System (0.6b)",
        icon_url="https://images-ext-2.discordapp.net/external/LEy12yVHJziqiqnjHzdlmAGVx-rL7xsKzu3A57CfV3M/%3Fsize%3D1024/https/cdn.discordapp.com/avatars/1059400568805785620/63a77f852ea29f37961f458c53fb5a97.png?width=676&height=676"
    )
    embed.set_author(
        name="Ryujin",
        icon_url="https://images-ext-2.discordapp.net/external/LEy12yVHJziqiqnjHzdlmAGVx-rL7xsKzu3A57CfV3M/%3Fsize%3D1024/https/cdn.discordapp.com/avatars/1059400568805785620/63a77f852ea29f37961f458c53fb5a97.png?width=676&height=676"
    )
    await Interaction.send(embed=embed, ephemeral=True)
    await maybe_send_ad(Interaction)

# Preset Command
@bot.slash_command(
    name="preset",
    description="Sends a random preset from a specific category!",
)
async def preset(Interaction, category: str):
    user_id = Interaction.user.id
    if user_id in blacklist:
        embed = nextcord.Embed(
            title="You are blacklisted!",
            description=f"**You can't use Ryujin's commands anymore because you have been blacklisted for `{blacklist[user_id]}`.**",
            color=nextcord.Color.red()
        )
        embed.set_footer(
            text="© Ryujin Bot (2023-2025) | Blacklist System",
            icon_url="https://images-ext-2.discordapp.net/external/LEy12yVHJziqiqnjHzdlmAGVx-rL7xsKzu3A57CfV3M/%3Fsize%3D1024/https/cdn.discordapp.com/avatars/1059400568805785620/63a77f852ea29f37961f458c53fb5a97.png?width=676&height=676"
        )
        embed.set_author(
            name="Ryujin",
            icon_url="https://images-ext-2.discordapp.net/external/LEy12yVHJziqiqnjHzdlmAGVx-rL7xsKzu3A57CfV3M/%3Fsize%3D1024/https/cdn.discordapp.com/avatars/1059400568805785620/63a77f852ea29f37961f458c53fb5a97.png?width=676&height=676"
        )
        await Interaction.send(embed=embed, ephemeral=True)
        return
    with open("config/presets.json", "r") as presets_file:
        presets_data = json.load(presets_file)
    presetscategories = presets_data.get("presetscategories", {})
    matching_category = next((key for key in presetscategories if key.lower() == category.lower()), None)
    if not matching_category:
        await Interaction.send(f"**The category `{category}` was not found! Please use `/presets_categories` to see the categories available.**", ephemeral=True)
        return
    category_folder = presetscategories[matching_category]
    assets = [f for f in os.listdir(f"resources/presets/{category_folder}") if f.endswith(".ffx")]
    if not assets:
        await Interaction.send(f"No presets found in the `{matching_category}` category.", ephemeral=True)
        return
    asset = random.choice(assets)
    file_path = os.path.join(f"resources/presets/{category_folder}", asset)
    await Interaction.send(file=nextcord.File(file_path), ephemeral=True)
    await maybe_send_ad(Interaction)
# Presets Categories Command
@bot.slash_command(
    name="presets_categories",
    description="See the presets categories.",
)
async def presets_categories(Interaction):
    user_id = Interaction.user.id
    if user_id in blacklist:
        embed = nextcord.Embed(
            title="You are blacklisted!",
            description=f"**You can't use Ryujin's commands anymore because you have been blacklisted for `{blacklist[user_id]}`.**",
            color=nextcord.Color.red()
        )
        embed.set_footer(
            text="© Ryujin Bot (2023-2025) | Blacklist System",
            icon_url="https://images-ext-2.discordapp.net/external/LEy12yVHJziqiqnjHzdlmAGVx-rL7xsKzu3A57CfV3M/%3Fsize%3D1024/https/cdn.discordapp.com/avatars/1059400568805785620/63a77f852ea29f37961f458c53fb5a97.png?width=676&height=676"
        )
        embed.set_author(
            name="Ryujin",
            icon_url="https://images-ext-2.discordapp.net/external/LEy12yVHJziqiqnjHzdlmAGVx-rL7xsKzu3A57CfV3M/%3Fsize%3D1024/https/cdn.discordapp.com/avatars/1059400568805785620/63a77f852ea29f37961f458c53fb5a97.png?width=676&height=676"
        )
        await Interaction.send(embed=embed, ephemeral=True)
        return
    with open("config/presets.json", "r") as presets_file:
        presets_data = json.load(presets_file)
    presetscategories = presets_data.get("presetscategories", {})
    categories = list(presetscategories.keys())
    categories_list = "\n".join(categories)
    embed = nextcord.Embed(title="Presets Categories")
    embed.description = categories_list
    embed.set_footer(
        text="© Ryujin Bot (2023-2025) | Resources System",
        icon_url="https://images-ext-2.discordapp.net/external/LEy12yVHJziqiqnjHzdlmAGVx-rL7xsKzu3A57CfV3M/%3Fsize%3D1024/https/cdn.discordapp.com/avatars/1059400568805785620/63a77f852ea29f37961f458c53fb5a97.png?width=676&height=676"
    )
    await Interaction.send("Have some presets?\n**Please join our discord server!** https://discord.gg/FSjRSaJ4bt", embed=embed, ephemeral=True)
    await maybe_send_ad(Interaction)
# Random Edit Command
@bot.slash_command(
    name="random_edit",
    description="Sends a random edit. Good command if you don't have ideas what to edit.",
)
async def random_edit(Interaction):
    user_id = Interaction.user.id
    if user_id in blacklist:
        embed = nextcord.Embed(
            title="You are blacklisted!",
            description=f"**You can't use Ryujin's commands anymore because you have been blacklisted for `{blacklist[user_id]}`.**",
            color=nextcord.Color.red()
        )
        embed.set_footer(
            text="© Ryujin Bot (2023-2025) | Blacklist System",
            icon_url="https://images-ext-2.discordapp.net/external/LEy12yVHJziqiqnjHzdlmAGVx-rL7xsKzu3A57CfV3M/%3Fsize%3D1024/https/cdn.discordapp.com/avatars/1059400568805785620/63a77f852ea29f37961f458c53fb5a97.png?width=676&height=676"
        )
        embed.set_author(
            name="Ryujin",
            icon_url="https://images-ext-2.discordapp.net/external/LEy12yVHJziqiqnjHzdlmAGVx-rL7xsKzu3A57CfV3M/%3Fsize%3D1024/https/cdn.discordapp.com/avatars/1059400568805785620/63a77f852ea29f37961f458c53fb5a97.png?width=676&height=676"
        )
        await Interaction.send(embed=embed, ephemeral=True)
        return
    with open("edits.txt", "r") as f:
        lines = f.read().strip().split("\n")
    link = random.choice(lines)
    button_view = AnotherButtonEdit()
    await Interaction.send(link, ephemeral=True, view=button_view)
    await maybe_send_ad(Interaction)
    
# Guild Join Event
@bot.event
async def on_guild_join(guild):
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

# Guild Remove Event  
@bot.event
async def on_guild_remove(guild):
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

sfxcategories = {
    "dragonball": "dragonball",
    "fireforce": "fireforce",
    "naruto": "naruto",
    "whooshes": "whooshes",
    "random": "random"
}

# SFX Command
@bot.slash_command(
    name="sfx",
    description="Sends a random SFX!",
)
async def sfx(Interaction, category: str):
    user_id = Interaction.user.id
    if user_id in blacklist:
        embed = nextcord.Embed(
            title="You are blacklisted!",
            description=f"**You can't use Ryujin's commands anymore because you have been blacklisted for `{blacklist[user_id]}`.**",
            color=nextcord.Color.red()
        )
        embed.set_footer(
            text="© Ryujin Bot (2023-2025) | Blacklist System",
            icon_url="https://images-ext-2.discordapp.net/external/LEy12yVHJziqiqnjHzdlmAGVx-rL7xsKzu3A57CfV3M/%3Fsize%3D1024/https/cdn.discordapp.com/avatars/1059400568805785620/63a77f852ea29f37961f458c53fb5a97.png?width=676&height=676"
        )
        embed.set_author(
            name="Ryujin",
            icon_url="https://images-ext-2.discordapp.net/external/LEy12yVHJziqiqnjHzdlmAGVx-rL7xsKzu3A57CfV3M/%3Fsize%3D1024/https/cdn.discordapp.com/avatars/1059400568805785620/63a77f852ea29f37961f458c53fb5a97.png?width=676&height=676"
        )
        await Interaction.send(embed=embed, ephemeral=True)
        return
    if category not in sfxcategories:
        await Interaction.send(f"**The category `{category}` was not found! Please use `/sfx_categories` to see the categories available.**")
        return
    assets = [f for f in os.listdir(f"resources/sfx/{category}") if f.endswith(".mp3")]
    asset = random.choice(assets)
    file_path = os.path.join(f"resources/sfx/{category}", asset)
    await Interaction.send(file=nextcord.File(file_path), ephemeral=True)
    await maybe_send_ad(Interaction)
# SFX Categories Command
@bot.slash_command(
    name="sfx_categories",
    description="See the SFX categories.",
)
async def sfx_categories(Interaction):
    user_id = Interaction.user.id
    if user_id in blacklist:
        embed = nextcord.Embed(
            title="You are blacklisted!",
            description=f"**You can't use Ryujin's commands anymore because you have been blacklisted for `{blacklist[user_id]}`.**",
            color=nextcord.Color.red()
        )
        embed.set_footer(
            text="© Ryujin Bot (2023-2025) | Blacklist System",
            icon_url="https://images-ext-2.discordapp.net/external/LEy12yVHJziqiqnjHzdlmAGVx-rL7xsKzu3A57CfV3M/%3Fsize%3D1024/https/cdn.discordapp.com/avatars/1059400568805785620/63a77f852ea29f37961f458c53fb5a97.png?width=676&height=676"
        )
        embed.set_author(
            name="Ryujin",
            icon_url="https://images-ext-2.discordapp.net/external/LEy12yVHJziqiqnjHzdlmAGVx-rL7xsKzu3A57CfV3M/%3Fsize%3D1024/https/cdn.discordapp.com/avatars/1059400568805785620/63a77f852ea29f37961f458c53fb5a97.png?width=676&height=676"
        )
        await Interaction.send(embed=embed, ephemeral=True)
        return
    embed = nextcord.Embed(title="SFX Categories")
    embed.description = "\n".join(sfxcategories)
    embed.set_footer(
        text="© Ryujin Bot (2023-2025) | Resources System",
        icon_url="https://images-ext-2.discordapp.net/external/LEy12yVHJziqiqnjHzdlmAGVx-rL7xsKzu3A57CfV3M/%3Fsize%3D1024/https/cdn.discordapp.com/avatars/1059400568805785620/63a77f852ea29f37961f458c53fb5a97.png?width=676&height=676"
    )
    await Interaction.send("Have some SFX?\n**Please join our discord server!** https://discord.gg/FSjRSaJ4bt", embed=embed, ephemeral=True)
    await maybe_send_ad(Interaction)
# Project File Command
@bot.slash_command(
    name="project_file",
    description="Sends a project file and a preview link.",
)
async def project(Interaction, project_number: int):
    user_id = Interaction.user.id
    if user_id in blacklist:
        embed = nextcord.Embed(
            title="You are blacklisted!",
            description=f"**You can't use Ryujin's commands anymore because you have been blacklisted for `{blacklist[user_id]}`.**",
            color=nextcord.Color.red()
        )
        embed.set_footer(
            text="© Ryujin Bot (2023-2025) | Blacklist System",
            icon_url="https://images-ext-2.discordapp.net/external/LEy12yVHJziqiqnjHzdlmAGVx-rL7xsKzu3A57CfV3M/%3Fsize%3D1024/https/cdn.discordapp.com/avatars/1059400568805785620/63a77f852ea29f37961f458c53fb5a97.png?width=676&height=676"
        )
        embed.set_author(
            name="Ryujin",
            icon_url="https://images-ext-2.discordapp.net/external/LEy12yVHJziqiqnjHzdlmAGVx-rL7xsKzu3A57CfV3M/%3Fsize%3D1024/https/cdn.discordapp.com/avatars/1059400568805785620/63a77f852ea29f37961f458c53fb5a97.png?width=676&height=676"
        )
        await Interaction.send(embed=embed, ephemeral=True)
        return
    project_files_dir = "resources/project_files"
    try:
        project_name = project_files.get(str(project_number))
    except KeyError:
        return await Interaction.send(f"No project file found with number {project_number}.", ephemeral=True)
    project_path = os.path.join(project_files_dir, project_name.replace(" ", "_"))
    if os.path.exists(project_path):
        for root, dirs, files in os.walk(project_path):
            for file in files:
                if file.endswith(".aep"):
                    aep_file = os.path.join(root, file)
                if file == "preview.txt":
                    with open(os.path.join(root, file), "r") as f:
                        preview_link = f.read().strip()
        await Interaction.send(f"{preview_link}", file=nextcord.File(aep_file), ephemeral=True)
        await maybe_send_ad(Interaction)
    else:
        await Interaction.send(f"The specified project files for {project_name} do not exist.", ephemeral=True)

# Script Command
@bot.slash_command(
    name="script",
    description="Sends a script for After Effects.",
)
async def script_command(Interaction, script_number: int):
    user_id = Interaction.user.id
    if user_id in blacklist:
        embed = nextcord.Embed(
            title="You are blacklisted!",
            description=f"**You can't use Ryujin's commands anymore because you have been blacklisted for `{blacklist[user_id]}`.**",
            color=nextcord.Color.red()
        )
        embed.set_footer(
            text="© Ryujin Bot (2023-2025) | Blacklist System",
            icon_url="https://images-ext-2.discordapp.net/external/LEy12yVHJziqiqnjHzdlmAGVx-rL7xsKzu3A57CfV3M/%3Fsize%3D1024/https/cdn.discordapp.com/avatars/1059400568805785620/63a77f852ea29f37961f458c53fb5a97.png?width=676&height=676"
        )
        embed.set_author(
            name="Ryujin",
            icon_url="https://images-ext-2.discordapp.net/external/LEy12yVHJziqiqnjHzdlmAGVx-rL7xsKzu3A57CfV3M/%3Fsize%3D1024/https/cdn.discordapp.com/avatars/1059400568805785620/63a77f852ea29f37961f458c53fb5a97.png?width=676&height=676"
        )
        await Interaction.send(embed=embed, ephemeral=True)
        return

    script_files_dir = "resources/scripts"
    try:
        script_name = script_files.get(str(script_number))
    except KeyError:
        return await Interaction.send(f"No script found with number {script_number}.", ephemeral=True)

    script_path = os.path.join(script_files_dir, script_name.replace(" ", "_"))

    if os.path.exists(script_path):
        for root, dirs, files in os.walk(script_path):
            for file in files:
                if file.endswith(("jsx", ".jsxbin", "zip", "rar")):
                    script_file = os.path.join(root, file)
                if file == "preview.txt":
                    with open(os.path.join(root, file), "r") as f:
                        preview_link = f.read().strip()

        await Interaction.send(f"{preview_link}", file=nextcord.File(script_file), ephemeral=True)
        await maybe_send_ad(Interaction)
    else:
        await Interaction.send(f"The specified script file for {script_name} does not exist.", ephemeral=True)

# Extension Command
@bot.slash_command(
    name="extension",
    description="Sends a extension for After Effects.",
)
async def extension(Interaction, extension_number: int):
    user_id = Interaction.user.id
    if user_id in blacklist:
        embed = nextcord.Embed(
            title="You are blacklisted!",
            description=f"**You can't use Ryujin's commands anymore because you have been blacklisted for `{blacklist[user_id]}`.**",
            color=nextcord.Color.red()
        )
        embed.set_footer(
            text="© Ryujin Bot (2023-2025) | Blacklist System",
            icon_url="https://images-ext-2.discordapp.net/external/LEy12yVHJziqiqnjHzdlmAGVx-rL7xsKzu3A57CfV3M/%3Fsize%3D1024/https/cdn.discordapp.com/avatars/1059400568805785620/63a77f852ea29f37961f458c53fb5a97.png?width=676&height=676"
        )
        embed.set_author(
            name="Ryujin",
            icon_url="https://images-ext-2.discordapp.net/external/LEy12yVHJziqiqnjHzdlmAGVx-rL7xsKzu3A57CfV3M/%3Fsize%3D1024/https/cdn.discordapp.com/avatars/1059400568805785620/63a77f852ea29f37961f458c53fb5a97.png?width=676&height=676"
        )
        await Interaction.send(embed=embed, ephemeral=True)
        return
    extension_files_dir = "resources/extensions"
    try:
        extension_name = extension_files.get(str(extension_number))
    except KeyError:
        return await Interaction.send(f"No extension found with number {extension_number}.", ephemeral=True)
    extension_path = os.path.join(extension_files_dir, extension_name.replace(" ", "_"))
    if os.path.exists(extension_path):
        for root, dirs, files in os.walk(extension_path):
            for file in files:
                if file.endswith((".zip", ".rar", ".jsx")):
                    extension_file = os.path.join(root, file)
                if file == "preview.txt":
                    with open(os.path.join(root, file), "r") as f:
                        preview_link = f.read().strip()
        await Interaction.send(f"{preview_link}", file=nextcord.File(extension_file), ephemeral=True)
        await maybe_send_ad(Interaction)
    else:
        await Interaction.send(f"The specified extension file for {extension_name} do not exist.", ephemeral=True)

# Projects List Command
@bot.slash_command(
    name="projects_list",
    description="Shows all the available project files"
)
async def projectfilelist(Interaction):
    user_id = Interaction.user.id
    if user_id in blacklist:
        embed = nextcord.Embed(
            title="You are blacklisted!",
            description=f"**You can't use Ryujin's commands anymore because you have been blacklisted for `{blacklist[user_id]}`.**",
            color=nextcord.Color.red()
        )
        embed.set_footer(
            text="© Ryujin Bot (2023-2025) | Blacklist System",
            icon_url="https://images-ext-2.discordapp.net/external/LEy12yVHJziqiqnjHzdlmAGVx-rL7xsKzu3A57CfV3M/%3Fsize%3D1024/https/cdn.discordapp.com/avatars/1059400568805785620/63a77f852ea29f37961f458c53fb5a97.png?width=676&height=676"
        )
        embed.set_author(
            name="Ryujin",
            icon_url="https://images-ext-2.discordapp.net/external/LEy12yVHJziqiqnjHzdlmAGVx-rL7xsKzu3A57CfV3M/%3Fsize%3D1024/https/cdn.discordapp.com/avatars/1059400568805785620/63a77f852ea29f37961f458c53fb5a97.png?width=676&height=676"
        )
        await Interaction.send(embed=embed, ephemeral=True)
        return
    subfolders = os.listdir("resources/project_files")
    subfolders = [folder.replace("_", " ") for folder in subfolders]
    
    subfolders.sort()
    
    files = "\n".join(f"**{i+1}**. {folder}" for i, folder in enumerate(subfolders))
    embed = nextcord.Embed(title="Project Files List")
    embed.description = files
    embed.add_field(name="How to use the command?", value="\n Example:\nIf you want `AMV Flow edit (Chophurr)`, you can just use: **/project_file 1**.")
    embed.set_footer(
        text="© Ryujin Bot (2023-2025) | Resources System",
        icon_url="https://images-ext-2.discordapp.net/external/LEy12yVHJziqiqnjHzdlmAGVx-rL7xsKzu3A57CfV3M/%3Fsize%3D1024/https/cdn.discordapp.com/avatars/1059400568805785620/63a77f852ea29f37961f458c53fb5a97.png?width=676&height=676"
    )
    await Interaction.send("Have some Project Files?\n**Please join our discord server!** https://discord.gg/FSjRSaJ4bt", embed=embed, ephemeral=True)
    await maybe_send_ad(Interaction)
    
# Scripts List Command
@bot.slash_command(
    name="scripts_list",
    description="Shows all the available scripts for After Effects"
)
async def scriptsfilelist(Interaction):
    user_id = Interaction.user.id
    if user_id in blacklist:
        embed = nextcord.Embed(
            title="You are blacklisted!",
            description=f"**You can't use Ryujin's commands anymore because you have been blacklisted for `{blacklist[user_id]}`.**",
            color=nextcord.Color.red()
        )
        embed.set_footer(
            text="© Ryujin Bot (2023-2025) | Blacklist System",
            icon_url="https://images-ext-2.discordapp.net/external/LEy12yVHJziqiqnjHzdlmAGVx-rL7xsKzu3A57CfV3M/%3Fsize%3D1024/https/cdn.discordapp.com/avatars/1059400568805785620/63a77f852ea29f37961f458c53fb5a97.png?width=676&height=676"
        )
        embed.set_author(
            name="Ryujin",
            icon_url="https://images-ext-2.discordapp.net/external/LEy12yVHJziqiqnjHzdlmAGVx-rL7xsKzu3A57CfV3M/%3Fsize%3D1024/https/cdn.discordapp.com/avatars/1059400568805785620/63a77f852ea29f37961f458c53fb5a97.png?width=676&height=676"
        )
        await Interaction.send(embed=embed, ephemeral=True)
        return
    subfolders = os.listdir("resources/scripts")
    subfolders = [folder.replace("_", " ") for folder in subfolders]
    
    subfolders.sort()
    
    files = "\n".join(f"**{i+1}**. {folder}" for i, folder in enumerate(subfolders))
    embed = nextcord.Embed(title="Scripts List")
    embed.description = files
    embed.add_field(name="How to use the command?", value="\n Example:\nIf you want to download `Flow Script`, you can just use: **/script 1**.")
    embed.set_footer(
        text="© Ryujin Bot (2023-2025) | Resources System",
        icon_url="https://images-ext-2.discordapp.net/external/LEy12yVHJziqiqnjHzdlmAGVx-rL7xsKzu3A57CfV3M/%3Fsize%3D1024/https/cdn.discordapp.com/avatars/1059400568805785620/63a77f852ea29f37961f458c53fb5a97.png?width=676&height=676"
    )
    await Interaction.send(embed=embed, ephemeral=True)
    await maybe_send_ad(Interaction)
# Extensions List Command
@bot.slash_command(
    name="extensions_list",
    description="Shows all the available extensions for After Effects"
)
async def projectfilelist(Interaction):
    user_id = Interaction.user.id
    if user_id in blacklist:
        embed = nextcord.Embed(
            title="You are blacklisted!",
            description=f"**You can't use Ryujin's commands anymore because you have been blacklisted for `{blacklist[user_id]}`.**",
            color=nextcord.Color.red()
        )
        embed.set_footer(
            text="© Ryujin Bot (2023-2025) | Blacklist System",
            icon_url="https://images-ext-2.discordapp.net/external/LEy12yVHJziqiqnjHzdlmAGVx-rL7xsKzu3A57CfV3M/%3Fsize%3D1024/https/cdn.discordapp.com/avatars/1059400568805785620/63a77f852ea29f37961f458c53fb5a97.png?width=676&height=676"
        )
        embed.set_author(
            name="Ryujin",
            icon_url="https://images-ext-2.discordapp.net/external/LEy12yVHJziqiqnjHzdlmAGVx-rL7xsKzu3A57CfV3M/%3Fsize%3D1024/https/cdn.discordapp.com/avatars/1059400568805785620/63a77f852ea29f37961f458c53fb5a97.png?width=676&height=676"
        )
        await Interaction.send(embed=embed, ephemeral=True)
        return
    subfolders = os.listdir("resources/extensions")
    subfolders = [folder.replace("_", " ") for folder in subfolders]
    
    subfolders.sort()
    
    files = "\n".join(f"**{i+1}**. {folder}" for i, folder in enumerate(subfolders))
    embed = nextcord.Embed(title="extensions List")
    embed.description = files
    embed.add_field(name="How to use the command?", value="\n Example:\nIf you want to download `Flow Script`, you can just use: **/script 1**.")
    embed.set_footer(
        text="© Ryujin Bot (2023-2025) | Resources System",
        icon_url="https://images-ext-2.discordapp.net/external/LEy12yVHJziqiqnjHzdlmAGVx-rL7xsKzu3A57CfV3M/%3Fsize%3D1024/https/cdn.discordapp.com/avatars/1059400568805785620/63a77f852ea29f37961f458c53fb5a97.png?width=676&height=676"
    )
    await Interaction.send(embed=embed, ephemeral=True)
    await maybe_send_ad(Interaction)

# Bot Stats Command
@bot.slash_command(
    name="bot_stats",
    description="Display detailed statistics about the bot.",
)
async def bot_stats(Interaction):
    user_id = Interaction.user.id
    if user_id in blacklist:
        embed = nextcord.Embed(
            title="You are blacklisted!",
            description=f"**You can't use Ryujin's commands anymore because you have been blacklisted for `{blacklist[user_id]}`.**",
            color=nextcord.Color.red()
        )
        embed.set_footer(
            text="© Ryujin Bot (2023-2025) | Blacklist System",
            icon_url="https://images-ext-2.discordapp.net/external/LEy12yVHJziqiqnjHzdlmAGVx-rL7xsKzu3A57CfV3M/%3Fsize%3D1024/https/cdn.discordapp.com/avatars/1059400568805785620/63a77f852ea29f37961f458c53fb5a97.png?width=676&height=676"
        )
        await Interaction.send(embed=embed, ephemeral=True)
        return

    total_servers = len(bot.guilds)
    total_members = sum(len(guild.members) for guild in bot.guilds)
    current_time = datetime.now()
    uptime = current_time - bot.start_time
    latency_ms = round(bot.latency * 1000, 2)
    
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
        icon_url="https://images-ext-2.discordapp.net/external/LEy12yVHJziqiqnjHzdlmAGVx-rL7xsKzu3A57CfV3M/%3Fsize%3D1024/https/cdn.discordapp.com/avatars/1059400568805785620/63a77f852ea29f37961f458c53fb5a97.png?width=676&height=676"
    )
    embed.set_footer(
        text="© Ryujin Bot (2023-2025) | Stats System",
        icon_url="https://images-ext-2.discordapp.net/external/LEy12yVHJziqiqnjHzdlmAGVx-rL7xsKzu3A57CfV3M/%3Fsize%3D1024/https/cdn.discordapp.com/avatars/1059400568805785620/63a77f852ea29f37961f458c53fb5a97.png?width=676&height=676"
    )
    await maybe_send_ad(Interaction)
    await Interaction.send(embed=embed, ephemeral=True)

# Trending Command
@bot.slash_command(
    name="trending",
    description="See what's trending in AMV Community!"
)
async def trending(Interaction):
    user_id = Interaction.user.id
    if user_id in blacklist:
        embed = nextcord.Embed(
            title="You are blacklisted!",
            description=f"You can't use Ryujin's commands anymore because you have been blacklisted for `{blacklist[user_id]}`.",
            color=nextcord.Color.red()
        )
        embed.set_footer(
            text="© Ryujin Bot (2023-2025) | Blacklist System",
            icon_url="https://images-ext-2.discordapp.net/external/LEy12yVHJziqiqnjHzdlmAGVx-rL7xsKzu3A57CfV3M/%3Fsize%3D1024/https/cdn.discordapp.com/avatars/1059400568805785620/63a77f852ea29f37961f458c53fb5a97.png?width=676&height=676"
        )
        embed.set_author(
            name="Ryujin",
            icon_url="https://images-ext-2.discordapp.net/external/LEy12yVHJziqiqnjHzdlmAGVx-rL7xsKzu3A57CfV3M/%3Fsize%3D1024/https/cdn.discordapp.com/avatars/1059400568805785620/63a77f852ea29f37961f458c53fb5a97.png?width=676&height=676"
        )
        await Interaction.send(embed=embed, ephemeral=True)
        return

    try:
        with open('config/trending.json', 'r') as f:
            trending_data = json.load(f)

        embed = nextcord.Embed(
            title="📈 AMV Community Trends",
            description="Here's what's currently trending in the AMV community:",
            color=0x2a2a2a
        )

        songs_field = ""
        for song in trending_data["Songs"]:
            songs_field += f"» **{song['name']}**\n"
            songs_field += f"Original: [YouTube]({song['link']})\n"
            songs_field += f"Popular Edit: [YouTube]({song['popular-edit']})\n\n"

        embed.add_field(
            name="🎵 Trending Songs in AMVs",
            value=songs_field or "No songs trending",
            inline=False
        )

        anime_field = ""
        for anime in trending_data["Animes"]:
            anime_field += f"» **{anime['name']}**\n"

        embed.add_field(
            name="📺 Trending Anime",
            value=anime_field or "No anime trending",
            inline=False
        )

        embed.set_footer(
            text="© Ryujin Bot (2023-2025) | Trending System",
            icon_url="https://images-ext-2.discordapp.net/external/LEy12yVHJziqiqnjHzdlmAGVx-rL7xsKzu3A57CfV3M/%3Fsize%3D1024/https/cdn.discordapp.com/avatars/1059400568805785620/63a77f852ea29f37961f458c53fb5a97.png?width=676&height=676"
        )
        embed.set_author(
            name="Ryujin",
            icon_url="https://images-ext-2.discordapp.net/external/LEy12yVHJziqiqnjHzdlmAGVx-rL7xsKzu3A57CfV3M/%3Fsize%3D1024/https/cdn.discordapp.com/avatars/1059400568805785620/63a77f852ea29f37961f458c53fb5a97.png?width=676&height=676"
        )

        await Interaction.send(embed=embed, ephemeral=True)
        await maybe_send_ad(Interaction)

    except Exception as e:
        error_embed = nextcord.Embed(
            title="❌ Error",
            description="Could not fetch trending data. Please try again later.",
            color=nextcord.Color.red()
        )
        await Interaction.send(embed=error_embed, ephemeral=True)
        print(f"Error in trending command: {str(e)}")

# Add Trending Song Command
@bot.slash_command(
    name="add_trending_song",
    description="Add a trending song (Moongetsu only)",
    guild_ids=[1060144274722787328]
)
async def add_trending_song(
    Interaction,
    name: str = SlashOption(description="Song name"),
    link: str = SlashOption(description="Original song YouTube link"),
    popular_edit: str = SlashOption(description="Popular edit YouTube link")
):
    if Interaction.user.id != 977190163736322088:
        await Interaction.send("This command is only for moongetsu!", ephemeral=True)
        return

    try:
        with open('config/trending.json', 'r') as f:
            data = json.load(f)
        
        new_song = {
            "name": name,
            "link": link,
            "popular-edit": popular_edit
        }
        
        data["Songs"].append(new_song)
        
        with open('config/trending.json', 'w') as f:
            json.dump(data, f, indent=4)
            
        await Interaction.send(f"Added song **{name}** to trending!", ephemeral=True)
        
    except Exception as e:
        await Interaction.send(f"Error adding song: {str(e)}", ephemeral=True)

# Add Trending Anime Command
@bot.slash_command(
    name="add_trending_anime",
    description="Add a trending anime (Moongetsu only)",
    guild_ids=[1060144274722787328]
)
async def add_trending_anime(
    Interaction,
    name: str = SlashOption(description="Anime name")
):
    if Interaction.user.id != 977190163736322088:
        await Interaction.send("This command is only for moongetsu!", ephemeral=True)
        return

    try:
        with open('config/trending.json', 'r') as f:
            data = json.load(f)
        
        new_anime = {
            "name": name
        }
        
        data["Animes"].append(new_anime)
        
        with open('config/trending.json', 'w') as f:
            json.dump(data, f, indent=4)
            
        await Interaction.send(f"Added anime **{name}** to trending!", ephemeral=True)
        
    except Exception as e:
        await Interaction.send(f"Error adding anime: {str(e)}", ephemeral=True)

# Remove Trending Item Command
@bot.slash_command(
    name="remove_trending",
    description="Remove a trending item (Moongetsu only)",
    guild_ids=[1060144274722787328]
)
async def remove_trending(
    Interaction,
    type: str = SlashOption(choices=["song", "anime"], description="Type to remove"),
    name: str = SlashOption(description="Name of item to remove")
):
    if Interaction.user.id != 977190163736322088:
        await Interaction.send("This command is only for moongetsu!", ephemeral=True)
        return

    try:
        with open('config/trending.json', 'r') as f:
            data = json.load(f)
        
        if type == "song":
            data["Songs"] = [s for s in data["Songs"] if s["name"] != name]
            item_type = "song"
        else:
            data["Animes"] = [a for a in data["Animes"] if a["name"] != name]
            item_type = "anime"
        
        with open('config/trending.json', 'w') as f:
            json.dump(data, f, indent=4)
            
        await Interaction.send(f"Removed {item_type} **{name}** from trending!", ephemeral=True)
        
    except Exception as e:
        await Interaction.send(f"Error removing item: {str(e)}", ephemeral=True)

# Convert Command
@bot.slash_command(
    name="convert",
    description="Convert a file from one format to another.",
)
async def convert(interaction: nextcord.Interaction, 
                  from_format: str = SlashOption(choices=["MP4", "MKV", "MOV", "AVI", "MP3", "WAV", "M4A", "PNG", "JPG", "JPEG", "SVG", "WEBP", "ICO"]),
                  to_format: str = SlashOption(choices=["MP4", "MKV", "MOV", "AVI", "MP3", "WAV", "M4A", "PNG", "JPG", "JPEG", "SVG", "WEBP", "ICO"]),
                  file: nextcord.Attachment = SlashOption(required=True)):
    await interaction.response.defer(ephemeral=True)
    await file.save(f"temp/{file.filename}")
    input_file = f"temp/{file.filename}"
    base_name = os.path.splitext(file.filename)[0]
    output_file = f"temp/{sanitize_filename(base_name)}.{to_format.lower()}"

    try:
        if from_format in ["MP4", "MKV", "MOV", "AVI"]:
            if to_format in ["MP3", "WAV", "M4A"]:
                video = VideoFileClip(input_file)
                if to_format == "MP3":
                    video.audio.write_audiofile(output_file, codec='libmp3lame')
                elif to_format == "WAV":
                    video.audio.write_audiofile(output_file, codec='pcm_s16le')
                elif to_format == "M4A":
                    video.audio.write_audiofile(output_file, codec='aac')
                video.close()
            elif to_format in ["MP4", "MKV", "MOV", "AVI"]:
                video = VideoFileClip(input_file)
                video.write_videofile(output_file, codec='libx264')
                video.close()
            else:
                await interaction.followup.send("Invalid conversion type.", ephemeral=True)
                return
        elif from_format in ["MP3", "WAV", "M4A"]:
            if to_format in ["MP3", "WAV", "M4A"]:
                audio = AudioFileClip(input_file)
                if to_format == "MP3":
                    audio.write_audiofile(output_file, codec='libmp3lame')
                elif to_format == "WAV":
                    audio.write_audiofile(output_file, codec='pcm_s16le')
                elif to_format == "M4A":
                    audio.write_audiofile(output_file, codec='aac')
                audio.close()
            else:
                await interaction.followup.send("Invalid conversion type.", ephemeral=True)
                return
        elif from_format in ["PNG", "JPG", "JPEG", "SVG", "WEBP", "ICO"]:
            if to_format in ["PNG", "JPG", "JPEG", "SVG", "WEBP", "ICO"]:
                image = Image.open(input_file)
                image.save(output_file)
                image.close()
            else:
                await interaction.followup.send("Invalid conversion type.", ephemeral=True)
                return
        else:
            await interaction.followup.send("Unsupported file format.", ephemeral=True)
            return
        await interaction.followup.send(file=nextcord.File(output_file), ephemeral=True)
        await maybe_send_ad(interaction)
    except Exception as e:
        await interaction.followup.send(f"An error occurred: {e}", ephemeral=True)
    finally:
        if os.path.exists(input_file):
            os.remove(input_file)
        if os.path.exists(output_file):
            os.remove(output_file)

def create_nightcore(input_audio_path, output_audio_path):
    try:
        nc_audio = input_audio_path @ nc.Tones(2)
        nc_audio.export(output_audio_path, format="mp3")
        return True, output_audio_path
    except Exception as e:
        print(f"An error occurred: {e}")
        return False, str(e)

# Nightcore Command
@bot.slash_command(
    name="nightcore",
    description="Converts an uploaded audio file into a Nightcore version."
)
async def nightcore_command(interaction: nextcord.Interaction, song: nextcord.Attachment):
    await interaction.response.defer()
    try:
        audio_path = f"temp/{song.filename}"
        await song.save(audio_path)
        if not audio_path.endswith(('.mp3', '.wav')):
            await interaction.followup.send("❌ Please upload a valid audio file (MP3, WAV).", ephemeral=True)
            return
        output_path = f"temp/nightcore_{song.filename}"
        success, result_path = create_nightcore(audio_path, output_path)
        if success:
            await interaction.followup.send(file=nextcord.File(result_path), ephemeral=True)
            await maybe_send_ad(interaction)
        else:
            await interaction.followup.send(f"❌ Error: {result_path}", ephemeral=True)
        os.remove(audio_path)
        os.remove(result_path)
    except Exception as e:
        await interaction.followup.send(f"❌ An error occurred: {e}", ephemeral=True)

def create_spedup(input_audio_path, output_audio_path):
    try:
        nc_audio = input_audio_path @ nc.Tones(1)
        nc_audio.export(output_audio_path, format="mp3")
        return True, output_audio_path
    except Exception as e:
        print(f"An error occurred: {e}")
        return False, str(e)

# Spedup Command
@bot.slash_command(
    name="spedup",
    description="Converts an uploaded audio file into a Sped Up version."
)
async def spedup_command(interaction: nextcord.Interaction, song: nextcord.Attachment):
    await interaction.response.defer()
    try:
        audio_path = f"temp/{song.filename}"
        await song.save(audio_path)
        if not audio_path.endswith(('.mp3', '.wav')):
            await interaction.followup.send("❌ Please upload a valid audio file (MP3, WAV).", ephemeral=True)
            return
        output_path = f"temp/spedup_{song.filename}"
        success, result_path = create_spedup(audio_path, output_path)
        if success:
            await interaction.followup.send(file=nextcord.File(result_path), ephemeral=True)
            await maybe_send_ad(interaction)
        else:
            await interaction.followup.send(f"❌ Error: {result_path}", ephemeral=True)
        os.remove(audio_path)
        os.remove(result_path)
    except Exception as e:
        await interaction.followup.send(f"❌ An error occurred: {e}", ephemeral=True)

def create_slowed(input_audio_path, output_audio_path):
    try:
        nc_audio = input_audio_path @ nc.Tones(-1)
        nc_audio.export(output_audio_path, format="mp3")
        return True, output_audio_path
    except Exception as e:
        print(f"An error occurred: {e}")
        return False, str(e)

# Slowed Command
@bot.slash_command(
    name="slowed",
    description="Converts an uploaded audio file into a Slowed version."
)
async def slowed_command(interaction: nextcord.Interaction, song: nextcord.Attachment):
    await interaction.response.defer()
    try:
        audio_path = f"temp/{song.filename}"
        await song.save(audio_path)
        if not audio_path.endswith(('.mp3', '.wav')):
            await interaction.followup.send("❌ Please upload a valid audio file (MP3, WAV).", ephemeral=True)
            return
        output_path = f"temp/slowed_{song.filename}"
        success, result_path = create_slowed(audio_path, output_path)
        
        if success:
            await interaction.followup.send(file=nextcord.File(result_path), ephemeral=True)
            await maybe_send_ad(interaction)
        else:
            await interaction.followup.send(f"❌ Error: {result_path}", ephemeral=True)
        os.remove(audio_path)
        os.remove(result_path)
    except Exception as e:
        await interaction.followup.send(f"❌ An error occurred: {e}", ephemeral=True)

@bot.slash_command(
    name="disableads",
    description="Disable promotional messages in this server",
)
async def disableads(interaction: nextcord.Interaction):
    if not (interaction.user.id == 977190163736322088 or 
            interaction.user == interaction.guild.owner or 
            interaction.user.guild_permissions.administrator):
        await interaction.response.send_message(
            "Only the server owner or administrators can disable ads.",
            ephemeral=True
        )
        return

    cursor = connection.cursor()
    cursor.execute("SELECT server_id FROM disableads_servers WHERE server_id = ?", (interaction.guild.id,))
    result = cursor.fetchone()
    
    if result:
        embed = nextcord.Embed(
            title="Already Disabled",
            description="Promotional messages are already disabled in this server!",
            color=0x2a2a2a
        )
    else:
        cursor.execute("INSERT INTO disableads_servers (server_id) VALUES (?)", (interaction.guild.id,))
        connection.commit()
        
        embed = nextcord.Embed(
            title="Ads Disabled", 
            description="Promotional messages have been disabled for this server!",
            color=0x2a2a2a
        )
    
    embed.set_footer(
        text="© Ryujin Bot (2023-2025) | Ads System",
        icon_url=RYUJIN_LOGO
    )

    embed.set_author(
        name="Ryujin",
        icon_url=RYUJIN_LOGO
    )
    await interaction.response.send_message(embed=embed, ephemeral=True)

@bot.slash_command(
    name="donate",
    description="Support the development of Ryujin"
)
async def donate(interaction: nextcord.Interaction):
    embed = nextcord.Embed(
        title="Support the development of Ryujin",
        description="If you want to support the development of Ryujin, you can donate by clicking the button below.",
        color=0x2a2a2a
    )
    embed.set_footer(
        text="© Ryujin Bot (2023-2025) | Donate System",
        icon_url=RYUJIN_LOGO
    )
    embed.set_author(
        name="Ryujin",
        icon_url=RYUJIN_LOGO
    )
    view = nextcord.ui.View()
    view.add_item(nextcord.ui.Button(label="Donate", url="https://ko-fi.com/ryujinsupport", style=nextcord.ButtonStyle.link))
    await interaction.response.send_message(embed=embed, view=view, ephemeral=True)

@bot.slash_command(
    name="bug",
    description="Report a bug to the Ryujin team"
)
async def bug(interaction: nextcord.Interaction):
    embed = nextcord.Embed(
        title="Report a bug to the Ryujin team",
        description="If you want to report a bug, you need to join the support server and report it in the `🐞〢bugs` channel.",
        color=0x2a2a2a
    )
    embed.set_footer(
        text="© Ryujin Bot (2023-2025) | Bug System",
        icon_url=RYUJIN_LOGO
    )
    embed.set_author(
        name="Ryujin",
        icon_url=RYUJIN_LOGO
    )
    view = nextcord.ui.View()
    view.add_item(nextcord.ui.Button(label="Support Server", url="https://discord.gg/FSjRSaJ4bt", style=nextcord.ButtonStyle.link))
    await interaction.response.send_message(embed=embed, view=view, ephemeral=True)

@bot.slash_command(
    name="apikey",
    description="Manage API keys for the Remove Background feature",
    guild_ids=[1060144274722787328]
)
async def apikey(
    interaction: nextcord.Interaction,
    action: str = nextcord.SlashOption(
        name="action",
        description="Action to perform",
        choices={"Add": "add", "Remove": "remove", "List": "list", "Test": "test"},
        required=True
    ),
    api_key: str = nextcord.SlashOption(
        name="api_key",
        description="API key to add/remove",
        required=False
    )
):
    if interaction.user.id not in [977190163736322088, 1286323016061685779]:
        embed = nextcord.Embed(
            title="Error",
            description="You don't have permission to use this command.",
            color=0xff0000
        )
        embed.set_footer(
            text="© Ryujin Bot (2023-2025) | Remove Background System",
            icon_url=RYUJIN_LOGO
        )
        embed.set_author(
            name="Ryujin",
            icon_url=RYUJIN_LOGO
        )
        await interaction.response.send_message(embed=embed, ephemeral=True)
        return

    try:
        cursor = connection.cursor()
        
        if action == "add":
            if not api_key:
                raise ValueError("API key is required for add action")
                
            cursor.execute(
                "INSERT INTO removebgapi (api_key) VALUES (%s)",
                (api_key,)
            )
            connection.commit()
            description = "API key has been added successfully."
            
        elif action == "remove":
            if api_key == "all":
                cursor.execute("DELETE FROM removebgapi")
                connection.commit()
                description = "All API keys have been removed successfully."
            else:
                if not api_key:
                    raise ValueError("API key is required for remove action")
                    
                cursor.execute(
                    "DELETE FROM removebgapi WHERE api_key = %s",
                    (api_key,)
                )
                connection.commit()
                description = "API key has been removed successfully."
            
        elif action == "list":
            cursor.execute("SELECT api_key FROM removebgapi")
            keys = cursor.fetchall()
            if keys:
                description = "Current API keys:\n"
                for key in keys:
                    description += f"• {key[0]}\n"
            else:
                description = "No API keys found."
        elif action == "test":
            if not api_key:
                raise ValueError("API key is required for testing")
                
            try:
                response = requests.get(
                    "https://api.developer.pixelcut.ai/v1/credits",
                    headers={
                        'Accept': 'application/json',
                        "X-API-Key": api_key
                    }
                )
                if response.status_code == 200:
                    credits = response.json().get("credits", "Unknown")
                    description = f"API key is valid. Credits remaining: {credits}"
                else:
                    description = "API key is invalid or expired"
            except:
                description = "Error testing API key"
        
        cursor.close()

        embed = nextcord.Embed(
            title="API Key Management",
            description=description,
            color=0x2a2a2a
        )
        embed.set_footer(
            text="© Ryujin Bot (2023-2025) | Remove Background System",
            icon_url=RYUJIN_LOGO
        )
        embed.set_author(
            name="Ryujin",
            icon_url=RYUJIN_LOGO
        )
        await interaction.response.send_message(embed=embed, ephemeral=True)
        
    except ValueError as ve:
        embed = nextcord.Embed(
            title="Error", 
            description=str(ve),
            color=0xff0000
        )
        embed.set_footer(
            text="© Ryujin Bot (2023-2025) | Remove Background System",
            icon_url=RYUJIN_LOGO
        )
        embed.set_author(
            name="Ryujin",
            icon_url=RYUJIN_LOGO
        )
        await interaction.response.send_message(embed=embed, ephemeral=True)
        
    except Error as e:
        embed = nextcord.Embed(
            title="Error",
            description=f"Database error: {str(e)}",
            color=0xff0000
        )
        embed.set_footer(
            text="© Ryujin Bot (2023-2025) | Remove Background System",
            icon_url=RYUJIN_LOGO
        )
        embed.set_author(
            name="Ryujin",
            icon_url=RYUJIN_LOGO
        )
        await interaction.response.send_message(embed=embed, ephemeral=True)

@bot.slash_command(
    name="compress_file",
    description="Compress a file to reduce its size while maintaining quality"
)
async def compress_file(interaction: nextcord.Interaction, file: nextcord.Attachment):
    await interaction.response.defer(ephemeral=True)
    
    try:
        if not os.path.exists('temp'):
            os.makedirs('temp')
            
        input_path = f"temp/{file.filename}"
        await file.save(input_path)
        
        file_ext = os.path.splitext(file.filename)[1].lower()
        output_path = f"temp/compressed_{file.filename}"
        
        if file_ext in ['.mp4', '.mov', '.avi', '.mkv', '.webm']:

            ffmpeg_cmd = [
                'ffmpeg', '-i', input_path,
                '-c:v', 'libx264', '-crf', '23',
                '-preset', 'medium',
                '-c:a', 'aac', '-b:a', '128k',
                output_path
            ]
            subprocess.run(ffmpeg_cmd, check=True)
            
        elif file_ext in ['.jpg', '.jpeg', '.png', '.webp']:
            with Image.open(input_path) as img:
                if file_ext in ['.jpg', '.jpeg']:
                    img.save(output_path, 'JPEG', quality=85, optimize=True)
                elif file_ext == '.png':
                    img.save(output_path, 'PNG', optimize=True)
                elif file_ext == '.webp':
                    img.save(output_path, 'WEBP', quality=85)
                    
        elif file_ext in ['.mp3', '.wav', '.m4a', '.ogg']:

            ffmpeg_cmd = [
                'ffmpeg', '-i', input_path,
                '-c:a', 'libmp3lame', '-b:a', '192k',
                output_path
            ]
            subprocess.run(ffmpeg_cmd, check=True)
            
        elif file_ext in ['.pdf']:
            gs_cmd = [
                'gs', '-sDEVICE=pdfwrite', '-dCompatibilityLevel=1.4',
                '-dPDFSETTINGS=/ebook', '-dNOPAUSE', '-dQUIET', '-dBATCH',
                f'-sOutputFile={output_path}', input_path
            ]
            subprocess.run(gs_cmd, check=True)
            
        elif file_ext in ['.zip', '.rar', '.7z']:
            seven_zip_cmd = [
                '7z', 'a', '-mx=9', output_path, input_path
            ]
            subprocess.run(seven_zip_cmd, check=True)
            
        else:
            await interaction.followup.send("❌ Unsupported file format. Supported formats: video, image, audio, PDF, and archives.", ephemeral=True)
            return
            
        original_size = os.path.getsize(input_path)
        compressed_size = os.path.getsize(output_path)
        reduction = ((original_size - compressed_size) / original_size) * 100
        
        await interaction.followup.send(
            f"✅ File compressed successfully!\n"
            f"Original size: {original_size/1024/1024:.2f} MB\n"
            f"Compressed size: {compressed_size/1024/1024:.2f} MB\n"
            f"Size reduction: {reduction:.1f}%",
            file=nextcord.File(output_path),
            ephemeral=True
        )
        await maybe_send_ad(interaction)
        
    except Exception as e:
        await interaction.followup.send(f"❌ An error occurred: {str(e)}", ephemeral=True)
        
    finally:
        try:
            if os.path.exists(input_path):
                os.remove(input_path)
            if os.path.exists(output_path):
                os.remove(output_path)
        except:
            pass
@bot.slash_command(
    name="resize_video",
    description="Resize a video to a specific resolution while maintaining aspect ratio"
)
async def resize_video(
    interaction: nextcord.Interaction,
    video: nextcord.Attachment,
    width: int = SlashOption(description="Target width in pixels", required=True),
    height: int = SlashOption(description="Target height in pixels", required=True)
):
    if not video.filename.lower().endswith(('.mp4', '.mov', '.avi', '.mkv')):
        await interaction.response.send_message("❌ Please provide a valid video file.", ephemeral=True)
        return

    await interaction.response.defer(ephemeral=True)
    
    try:
        input_path = f"temp/{uuid.uuid4()}_{video.filename}"
        output_path = f"temp/resized_{uuid.uuid4()}_{video.filename}"
        
        await video.save(input_path)
        
        ffmpeg_cmd = [
            'ffmpeg', '-i', input_path,
            '-vf', f'scale={width}:{height}:force_original_aspect_ratio=decrease,pad={width}:{height}:(ow-iw)/2:(oh-ih)/2',
            '-c:a', 'copy',
            output_path
        ]
        
        subprocess.run(ffmpeg_cmd, check=True)
        
        original_size = os.path.getsize(input_path)
        resized_size = os.path.getsize(output_path)
        
        await interaction.followup.send(
            f"✅ Video resized successfully!\n"
            f"Original size: {original_size/1024/1024:.2f} MB\n"
            f"Resized size: {resized_size/1024/1024:.2f} MB\n"
            f"New resolution: {width}x{height}",
            file=nextcord.File(output_path),
            ephemeral=True
        )
        await maybe_send_ad(interaction)
        
    except Exception as e:
        await interaction.followup.send(f"❌ An error occurred: {str(e)}", ephemeral=True)
        
    finally:
        try:
            if os.path.exists(input_path):
                os.remove(input_path)
            if os.path.exists(output_path):
                os.remove(output_path)
        except:
            pass

@bot.slash_command(
    name="cut_audio",
    description="Cut an audio file to a specific duration"
)
async def cut_audio(
    interaction: nextcord.Interaction,
    audio: nextcord.Attachment,
    start_time: str = SlashOption(description="Start time (format: 0:00)", required=True),
    end_time: str = SlashOption(description="End time (format: 0:00)", required=True)
):
    if not audio.filename.lower().endswith(('.mp3', '.wav', '.m4a', '.ogg')):
        await interaction.response.send_message("❌ Please provide a valid audio file.", ephemeral=True)
        return

    try:
        def time_to_seconds(time_str):
            parts = time_str.split(':')
            if len(parts) == 2:
                minutes, seconds = map(int, parts)
                return minutes * 60 + seconds
            else:
                raise ValueError
                
        start_seconds = time_to_seconds(start_time)
        end_seconds = time_to_seconds(end_time)
    except:
        await interaction.response.send_message("❌ Invalid time format. Please use format 0:00", ephemeral=True)
        return

    if start_seconds >= end_seconds:
        await interaction.response.send_message("❌ Start time must be less than end time.", ephemeral=True)
        return

    await interaction.response.defer(ephemeral=True)
    
    try:
        input_path = f"temp/{uuid.uuid4()}_{audio.filename}"
        output_path = f"temp/cut_{uuid.uuid4()}_{audio.filename}"
        
        await audio.save(input_path)
        
        ffmpeg_cmd = [
            'ffmpeg', '-i', input_path,
            '-ss', str(start_seconds), 
            '-to', str(end_seconds),
            '-acodec', 'copy',
            output_path
        ]

        subprocess.run(ffmpeg_cmd, check=True)
        
        original_size = os.path.getsize(input_path)
        cut_size = os.path.getsize(output_path)
        
        duration = end_seconds - start_seconds
        
        await interaction.followup.send(
            f"✅ Audio cut successfully!\n"
            f"Duration: {duration} seconds\n"
            f"Original size: {original_size/1024/1024:.2f} MB\n"
            f"Cut size: {cut_size/1024/1024:.2f} MB",
            file=nextcord.File(output_path),
            ephemeral=True
        )
        await maybe_send_ad(interaction)
        
    except Exception as e:
        await interaction.followup.send(f"❌ An error occurred: {str(e)}", ephemeral=True)
        
    finally:
        try:
            if os.path.exists(input_path):
                os.remove(input_path)
            if os.path.exists(output_path):
                os.remove(output_path)
        except:
            pass


bot.run(TOKEN)