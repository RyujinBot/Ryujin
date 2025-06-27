import nextcord
from nextcord.ext import commands
import os
import nightcore as nc

class SlowedCog(commands.Cog):
    def __init__(self, bot):
        self.bot = bot
        self.RYUJIN_LOGO = "https://cdn.discordapp.com/avatars/1059400568805785620/63a77f852ea29f37961f458c53fb5a97.png"

    def create_slowed(self, input_audio_path, output_audio_path):
        try:
            nc_audio = input_audio_path @ nc.Tones(-1)
            nc_audio.export(output_audio_path, format="mp3")
            return True, output_audio_path
        except Exception as e:
            print(f"An error occurred: {e}")
            return False, str(e)

    @nextcord.slash_command(
        name="slowed",
        description="Converts an uploaded audio file into a Slowed version."
    )
    async def slowed_command(self, interaction: nextcord.Interaction, song: nextcord.Attachment):
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

        await interaction.response.defer()
        
        try:
            if not os.path.exists('temp'):
                os.makedirs('temp')
                
            audio_path = f"temp/{song.filename}"
            await song.save(audio_path)
            
            if not audio_path.endswith(('.mp3', '.wav')):
                await interaction.followup.send("❌ Please upload a valid audio file (MP3, WAV).", ephemeral=True)
                return
                
            output_path = f"temp/slowed_{song.filename}"
            success, result_path = self.create_slowed(audio_path, output_path)
            
            if success:
                await interaction.followup.send(file=nextcord.File(result_path), ephemeral=True)
                await self.bot.maybe_send_ad(interaction)
            else:
                await interaction.followup.send(f"❌ Error: {result_path}", ephemeral=True)
                
        except Exception as e:
            await interaction.followup.send(f"❌ An error occurred: {e}", ephemeral=True)
            
        finally:
            try:
                if os.path.exists(audio_path):
                    os.remove(audio_path)
                if os.path.exists(output_path):
                    os.remove(output_path)
            except:
                pass

def setup(bot):
    bot.add_cog(SlowedCog(bot)) 