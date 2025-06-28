import nextcord
from nextcord.ext import commands
import re
from datetime import datetime

class MorseCog(commands.Cog):
    def __init__(self, bot):
        self.bot = bot
        self.RYUJIN_LOGO = "https://cdn.discordapp.com/avatars/1059400568805785620/63a77f852ea29f37961f458c53fb5a97.png"
        
        self.morse_dict = {
            'A': '.-', 'B': '-...', 'C': '-.-.', 'D': '-..', 'E': '.', 'F': '..-.',
            'G': '--.', 'H': '....', 'I': '..', 'J': '.---', 'K': '-.-', 'L': '.-..',
            'M': '--', 'N': '-.', 'O': '---', 'P': '.--.', 'Q': '--.-', 'R': '.-.',
            'S': '...', 'T': '-', 'U': '..-', 'V': '...-', 'W': '.--', 'X': '-..-',
            'Y': '-.--', 'Z': '--..',
            '0': '-----', '1': '.----', '2': '..---', '3': '...--', '4': '....-',
            '5': '.....', '6': '-....', '7': '--...', '8': '---..', '9': '----.',
            '.': '.-.-.-', ',': '--..--', '?': '..--..', '!': '-.-.--', ';': '-.-.-.',
            ':': '---...', '-': '-....-', '/': '-..-.', '(': '-.--.', ')': '-.--.-',
            '&': '.-...', '=': '-...-', '+': '.-.-.', '_': '..--.-', '"': '.-..-.',
            '$': '...-..-', '@': '.--.-.', ' ': ' '
        }
        
        self.reverse_morse = {v: k for k, v in self.morse_dict.items()}

    def check_blacklist(self, user_id):
        """Check if user is blacklisted"""
        return user_id in self.bot.blacklist

    def create_blacklist_embed(self, reason):
        """Create blacklist embed"""
        embed = nextcord.Embed(
            title="You are blacklisted!",
            description=f"**You can't use Ryujin's functions anymore because you have been blacklisted for `{reason}`.**",
            color=nextcord.Color.red()
        )
        embed.set_footer(text="© Ryujin Bot (2023-2025) | Blacklist System")
        embed.set_author(
            name="Ryujin",
            icon_url=self.RYUJIN_LOGO
        )
        return embed

    def text_to_morse(self, text):
        """Convert text to morse code"""
        morse_result = []
        for char in text.upper():
            if char in self.morse_dict:
                morse_result.append(self.morse_dict[char])
            else:
                morse_result.append('?')
        return ' '.join(morse_result)

    def morse_to_text(self, morse_code):
        """Convert morse code to text"""
        morse_parts = re.split(r'\s+', morse_code.strip())
        text_result = []
        
        for part in morse_parts:
            if part in self.reverse_morse:
                text_result.append(self.reverse_morse[part])
            elif part == '':
                text_result.append(' ')
            else:
                text_result.append('?')
        
        return ''.join(text_result)

    def is_morse_code(self, text):
        """Check if text looks like morse code"""
        morse_chars = set('.- ')
        return all(char in morse_chars for char in text)

    @nextcord.slash_command(
        name="morse",
        description="Convert text to morse code and vice versa! 📡"
    )
    async def morse(
        self,
        interaction: nextcord.Interaction,
        text: str = nextcord.SlashOption(
            description="Text to convert (or morse code to decode)",
            required=True
        )
    ):
        if self.check_blacklist(interaction.user.id):
            embed = self.create_blacklist_embed(self.bot.blacklist[interaction.user.id])
            await interaction.response.send_message(embed=embed, ephemeral=True)
            return

        is_morse = self.is_morse_code(text)
        
        if is_morse:
            result = self.morse_to_text(text)
            operation = "Decoded"
            input_type = "Morse Code"
            output_type = "Plain Text"
            color = 0x00FF00
            emoji = "📡"
        else:
            result = self.text_to_morse(text)
            operation = "Encoded"
            input_type = "Plain Text"
            output_type = "Morse Code"
            color = 0x2a2a2a
            emoji = "🔤"

        embed = nextcord.Embed(
            title=f"{emoji} **Morse Code {operation}**",
            description=f"Successfully {operation.lower()} your message!",
            color=color
        )
        
        embed.add_field(
            name=f"📝 {input_type}",
            value=f"```{text}```",
            inline=False
        )
        
        embed.add_field(
            name=f"📡 {output_type}",
            value=f"```{result}```",
            inline=False
        )
        
        embed.add_field(
            name="📊 Character Count",
            value=f"**Input:** {len(text)} | **Output:** {len(result)}",
            inline=True
        )
        
        embed.add_field(
            name="🔄 Operation",
            value=f"```{operation}```",
            inline=True
        )
        
        embed.add_field(
            name="⏰ Conversion Time",
            value=f"<t:{int(datetime.now().timestamp())}:R>",
            inline=False
        )
        
        embed.set_footer(
            text="© Ryujin Bot (2023-2025) | Fun System",
            icon_url=self.RYUJIN_LOGO
        )
        embed.set_author(
            name=f"{interaction.user.name}",
            icon_url=interaction.user.display_avatar.url
        )

        await interaction.response.send_message(embed=embed)
        
        await self.bot.maybe_send_ad(interaction)

    @nextcord.slash_command(
        name="morse_encode",
        description="Encode text to morse code! 🔤"
    )
    async def morse_encode(
        self,
        interaction: nextcord.Interaction,
        text: str = nextcord.SlashOption(
            description="Text to encode to morse code",
            required=True
        )
    ):
        if self.check_blacklist(interaction.user.id):
            embed = self.create_blacklist_embed(self.bot.blacklist[interaction.user.id])
            await interaction.response.send_message(embed=embed, ephemeral=True)
            return

        morse_result = self.text_to_morse(text)
        
        embed = nextcord.Embed(
            title="🔤 **Text to Morse Code**",
            description="Your text has been encoded to morse code!",
            color=0x2a2a2a
        )
        
        embed.add_field(
            name="📝 Original Text",
            value=f"```{text}```",
            inline=False
        )
        
        embed.add_field(
            name="📡 Morse Code",
            value=f"```{morse_result}```",
            inline=False
        )
        
        char_count = len(text)
        word_count = len(text.split())
        embed.add_field(
            name="📊 Text Analysis",
            value=f"**Characters:** {char_count} | **Words:** {word_count}",
            inline=True
        )
        
        unique_chars = len(set(text.upper()))
        embed.add_field(
            name="🔤 Unique Characters",
            value=f"```{unique_chars}```",
            inline=True
        )
        
        embed.add_field(
            name="⏰ Encode Time",
            value=f"<t:{int(datetime.now().timestamp())}:R>",
            inline=False
        )
        
        embed.set_footer(
            text="© Ryujin Bot (2023-2025) | Fun System",
            icon_url=self.RYUJIN_LOGO
        )
        embed.set_author(
            name=f"{interaction.user.name}",
            icon_url=interaction.user.display_avatar.url
        )

        await interaction.response.send_message(embed=embed)
        
        await self.bot.maybe_send_ad(interaction)

    @nextcord.slash_command(
        name="morse_decode",
        description="Decode morse code to text! 📡"
    )
    async def morse_decode(
        self,
        interaction: nextcord.Interaction,
        morse_code: str = nextcord.SlashOption(
            description="Morse code to decode",
            required=True
        )
    ):
        if self.check_blacklist(interaction.user.id):
            embed = self.create_blacklist_embed(self.bot.blacklist[interaction.user.id])
            await interaction.response.send_message(embed=embed, ephemeral=True)
            return

        text_result = self.morse_to_text(morse_code)
        
        embed = nextcord.Embed(
            title="📡 **Morse Code to Text**",
            description="Your morse code has been decoded!",
            color=0x00FF00
        )
        
        embed.add_field(
            name="📡 Morse Code",
            value=f"```{morse_code}```",
            inline=False
        )
        
        embed.add_field(
            name="📝 Decoded Text",
            value=f"```{text_result}```",
            inline=False
        )
        
        morse_length = len(morse_code)
        dots_count = morse_code.count('.')
        dashes_count = morse_code.count('-')
        spaces_count = morse_code.count(' ')
        
        embed.add_field(
            name="📊 Morse Analysis",
            value=f"**Length:** {morse_length} | **Dots:** {dots_count} | **Dashes:** {dashes_count}",
            inline=True
        )
        
        embed.add_field(
            name="🔤 Spaces",
            value=f"```{spaces_count}```",
            inline=True
        )
        
        embed.add_field(
            name="⏰ Decode Time",
            value=f"<t:{int(datetime.now().timestamp())}:R>",
            inline=False
        )
        
        embed.set_footer(
            text="© Ryujin Bot (2023-2025) | Fun System",
            icon_url=self.RYUJIN_LOGO
        )
        embed.set_author(
            name=f"{interaction.user.name}",
            icon_url=interaction.user.display_avatar.url
        )

        await interaction.response.send_message(embed=embed)
        
        await self.bot.maybe_send_ad(interaction)

def setup(bot):
    bot.add_cog(MorseCog(bot)) 