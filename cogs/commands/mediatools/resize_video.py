import nextcord
from nextcord.ext import commands
import os
import subprocess
import uuid

class ResizeVideoCog(commands.Cog):
    def __init__(self, bot):
        self.bot = bot
        self.RYUJIN_LOGO = "https://cdn.discordapp.com/avatars/1059400568805785620/63a77f852ea29f37961f458c53fb5a97.png"

    @nextcord.slash_command(
        name="resize_video",
        description="Resize a video to a specific resolution while maintaining aspect ratio"
    )
    async def resize_video(
        self, 
        interaction: nextcord.Interaction,
        video: nextcord.Attachment,
        width: int = nextcord.SlashOption(description="Target width in pixels", required=True),
        height: int = nextcord.SlashOption(description="Target height in pixels", required=True)
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
    bot.add_cog(ResizeVideoCog(bot)) 