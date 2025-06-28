import nextcord
from nextcord.ext import commands
import random
from datetime import datetime

class EightBallCog(commands.Cog):
    def __init__(self, bot):
        self.bot = bot
        self.RYUJIN_LOGO = "https://cdn.discordapp.com/avatars/1059400568805785620/63a77f852ea29f37961f458c53fb5a97.png"
        
        self.positive_responses = [
            "🎯 **It is certain!**",
            "✨ **Without a doubt!**",
            "🌟 **Yes, definitely!**",
            "💫 **You may rely on it!**",
            "👑 **As I see it, yes!**",
            "⭐ **Most likely!**",
            "🔮 **Outlook good!**",
            "🎉 **Yes!**",
            "💎 **Signs point to yes!**"
        ]
        
        self.negative_responses = [
            "❌ **Don't count on it!**",
            "🚫 **My reply is no!**",
            "😔 **My sources say no!**",
            "🌙 **Outlook not so good!**",
            "💔 **Very doubtful!**",
            "⚡ **No way!**",
            "🚷 **Not a chance!**",
            "💀 **Absolutely not!**",
            "🔥 **Better not tell you now!**"
        ]
        
        self.neutral_responses = [
            "🤔 **Reply hazy, try again!**",
            "🌀 **Ask again later!**",
            "🎭 **Cannot predict now!**",
            "🔮 **Concentrate and ask again!**",
            "✨ **Better not tell you now!**",
            "🌊 **Ask again later!**",
            "🎪 **Cannot predict now!**",
            "💫 **Reply hazy, try again!**",
            "🌟 **Concentrate and ask again!**"
        ]

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

    @nextcord.slash_command(
        name="8ball",
        description="Ask the mystical 8-ball for guidance! 🔮"
    )
    async def eightball(
        self,
        interaction: nextcord.Interaction,
        question: str = nextcord.SlashOption(
            description="What would you like to ask the 8-ball?",
            required=True
        )
    ):
        if self.check_blacklist(interaction.user.id):
            embed = self.create_blacklist_embed(self.bot.blacklist[interaction.user.id])
            await interaction.response.send_message(embed=embed, ephemeral=True)
            return

        thinking_embed = nextcord.Embed(
            title="🔮 **Consulting the 8-Ball...**",
            description="The mystical forces are gathering... ✨",
            color=0x2a2a2a
        )
        thinking_embed.add_field(
            name="❓ Your Question",
            value=f"```{question}```",
            inline=False
        )
        thinking_embed.add_field(
            name="⏱️ Consultation Time",
            value="```2 seconds```",
            inline=True
        )
        thinking_embed.set_footer(
            text="© Ryujin Bot (2023-2025) | Fun System",
            icon_url=self.RYUJIN_LOGO
        )
        thinking_embed.set_author(
            name=f"{interaction.user.name}",
            icon_url=interaction.user.display_avatar.url
        )

        await interaction.response.send_message(embed=thinking_embed)

        import asyncio
        await asyncio.sleep(2)

        response_type = random.choices(
            ["positive", "negative", "neutral"],
            weights=[0.4, 0.3, 0.3]
        )[0]
        
        if response_type == "positive":
            answer = random.choice(self.positive_responses)
            color = 0x00FF00
            mood = "😊"
        elif response_type == "negative":
            answer = random.choice(self.negative_responses)
            color = 0xFF0000
            mood = "😔"
        else:
            answer = random.choice(self.neutral_responses)
            color = 0x87CEEB
            mood = "🤔"

        result_embed = nextcord.Embed(
            title="🔮 **8-Ball Response**",
            description=answer,
            color=color
        )
        
        result_embed.add_field(
            name="❓ Your Question",
            value=f"```{question}```",
            inline=False
        )
        
        result_embed.add_field(
            name=f"{mood} Response Type",
            value=f"```{response_type.title()}```",
            inline=True
        )
        
        result_embed.add_field(
            name="🎲 Mystical Energy",
            value=f"```{random.randint(1, 100)}%```",
            inline=True
        )
        
        result_embed.add_field(
            name="📊 8-Ball Statistics",
            value=f"```Positive: 40% | Negative: 30% | Neutral: 30%```",
            inline=True
        )
        
        result_embed.add_field(
            name="🔮 Mystical Factor",
            value=f"```Seed: {random.randint(1000, 9999)}```",
            inline=True
        )
        
        result_embed.add_field(
            name="⏰ Consultation Time",
            value=f"<t:{int(datetime.now().timestamp())}:R>",
            inline=False
        )
        
        result_embed.set_footer(
            text="© Ryujin Bot (2023-2025) | Fun System",
            icon_url=self.RYUJIN_LOGO
        )
        result_embed.set_author(
            name=f"{interaction.user.name}",
            icon_url=interaction.user.display_avatar.url
        )

        await interaction.edit_original_message(embed=result_embed)
        
        await self.bot.maybe_send_ad(interaction)

def setup(bot):
    bot.add_cog(EightBallCog(bot)) 