import nextcord
from nextcord.ext import commands
from datetime import datetime

class ReverseTextCog(commands.Cog):
    def __init__(self, bot):
        self.bot = bot
        self.RYUJIN_LOGO = "https://cdn.discordapp.com/avatars/1059400568805785620/63a77f852ea29f37961f458c53fb5a97.png"

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

    def reverse_text(self, text):
        """Reverse the text completely"""
        return text[::-1]

    def reverse_words(self, text):
        """Reverse the order of words"""
        words = text.split()
        return ' '.join(words[::-1])

    def reverse_letters(self, text):
        """Reverse letters in each word but keep word order"""
        words = text.split()
        reversed_words = [word[::-1] for word in words]
        return ' '.join(reversed_words)

    def flip_case(self, text):
        """Flip the case of each character"""
        return text.swapcase()

    def upside_down(self, text):
        """Convert text to upside down characters"""
        upside_down_chars = {
            'a': 'ɐ', 'b': 'q', 'c': 'ɔ', 'd': 'p', 'e': 'ǝ', 'f': 'ɟ', 'g': 'ƃ', 'h': 'ɥ',
            'i': 'ᴉ', 'j': 'ɾ', 'k': 'ʞ', 'l': 'l', 'm': 'ɯ', 'n': 'u', 'o': 'o', 'p': 'd',
            'q': 'b', 'r': 'ɹ', 's': 's', 't': 'ʇ', 'u': 'n', 'v': 'ʌ', 'w': 'ʍ', 'x': 'x',
            'y': 'ʎ', 'z': 'z',
            'A': '∀', 'B': 'B', 'C': 'Ɔ', 'D': 'D', 'E': 'Ǝ', 'F': 'Ⅎ', 'G': 'פ', 'H': 'H',
            'I': 'I', 'J': 'ſ', 'K': 'K', 'L': '˥', 'M': 'W', 'N': 'N', 'O': 'O', 'P': 'Ԁ',
            'Q': 'Q', 'R': 'R', 'S': 'S', 'T': '┴', 'U': '∩', 'V': 'Λ', 'W': 'M', 'X': 'X',
            'Y': '⅄', 'Z': 'Z',
            '0': '0', '1': 'Ɩ', '2': 'ᄅ', '3': 'Ɛ', '4': 'ㄣ', '5': 'ϛ', '6': '9', '7': 'ㄥ',
            '8': '8', '9': '6',
            ',': '\'', '.': '˙', '?': '¿', '!': '¡', '(': ')', ')': '(', '[': ']', ']': '[',
            '{': '}', '}': '{', '<': '>', '>': '<', '&': '⅋', '_': '‾', '∴': '∵', '⁅': '⁆',
            '∦': '∣', '⁀': '⁁', '⁂': '⁂', '⁃': '⁃', '⁄': '⁄', '⁅': '⁆', '⁆': '⁅', '⁇': '⁇',
            '⁈': '⁈', '⁉': '⁉', '‼': '‼', '⁎': '⁎', '⁏': '⁏', '⁐': '⁐', '⁑': '⁑', '⁒': '⁒',
            '⁓': '⁓', '⁔': '⁔', '⁕': '⁕', '⁖': '⁖', '⁗': '⁗', '⁘': '⁘', '⁙': '⁙', '⁚': '⁚',
            '⁛': '⁛', '⁜': '⁜', '⁝': '⁝', '⁞': '⁞'
        }
        
        result = ""
        for char in text:
            result += upside_down_chars.get(char, char)
        return result

    @nextcord.slash_command(
        name="reversetext",
        description="Reverse text in various ways! 🔄"
    )
    async def reversetext(
        self,
        interaction: nextcord.Interaction,
        text: str = nextcord.SlashOption(
            description="Text to reverse",
            required=True
        ),
        mode: str = nextcord.SlashOption(
            choices=["complete", "words", "letters", "case", "upside_down"],
            description="How to reverse the text",
            required=False,
            default="complete"
        )
    ):
        if self.check_blacklist(interaction.user.id):
            embed = self.create_blacklist_embed(self.bot.blacklist[interaction.user.id])
            await interaction.response.send_message(embed=embed, ephemeral=True)
            return

        if not text.strip():
            await interaction.response.send_message(
                "❌ Text cannot be empty!",
                ephemeral=True
            )
            return

        if len(text) > 1000:
            await interaction.response.send_message(
                "❌ Text is too long! Maximum 1000 characters allowed.",
                ephemeral=True
            )
            return

        if mode == "complete":
            result = self.reverse_text(text)
            mode_name = "Complete Reverse"
            emoji = "🔄"
        elif mode == "words":
            result = self.reverse_words(text)
            mode_name = "Word Order Reverse"
            emoji = "📝"
        elif mode == "letters":
            result = self.reverse_letters(text)
            mode_name = "Letter Reverse"
            emoji = "🔤"
        elif mode == "case":
            result = self.flip_case(text)
            mode_name = "Case Flip"
            emoji = "🔄"
        elif mode == "upside_down":
            result = self.upside_down(text)
            mode_name = "Upside Down"
            emoji = "🙃"
        else:
            result = self.reverse_text(text)
            mode_name = "Complete Reverse"
            emoji = "🔄"

        embed = nextcord.Embed(
            title=f"{emoji} **Text Reversed!**",
            description=f"Successfully reversed your text using **{mode_name}** mode!",
            color=0x2a2a2a
        )
        
        embed.add_field(
            name="📝 Original Text",
            value=f"```{text}```",
            inline=False
        )
        
        embed.add_field(
            name="🔄 Reversed Text",
            value=f"```{result}```",
            inline=False
        )
        
        embed.add_field(
            name="🎯 Mode Used",
            value=f"```{mode_name}```",
            inline=True
        )
        
        embed.add_field(
            name="📊 Character Count",
            value=f"**Original:** {len(text)} | **Reversed:** {len(result)}",
            inline=True
        )
        
        if mode in ["words", "letters"]:
            word_count = len(text.split())
            embed.add_field(
                name="📋 Word Count",
                value=f"```{word_count} words```",
                inline=True
            )
        
        embed.add_field(
            name="⏰ Reverse Time",
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
        name="reversetext_all",
        description="Reverse text in all possible ways! 🎭"
    )
    async def reversetext_all(
        self,
        interaction: nextcord.Interaction,
        text: str = nextcord.SlashOption(
            description="Text to reverse in all ways",
            required=True
        )
    ):
        if self.check_blacklist(interaction.user.id):
            embed = self.create_blacklist_embed(self.bot.blacklist[interaction.user.id])
            await interaction.response.send_message(embed=embed, ephemeral=True)
            return

        if not text.strip():
            await interaction.response.send_message(
                "❌ Text cannot be empty!",
                ephemeral=True
            )
            return

        if len(text) > 500:
            await interaction.response.send_message(
                "❌ Text is too long for all modes! Maximum 500 characters allowed.",
                ephemeral=True
            )
            return

        complete_reverse = self.reverse_text(text)
        word_reverse = self.reverse_words(text)
        letter_reverse = self.reverse_letters(text)
        case_flip = self.flip_case(text)
        upside_down = self.upside_down(text)

        embed = nextcord.Embed(
            title="🎭 **All Text Reversals!**",
            description="Here are all the different ways your text can be reversed!",
            color=0x2a2a2a
        )
        
        embed.add_field(
            name="📝 Original Text",
            value=f"```{text}```",
            inline=False
        )
        
        embed.add_field(
            name="🔄 Complete Reverse",
            value=f"```{complete_reverse}```",
            inline=False
        )
        
        embed.add_field(
            name="📝 Word Order Reverse",
            value=f"```{word_reverse}```",
            inline=False
        )
        
        embed.add_field(
            name="🔤 Letter Reverse",
            value=f"```{letter_reverse}```",
            inline=False
        )
        
        embed.add_field(
            name="🔄 Case Flip",
            value=f"```{case_flip}```",
            inline=False
        )
        
        embed.add_field(
            name="🙃 Upside Down",
            value=f"```{upside_down}```",
            inline=False
        )
        
        embed.add_field(
            name="📊 Text Statistics",
            value=f"**Characters:** {len(text)} | **Words:** {len(text.split())}",
            inline=True
        )
        
        embed.add_field(
            name="🎯 Modes Available",
            value=f"```5 different modes```",
            inline=True
        )
        
        embed.add_field(
            name="⏰ Process Time",
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
    bot.add_cog(ReverseTextCog(bot)) 