import nextcord
from nextcord.ext import commands
import random
import asyncio
from datetime import datetime

class CoinflipCog(commands.Cog):
    def __init__(self, bot):
        self.bot = bot
        self.RYUJIN_LOGO = "https://cdn.discordapp.com/avatars/1059400568805785620/63a77f852ea29f37961f458c53fb5a97.png"
        
        self.coin_images = {
            "heads": "https://cdn.moongetsu.ro/Ryujin/Coinflip/heads.png",
            "tails": "https://cdn.moongetsu.ro/Ryujin/Coinflip/tails.png",
            "spinning": "https://cdn.dribbble.com/userupload/19760526/file/original-86b4d507fac74ea591286f21d729d573.gif"
        }
        
        self.heads_messages = [
            "🎯 **Heads!** The coin landed perfectly on heads!",
            "👑 **Heads!** Crown side up - you're the king/queen of luck!",
            "⭐ **Heads!** The stars aligned for you!",
            "🌟 **Heads!** Shining bright like your future!",
            "💫 **Heads!** Cosmic energy favors you today!"
        ]
        
        self.tails_messages = [
            "🪙 **Tails!** The coin flipped to tails!",
            "🌙 **Tails!** Moon side showing - mysterious energy!",
            "✨ **Tails!** Sparkling with tail-side magic!",
            "🎭 **Tails!** The other side of the story!",
            "🔮 **Tails!** Fortune favors the bold!"
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
        name="coinflip",
        description="Flip a coin with creative animations and modern UI! 🪙"
    )
    async def coinflip(
        self,
        interaction: nextcord.Interaction,
        prediction: str = nextcord.SlashOption(
            choices=["heads", "tails", "random"],
            description="Predict the outcome (optional)",
            required=False
        )
    ):
        if self.check_blacklist(interaction.user.id):
            embed = self.create_blacklist_embed(self.bot.blacklist[interaction.user.id])
            await interaction.response.send_message(embed=embed, ephemeral=True)
            return

        spinning_embed = nextcord.Embed(
            title="🪙 **Coin Flip in Progress...**",
            description="The coin is spinning through the air! ✨",
            color=0x2a2a2a
        )
        spinning_embed.set_image(url=self.coin_images["spinning"])
        spinning_embed.add_field(
            name="🎯 Your Prediction",
            value=f"```{prediction.title() if prediction else 'None'}```",
            inline=True
        )
        spinning_embed.add_field(
            name="⏱️ Spinning Time",
            value="```3 seconds```",
            inline=True
        )
        spinning_embed.set_footer(
            text="© Ryujin Bot (2023-2025) | Fun System",
            icon_url=self.RYUJIN_LOGO
        )
        spinning_embed.set_author(
            name=f"{interaction.user.name}",
            icon_url=interaction.user.display_avatar.url
        )

        await interaction.response.send_message(embed=spinning_embed)

        await asyncio.sleep(3)

        result = random.choice(["heads", "tails"])
        
        if result == "heads":
            message = random.choice(self.heads_messages)
            result_emoji = "🪙"
            color = 0xFFD700
        else:
            message = random.choice(self.tails_messages)
            result_emoji = "🌙"
            color = 0x87CEEB

        result_embed = nextcord.Embed(
            title=f"{result_emoji} **{result.upper()}!**",
            description=message,
            color=color
        )
        result_embed.set_image(url=self.coin_images[result])
        
        if prediction:
            if prediction.lower() == result:
                prediction_result = "✅ **Correct!** You predicted it right!"
                prediction_emoji = "🎉"
            else:
                prediction_result = "❌ **Wrong!** Better luck next time!"
                prediction_emoji = "😅"
            
            result_embed.add_field(
                name=f"{prediction_emoji} Prediction Result",
                value=prediction_result,
                inline=False
            )
        
        result_embed.add_field(
            name="📊 Flip Statistics",
            value=f"```Heads: {random.randint(45, 55)}% | Tails: {random.randint(45, 55)}%```",
            inline=True
        )
        
        result_embed.add_field(
            name="🎲 Random Factor",
            value=f"```Seed: {random.randint(1000, 9999)}```",
            inline=True
        )
        
        result_embed.add_field(
            name="⏰ Flip Time",
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

    @nextcord.slash_command(
        name="coinflip_battle",
        description="Challenge someone to a coin flip battle! ⚔️"
    )
    async def coinflip_battle(
        self,
        interaction: nextcord.Interaction,
        opponent: nextcord.Member = nextcord.SlashOption(
            description="Who do you want to challenge?",
            required=True
        ),
        rounds: int = nextcord.SlashOption(
            description="Number of rounds (1-10)",
            min_value=1,
            max_value=10,
            required=False,
            default=3
        )
    ):
        if self.check_blacklist(interaction.user.id):
            embed = self.create_blacklist_embed(self.bot.blacklist[interaction.user.id])
            await interaction.response.send_message(embed=embed, ephemeral=True)
            return
            
        if self.check_blacklist(opponent.id):
            embed = self.create_blacklist_embed(self.bot.blacklist[opponent.id])
            await interaction.response.send_message(embed=embed, ephemeral=True)
            return

        if opponent == interaction.user:
            await interaction.response.send_message(
                "❌ You can't challenge yourself to a coin flip battle!",
                ephemeral=True
            )
            return

        battle_embed = nextcord.Embed(
            title="⚔️ **Coin Flip Battle Challenge!**",
            description=f"**{interaction.user.mention}** challenges **{opponent.mention}** to a coin flip battle!",
            color=0xFF6B6B
        )
        battle_embed.add_field(
            name="🎯 Battle Details",
            value=f"**Rounds:** {rounds}\n**Type:** Best of {rounds}",
            inline=True
        )
        battle_embed.add_field(
            name="🏆 Prize",
            value="**Bragging Rights!** 👑",
            inline=True
        )
        battle_embed.set_image(url="https://cdn.moongetsu.ro/Ryujin/Coinflip/battle.gif")
        battle_embed.set_footer(
            text="© Ryujin Bot (2023-2025) | Fun System Battle",
            icon_url=self.RYUJIN_LOGO
        )
        battle_embed.set_author(
            name="Ryujin",
            icon_url=self.RYUJIN_LOGO
        )

        class BattleView(nextcord.ui.View):
            def __init__(self, cog, challenger, opponent, rounds):
                super().__init__(timeout=60)
                self.cog = cog
                self.challenger = challenger
                self.opponent = opponent
                self.rounds = rounds
                self.accepted = False

            @nextcord.ui.button(label="✅ Accept Challenge", style=nextcord.ButtonStyle.green)
            async def accept(self, button: nextcord.ui.Button, interaction: nextcord.Interaction):
                if interaction.user != self.opponent:
                    await interaction.response.send_message("❌ Only the challenged player can accept!", ephemeral=True)
                    return
                
                self.accepted = True
                button.disabled = True
                button.label = "✅ Challenge Accepted!"
                
                await interaction.response.edit_message(view=self)
                
                await self.start_battle(interaction)

            @nextcord.ui.button(label="❌ Decline Challenge", style=nextcord.ButtonStyle.red)
            async def decline(self, button: nextcord.ui.Button, interaction: nextcord.Interaction):
                if interaction.user != self.opponent:
                    await interaction.response.send_message("❌ Only the challenged player can decline!", ephemeral=True)
                    return
                
                button.disabled = True
                button.label = "❌ Challenge Declined!"
                
                await interaction.response.edit_message(
                    embed=nextcord.Embed(
                        title="❌ Challenge Declined",
                        description=f"**{self.opponent.mention}** declined the coin flip battle challenge.",
                        color=0xFF0000
                    ),
                    view=self
                )

            async def start_battle(self, interaction: nextcord.Interaction):
                challenger_score = 0
                opponent_score = 0
                battle_log = []

                battle_embed = nextcord.Embed(
                    title="⚔️ **Coin Flip Battle**",
                    description="Battle in progress...",
                    color=0x2a2a2a
                )
                battle_embed.add_field(
                    name="📊 Score",
                    value=f"**{self.challenger.name}:** 0 | **{self.opponent.name}:** 0",
                    inline=False
                )
                battle_embed.add_field(
                    name="🎮 Current Round",
                    value="**Starting battle...**",
                    inline=False
                )
                battle_embed.set_footer(
                    text="© Ryujin Bot (2023-2025) | Fun System Battle",
                    icon_url=self.cog.RYUJIN_LOGO
                )

                battle_embed.set_author(
                    name=f"Ryujin",
                    icon_url=self.cog.RYUJIN_LOGO
                )
                
                battle_message = await interaction.channel.send(embed=battle_embed)

                for round_num in range(1, self.rounds + 1):
                    round_embed = nextcord.Embed(
                        title=f"⚔️ **Round {round_num}/{self.rounds}**",
                        description="The coin is spinning...",
                        color=0x2a2a2a
                    )
                    round_embed.set_image(url=self.cog.coin_images["spinning"])
                    round_embed.add_field(
                        name="📊 Current Score",
                        value=f"**{self.challenger.name}:** {challenger_score} | **{self.opponent.name}:** {opponent_score}",
                        inline=False
                    )
                    round_embed.add_field(
                        name="🎮 Current Round",
                        value=f"**Round {round_num}** - Spinning coin...",
                        inline=False
                    )
                    round_embed.set_footer(
                        text=f"© Ryujin Bot (2023-2025) | Round {round_num}/{self.rounds}",
                        icon_url=self.cog.RYUJIN_LOGO
                    )
                    round_embed.set_author(
                        name=f"Ryujin",
                        icon_url=self.cog.RYUJIN_LOGO
                    )
                    
                    await battle_message.edit(embed=round_embed)
                    await asyncio.sleep(2)

                    result = random.choice(["heads", "tails"])
                    if result == "heads":
                        challenger_score += 1
                        winner = self.challenger
                        loser = self.opponent
                    else:
                        opponent_score += 1
                        winner = self.opponent
                        loser = self.challenger

                    battle_log.append(f"**Round {round_num}:** {winner.name} wins with {result}!")

                    result_embed = nextcord.Embed(
                        title=f"🎯 **Round {round_num} Complete**",
                        description=f"**{result.upper()}!** {winner.mention} wins this round!",
                        color=0x00FF00
                    )
                    result_embed.set_image(url=self.cog.coin_images[result])
                    result_embed.add_field(
                        name="📊 Updated Score",
                        value=f"**{self.challenger.name}:** {challenger_score} | **{self.opponent.name}:** {opponent_score}",
                        inline=False
                    )
                    
                    if battle_log:
                        result_embed.add_field(
                            name="📝 Battle Log",
                            value="\n".join(battle_log[-3:]),
                            inline=False
                        )
                    
                    await battle_message.edit(embed=result_embed)
                    await asyncio.sleep(1)

                if challenger_score > opponent_score:
                    winner = self.challenger
                    loser = self.opponent
                    winner_score = challenger_score
                    loser_score = opponent_score
                elif opponent_score > challenger_score:
                    winner = self.opponent
                    loser = self.challenger
                    winner_score = opponent_score
                    loser_score = challenger_score
                else:
                    winner = None
                    winner_score = challenger_score
                    loser_score = opponent_score

                if winner:
                    final_embed = nextcord.Embed(
                        title="🏆 **Battle Complete!**",
                        description=f"**{winner.mention}** wins the coin flip battle!",
                        color=0xFFD700
                    )
                    final_embed.add_field(
                        name="📊 Final Score",
                        value=f"**{winner.name}:** {winner_score} | **{loser.name}:** {loser_score}",
                        inline=False
                    )
                else:
                    final_embed = nextcord.Embed(
                        title="🤝 **Battle Complete!**",
                        description="It's a tie! Both players are equally lucky!",
                        color=0x87CEEB
                    )
                    final_embed.add_field(
                        name="📊 Final Score",
                        value=f"**{self.challenger.name}:** {winner_score} | **{self.opponent.name}:** {loser_score}",
                        inline=False
                    )

                final_embed.add_field(
                    name="📝 Complete Battle Log",
                    value="\n".join(battle_log),
                    inline=False
                )
                final_embed.set_footer(
                    text="© Ryujin Bot (2023-2025) | Fun System Battle",
                    icon_url=self.cog.RYUJIN_LOGO
                )
                final_embed.set_author(
                    name=f"{winner.name}",
                    icon_url=winner.avatar.url
                )
                
                await battle_message.edit(embed=final_embed)

        view = BattleView(self, interaction.user, opponent, rounds)
        await interaction.response.send_message(embed=battle_embed, view=view)
        
        await self.bot.maybe_send_ad(interaction)

def setup(bot):
    bot.add_cog(CoinflipCog(bot)) 