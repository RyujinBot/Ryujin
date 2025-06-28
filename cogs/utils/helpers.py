import os
import random
import asyncio
import nextcord

def count_files(folder):
    """Count all files in a folder recursively"""
    count = 0
    for root, _, files in os.walk(folder):
        count += len(files)
    return count

def generate_hashtags(character, anime):
    """Generate hashtags for anime/character"""
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

async def handle_pagination(message, pages, bot):
    """Handle pagination for embeds"""
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

class AnotherButtonEdit(nextcord.ui.View):
    """Button view for another edit"""
    def __init__(self, maybe_send_ad_func):
        super().__init__()
        self.maybe_send_ad = maybe_send_ad_func
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
        await self.maybe_send_ad(interaction)

class AnotherButton(nextcord.ui.View):
    """Button view for another overlay"""
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

class GenerateHashtagsModal(nextcord.ui.Modal):
    """Modal for generating hashtags"""
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
            icon_url="https://cdn.discordapp.com/avatars/1059400568805785620/63a77f852ea29f37961f458c53fb5a97.png"
        )

        await interaction.response.send_message(embed=embed, ephemeral=True) 