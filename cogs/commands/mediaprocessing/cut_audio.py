import nextcord
from nextcord.ext import commands
import os
import subprocess
import uuid

class CutAudioCog(commands.Cog):
    def __init__(self, bot):
        self.bot = bot
        self.RYUJIN_LOGO = "https://cdn.discordapp.com/avatars/1059400568805785620/63a77f852ea29f37961f458c53fb5a97.png"

    @nextcord.slash_command(
        name="cut_audio",
        description="Cut an audio file to a specific duration"
    )
    async def cut_audio(
        self,
        interaction: nextcord.Interaction,
        audio: nextcord.Attachment,
        start_time: str = nextcord.SlashOption(description="Start time (format: 0:00)", required=True),
        end_time: str = nextcord.SlashOption(description="End time (format: 0:00)", required=True)
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
            if not os.path.exists('temp'):
                os.makedirs('temp')
                
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
    bot.add_cog(CutAudioCog(bot)) 