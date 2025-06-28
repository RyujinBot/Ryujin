import nextcord
from nextcord.ext import commands
import random
import asyncio
from datetime import datetime

class DiceCog(commands.Cog):
    def __init__(self, bot):
        self.bot = bot
        self.RYUJIN_LOGO = "https://cdn.discordapp.com/avatars/1059400568805785620/63a77f852ea29f37961f458c53fb5a97.png"
        
        self.dice_emojis = {
            1: "⚀",
            2: "⚁", 
            3: "⚂",
            4: "⚃",
            5: "⚄",
            6: "⚅"
        }
        
        self.critical_messages = [
            "🎯 **Critical Success!** Perfect roll!",
            "🌟 **Amazing!** The dice gods favor you!",
            "💫 **Incredible!** Maximum value achieved!",
            "👑 **Royal Roll!** You're the king/queen of dice!",
            "⭐ **Stellar!** Out of this world roll!"
        ]
        
        self.low_messages = [
            "😅 **Low Roll!** Better luck next time!",
            "🌙 **Minimum Value!** The dice were shy today!",
            "🍀 **Lucky Low!** Sometimes less is more!",
            "🎭 **Dramatic Low!** Setting up for a comeback!",
            "🔮 **Mysterious Low!** The dice have spoken!"
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
        name="dice",
        description="Roll dice with creative animations and modern UI! 🎲"
    )
    async def dice(
        self,
        interaction: nextcord.Interaction,
        sides: int = nextcord.SlashOption(
            description="Number of sides on the dice (2-100)",
            min_value=2,
            max_value=100,
            required=False,
            default=6
        ),
        count: int = nextcord.SlashOption(
            description="Number of dice to roll (1-10)",
            min_value=1,
            max_value=10,
            required=False,
            default=1
        )
    ):
        if self.check_blacklist(interaction.user.id):
            embed = self.create_blacklist_embed(self.bot.blacklist[interaction.user.id])
            await interaction.response.send_message(embed=embed, ephemeral=True)
            return

        rolling_embed = nextcord.Embed(
            title="🎲 **Dice Rolling...**",
            description="The dice are tumbling through the air! ✨",
            color=0x2a2a2a
        )
        rolling_embed.add_field(
            name="🎯 Dice Configuration",
            value=f"```{count} dice with {sides} sides each```",
            inline=True
        )
        rolling_embed.add_field(
            name="⏱️ Rolling Time",
            value="```2 seconds```",
            inline=True
        )
        rolling_embed.set_footer(
            text="© Ryujin Bot (2023-2025) | Fun System",
            icon_url=self.RYUJIN_LOGO
        )
        rolling_embed.set_author(
            name=f"{interaction.user.name}",
            icon_url=interaction.user.display_avatar.url
        )

        await interaction.response.send_message(embed=rolling_embed)

        await asyncio.sleep(2)

        results = [random.randint(1, sides) for _ in range(count)]
        total = sum(results)
        
        if sides == 6 and count == 1:
            if results[0] == sides:
                message = random.choice(self.critical_messages)
                color = 0xFFD700
            elif results[0] == 1:
                message = random.choice(self.low_messages)
                color = 0x87CEEB
            else:
                message = f"🎲 **Rolled {results[0]}!** Nice roll!"
                color = 0x2a2a2a
        else:
            if total == count * sides:
                message = random.choice(self.critical_messages)
                color = 0xFFD700
            elif total == count:
                message = random.choice(self.low_messages)
                color = 0x87CEEB
            else:
                message = f"🎲 **Total: {total}** Great rolling!"
                color = 0x2a2a2a

        result_embed = nextcord.Embed(
            title="🎲 **Dice Results!**",
            description=message,
            color=color
        )
        
        if count == 1:
            if sides <= 6:
                dice_display = f"{self.dice_emojis.get(results[0], '🎲')} **{results[0]}**"
            else:
                dice_display = f"🎲 **{results[0]}**"
            result_embed.add_field(
                name="🎯 Roll Result",
                value=dice_display,
                inline=False
            )
        else:
            dice_results = []
            for i, result in enumerate(results, 1):
                if sides <= 6:
                    dice_results.append(f"Die {i}: {self.dice_emojis.get(result, '🎲')} **{result}**")
                else:
                    dice_results.append(f"Die {i}: 🎲 **{result}**")
            
            result_embed.add_field(
                name="🎯 Individual Rolls",
                value="\n".join(dice_results),
                inline=False
            )
            result_embed.add_field(
                name="📊 Total Sum",
                value=f"**{total}**",
                inline=True
            )
        
        result_embed.add_field(
            name="📈 Roll Statistics",
            value=f"```Min: 1 | Max: {sides} | Average: {sides/2:.1f}```",
            inline=True
        )
        
        result_embed.add_field(
            name="🎲 Random Factor",
            value=f"```Seed: {random.randint(1000, 9999)}```",
            inline=True
        )
        
        result_embed.add_field(
            name="⏰ Roll Time",
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
        name="dice_battle",
        description="Challenge someone to a dice battle! ⚔️"
    )
    async def dice_battle(
        self,
        interaction: nextcord.Interaction,
        opponent: nextcord.Member = nextcord.SlashOption(
            description="Who do you want to challenge?",
            required=True
        ),
        sides: int = nextcord.SlashOption(
            description="Number of sides on the dice (2-20)",
            min_value=2,
            max_value=20,
            required=False,
            default=6
        ),
        rounds: int = nextcord.SlashOption(
            description="Number of rounds (1-5)",
            min_value=1,
            max_value=5,
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
                "❌ You can't challenge yourself to a dice battle!",
                ephemeral=True
            )
            return

        battle_embed = nextcord.Embed(
            title="⚔️ **Dice Battle Challenge!**",
            description=f"**{interaction.user.mention}** challenges **{opponent.mention}** to a dice battle!",
            color=0xFF6B6B
        )
        battle_embed.add_field(
            name="🎲 Battle Details",
            value=f"**Dice:** {sides}-sided\n**Rounds:** {rounds}\n**Type:** Best of {rounds}",
            inline=True
        )
        battle_embed.add_field(
            name="🏆 Prize",
            value="**Dice Master Title!** 👑",
            inline=True
        )
        battle_embed.set_footer(
            text="© Ryujin Bot (2023-2025) | Fun System",
            icon_url=self.RYUJIN_LOGO
        )
        battle_embed.set_author(
            name="Ryujin",
            icon_url=self.RYUJIN_LOGO
        )

        class DiceBattleView(nextcord.ui.View):
            def __init__(self, cog, challenger, opponent, sides, rounds):
                super().__init__(timeout=60)
                self.cog = cog
                self.challenger = challenger
                self.opponent = opponent
                self.sides = sides
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
                        description=f"**{self.opponent.mention}** declined the dice battle challenge.",
                        color=0xFF0000
                    ),
                    view=self
                )

            async def start_battle(self, interaction: nextcord.Interaction):
                challenger_score = 0
                opponent_score = 0
                battle_log = []

                battle_embed = nextcord.Embed(
                    title="⚔️ **Dice Battle**",
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
                    text="© Ryujin Bot (2023-2025) | Fun System",
                    icon_url=self.cog.RYUJIN_LOGO
                )
                
                battle_message = await interaction.channel.send(embed=battle_embed)

                for round_num in range(1, self.rounds + 1):
                    round_embed = nextcord.Embed(
                        title=f"⚔️ **Round {round_num}/{self.rounds}**",
                        description="Rolling the dice...",
                        color=0x2a2a2a
                    )
                    round_embed.add_field(
                        name="📊 Current Score",
                        value=f"**{self.challenger.name}:** {challenger_score} | **{self.opponent.name}:** {opponent_score}",
                        inline=False
                    )
                    round_embed.add_field(
                        name="🎮 Current Round",
                        value=f"**Round {round_num}** - Rolling dice...",
                        inline=False
                    )
                    round_embed.set_footer(
                        text=f"© Ryujin Bot (2023-2025) | Round {round_num}/{self.rounds}",
                        icon_url=self.cog.RYUJIN_LOGO
                    )
                    
                    await battle_message.edit(embed=round_embed)
                    await asyncio.sleep(1)

                    challenger_roll = random.randint(1, self.sides)
                    opponent_roll = random.randint(1, self.sides)

                    if challenger_roll > opponent_roll:
                        challenger_score += 1
                        winner = self.challenger
                        loser = self.opponent
                        winner_roll = challenger_roll
                        loser_roll = opponent_roll
                    elif opponent_roll > challenger_roll:
                        opponent_score += 1
                        winner = self.opponent
                        loser = self.challenger
                        winner_roll = opponent_roll
                        loser_roll = challenger_roll
                    else:
                        challenger_score += 1
                        opponent_score += 1
                        winner = None
                        winner_roll = challenger_roll
                        loser_roll = opponent_roll

                    if winner:
                        battle_log.append(f"**Round {round_num}:** {winner.name} wins with {winner_roll} vs {loser.name}'s {loser_roll}!")
                    else:
                        battle_log.append(f"**Round {round_num}:** Tie! Both rolled {winner_roll}!")

                    result_embed = nextcord.Embed(
                        title=f"🎲 **Round {round_num} Complete**",
                        description=f"**{self.challenger.name}:** {challenger_roll} | **{self.opponent.name}:** {opponent_roll}",
                        color=0x00FF00
                    )
                    
                    if winner:
                        result_embed.add_field(
                            name="🏆 Round Winner",
                            value=f"**{winner.mention}** wins this round!",
                            inline=False
                        )
                    else:
                        result_embed.add_field(
                            name="🤝 Round Result",
                            value="**It's a tie!** Both players get a point!",
                            inline=False
                        )
                    
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
                        description=f"**{winner.mention}** wins the dice battle!",
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
                        description="It's a tie! Both players are equally skilled!",
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
                    text="© Ryujin Bot (2023-2025) | Fun System",
                    icon_url=self.cog.RYUJIN_LOGO
                )
                
                await battle_message.edit(embed=final_embed)

        view = DiceBattleView(self, interaction.user, opponent, sides, rounds)
        await interaction.response.send_message(embed=battle_embed, view=view)
        
        await self.bot.maybe_send_ad(interaction)

def setup(bot):
    bot.add_cog(DiceCog(bot)) 