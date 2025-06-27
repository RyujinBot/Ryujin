import nextcord
from nextcord.ext import commands
from cogs.utils.helpers import GenerateHashtagsModal
from cogs.utils.embeds import create_blacklist_embed

class GenerateTagsCog(commands.Cog):
    def __init__(self, bot):
        self.bot = bot
        self.RYUJIN_LOGO = "https://cdn.discordapp.com/avatars/1059400568805785620/63a77f852ea29f37961f458c53fb5a97.png"

    @nextcord.slash_command(
        name="generatetags",
        description="Generate hashtags for anime/character"
    )
    async def generatetags(self, interaction: nextcord.Interaction):
        """Generate hashtags for anime/character"""
        if interaction.user.id in self.bot.blacklist:
            embed = create_blacklist_embed(interaction.user.id, self.bot.blacklist[interaction.user.id])
            await interaction.response.send_message(embed=embed, ephemeral=True)
            return

        modal = GenerateHashtagsModal(self.bot)
        await interaction.response.send_modal(modal)
        await self.bot.maybe_send_ad(interaction)

    def generate_hashtags(self, character, anime):
        base_tags = [
            "anime", "amv", "edit", "animeedit",
            f"{anime.replace(' ', '').lower()}",
            f"{anime.replace(' ', '').lower()}edit",
            f"{character.replace(' ', '').lower()}" if character else "",
            f"{character.replace(' ', '').lower()}shortamv" if character else "",
            f"{character.replace(' ', '').lower()}shortedit" if character else "",
            f"{character.replace(' ', '').lower()}edit" if character else "",
            f"{character.replace(' ', '').lower()}amv" if character else "",
            f"{character.replace(' ', '').lower()}editamv" if character else "",
            f"{anime.replace(' ', '').lower()}shortedit",
            f"{anime.replace(' ', '').lower()}shortamv",
            f"{anime.replace(' ', '').lower()}editamv",
            f"{anime.replace(' ', '').lower()}shorteditamv",
            f"{anime.replace(' ', '').lower()}amv",
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

def setup(bot):
    bot.add_cog(GenerateTagsCog(bot)) 