import nextcord
from nextcord.ext import commands
import os
import subprocess
from PIL import Image

class CompressFileCog(commands.Cog):
    def __init__(self, bot):
        self.bot = bot
        self.RYUJIN_LOGO = "https://cdn.discordapp.com/avatars/1059400568805785620/63a77f852ea29f37961f458c53fb5a97.png"

    @nextcord.slash_command(
        name="compress_file",
        description="Compress a file to reduce its size while maintaining quality"
    )
    async def compress_file(self, interaction: nextcord.Interaction, file: nextcord.Attachment):
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
            await self.bot.maybe_send_ad(interaction)
            
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

def setup(bot):
    bot.add_cog(CompressFileCog(bot)) 