import nextcord
from nextcord.ext import commands
import os
import subprocess
# from moviepy.editor import VideoFileClip, AudioFileClip
from PIL import Image
import re

class ConvertCog(commands.Cog):
    def __init__(self, bot):
        self.bot = bot
        self.RYUJIN_LOGO = "https://cdn.discordapp.com/avatars/1059400568805785620/63a77f852ea29f37961f458c53fb5a97.png"

    def sanitize_filename(self, filename):
        """Remove invalid characters from filename"""
        return re.sub(r'[<>:"/\\|?*]', '', filename)

    @nextcord.slash_command(
        name="convert",
        description="Convert a file from one format to another.",
    )
    async def convert(
        self, 
        interaction: nextcord.Interaction, 
        from_format: str = nextcord.SlashOption(
            choices=["MP4", "MKV", "MOV", "AVI", "MP3", "WAV", "M4A", "PNG", "JPG", "JPEG", "SVG", "WEBP", "ICO"],
            description="Source format"
        ),
        to_format: str = nextcord.SlashOption(
            choices=["MP4", "MKV", "MOV", "AVI", "MP3", "WAV", "M4A", "PNG", "JPG", "JPEG", "SVG", "WEBP", "ICO"],
            description="Target format"
        ),
        file: nextcord.Attachment = nextcord.SlashOption(description="File to convert", required=True)
    ):
        user_id = interaction.user.id
        if hasattr(self.bot, 'blacklist') and user_id in self.bot.blacklist:
            embed = nextcord.Embed(
                title="You are blacklisted!",
                description=f"**You can't use Ryujin's commands anymore because you have been blacklisted for `{self.bot.blacklist[user_id]}`.**",
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
            await interaction.send(embed=embed, ephemeral=True)
            return

        await interaction.response.defer(ephemeral=True)
        
        try:
            if not os.path.exists('temp'):
                os.makedirs('temp')
                
            await file.save(f"temp/{file.filename}")
            input_file = f"temp/{file.filename}"
            base_name = os.path.splitext(file.filename)[0]
            output_file = f"temp/{self.sanitize_filename(base_name)}.{to_format.lower()}"

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
            await self.bot.maybe_send_ad(interaction)
            
        except Exception as e:
            await interaction.followup.send(f"An error occurred: {e}", ephemeral=True)
            
        finally:
            try:
                if os.path.exists(input_file):
                    os.remove(input_file)
                if os.path.exists(output_file):
                    os.remove(output_file)
            except:
                pass

def setup(bot):
    bot.add_cog(ConvertCog(bot)) 