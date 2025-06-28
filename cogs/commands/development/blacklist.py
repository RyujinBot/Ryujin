import nextcord
from nextcord.ext import commands
from mysql.connector import Error
from cogs.utils.db import add_to_blacklist, remove_from_blacklist, get_blacklist

class BlacklistCog(commands.Cog):
    def __init__(self, bot):
        self.bot = bot
        self.RYUJIN_LOGO = "https://cdn.discordapp.com/avatars/1059400568805785620/63a77f852ea29f37961f458c53fb5a97.png"

    @nextcord.slash_command(
        name="blacklist",
        description="Manage user blacklist (Development only)",
        guild_ids=[1060144274722787328]
    )
    async def blacklist(
        self,
        interaction: nextcord.Interaction,
        action: str = nextcord.SlashOption(
            name="action",
            description="Action to perform",
            choices={"Add": "add", "Remove": "remove", "List": "list", "Check": "check"},
            required=True
        ),
        user: nextcord.Member = nextcord.SlashOption(
            name="user",
            description="User to blacklist/remove from blacklist",
            required=False
        ),
        reason: str = nextcord.SlashOption(
            name="reason",
            description="Reason for blacklisting",
            required=False
        )
    ):
        if interaction.user.id != 977190163736322088:
            embed = nextcord.Embed(
                title="❌ Access Denied",
                description="You don't have permission to use this command. Only the bot owner can manage the blacklist.",
                color=0xff0000
            )
            embed.set_footer(
                text="© Ryujin Bot (2023-2025) | Development System",
                icon_url=self.RYUJIN_LOGO
            )
            embed.set_author(
                name="Ryujin",
                icon_url=self.RYUJIN_LOGO
            )
            await interaction.response.send_message(embed=embed, ephemeral=True)
            return

        try:
            if action == "add":
                if not user:
                    embed = nextcord.Embed(
                        title="❌ Error",
                        description="Please specify a user to blacklist.",
                        color=0xff0000
                    )
                    embed.set_footer(
                        text="© Ryujin Bot (2023-2025) | Development System",
                        icon_url=self.RYUJIN_LOGO
                    )
                    embed.set_author(
                        name="Ryujin",
                        icon_url=self.RYUJIN_LOGO
                    )
                    await interaction.response.send_message(embed=embed, ephemeral=True)
                    return

                if not reason:
                    reason = "No reason provided"

                await add_to_blacklist(self.bot.connection, user.id, reason)
                
                self.bot.blacklist = get_blacklist(self.bot.connection)
                
                embed = nextcord.Embed(
                    title="✅ User Blacklisted",
                    description=f"**{user.mention}** has been added to the blacklist.\n\n**Reason:** {reason}",
                    color=0xff0000
                )
                embed.set_thumbnail(url=user.display_avatar.url)
                embed.set_footer(
                    text="© Ryujin Bot (2023-2025) | Development System",
                    icon_url=self.RYUJIN_LOGO
                )
                embed.set_author(
                    name="Ryujin",
                    icon_url=self.RYUJIN_LOGO
                )
                await interaction.response.send_message(embed=embed, ephemeral=True)

            elif action == "remove":
                if not user:
                    embed = nextcord.Embed(
                        title="❌ Error",
                        description="Please specify a user to remove from blacklist.",
                        color=0xff0000
                    )
                    embed.set_footer(
                        text="© Ryujin Bot (2023-2025) | Development System",
                        icon_url=self.RYUJIN_LOGO
                    )
                    embed.set_author(
                        name="Ryujin",
                        icon_url=self.RYUJIN_LOGO
                    )
                    await interaction.response.send_message(embed=embed, ephemeral=True)
                    return

                removed = await remove_from_blacklist(self.bot.connection, user.id)
                
                if removed:
                    self.bot.blacklist = get_blacklist(self.bot.connection)
                    
                    embed = nextcord.Embed(
                        title="✅ User Removed from Blacklist",
                        description=f"**{user.mention}** has been removed from the blacklist.",
                        color=0x00ff00
                    )
                    embed.set_thumbnail(url=user.display_avatar.url)
                    embed.set_footer(
                        text="© Ryujin Bot (2023-2025) | Development System",
                        icon_url=self.RYUJIN_LOGO
                    )
                    embed.set_author(
                        name="Ryujin",
                        icon_url=self.RYUJIN_LOGO
                    )
                    await interaction.response.send_message(embed=embed, ephemeral=True)
                else:
                    embed = nextcord.Embed(
                        title="❌ User Not Found",
                        description=f"**{user.mention}** is not in the blacklist.",
                        color=0xff0000
                    )
                    embed.set_footer(
                        text="© Ryujin Bot (2023-2025) | Development System",
                        icon_url=self.RYUJIN_LOGO
                    )
                    embed.set_author(
                        name="Ryujin",
                        icon_url=self.RYUJIN_LOGO
                    )
                    await interaction.response.send_message(embed=embed, ephemeral=True)

            elif action == "list":
                blacklist = get_blacklist(self.bot.connection)
                
                if not blacklist:
                    embed = nextcord.Embed(
                        title="📋 Blacklist",
                        description="No users are currently blacklisted.",
                        color=0x2a2a2a
                    )
                    embed.set_footer(
                        text="© Ryujin Bot (2023-2025) | Development System",
                        icon_url=self.RYUJIN_LOGO
                    )
                    embed.set_author(
                        name="Ryujin",
                        icon_url=self.RYUJIN_LOGO
                    )
                    await interaction.response.send_message(embed=embed, ephemeral=True)
                    return

                embed = nextcord.Embed(
                    title="📋 Blacklisted Users",
                    description=f"Total blacklisted users: **{len(blacklist)}**",
                    color=0x2a2a2a
                )

                for i, (user_id, reason) in enumerate(list(blacklist.items())[:25]):
                    try:
                        user_obj = await self.bot.fetch_user(user_id)
                        user_mention = user_obj.mention
                        user_name = user_obj.name
                    except:
                        user_mention = f"<@{user_id}>"
                        user_name = f"Unknown User ({user_id})"

                    embed.add_field(
                        name=f"#{i+1} {user_name}",
                        value=f"**User:** {user_mention}\n**Reason:** {reason}",
                        inline=False
                    )

                if len(blacklist) > 25:
                    embed.add_field(
                        name="Note",
                        value=f"Showing first 25 users. Total: {len(blacklist)}",
                        inline=False
                    )

                embed.set_footer(
                    text="© Ryujin Bot (2023-2025) | Development System",
                    icon_url=self.RYUJIN_LOGO
                )
                embed.set_author(
                    name="Ryujin",
                    icon_url=self.RYUJIN_LOGO
                )
                await interaction.response.send_message(embed=embed, ephemeral=True)

            elif action == "check":
                if not user:
                    embed = nextcord.Embed(
                        title="❌ Error",
                        description="Please specify a user to check.",
                        color=0xff0000
                    )
                    embed.set_footer(
                        text="© Ryujin Bot (2023-2025) | Development System",
                        icon_url=self.RYUJIN_LOGO
                    )
                    embed.set_author(
                        name="Ryujin",
                        icon_url=self.RYUJIN_LOGO
                    )
                    await interaction.response.send_message(embed=embed, ephemeral=True)
                    return

                blacklist = get_blacklist(self.bot.connection)
                
                if user.id in blacklist:
                    embed = nextcord.Embed(
                        title="🔴 User is Blacklisted",
                        description=f"**{user.mention}** is currently blacklisted.\n\n**Reason:** {blacklist[user.id]}",
                        color=0xff0000
                    )
                    embed.set_thumbnail(url=user.display_avatar.url)
                else:
                    embed = nextcord.Embed(
                        title="🟢 User is Not Blacklisted",
                        description=f"**{user.mention}** is not in the blacklist.",
                        color=0x00ff00
                    )
                    embed.set_thumbnail(url=user.display_avatar.url)

                embed.set_footer(
                    text="© Ryujin Bot (2023-2025) | Development System",
                    icon_url=self.RYUJIN_LOGO
                )
                embed.set_author(
                    name="Ryujin",
                    icon_url=self.RYUJIN_LOGO
                )
                await interaction.response.send_message(embed=embed, ephemeral=True)

        except Error as e:
            embed = nextcord.Embed(
                title="❌ Database Error",
                description=f"An error occurred while accessing the database: {str(e)}",
                color=0xff0000
            )
            embed.set_footer(
                text="© Ryujin Bot (2023-2025) | Development System",
                icon_url=self.RYUJIN_LOGO
            )
            embed.set_author(
                name="Ryujin",
                icon_url=self.RYUJIN_LOGO
            )
            await interaction.response.send_message(embed=embed, ephemeral=True)

        except Exception as e:
            embed = nextcord.Embed(
                title="❌ Error",
                description=f"An unexpected error occurred: {str(e)}",
                color=0xff0000
            )
            embed.set_footer(
                text="© Ryujin Bot (2023-2025) | Development System",
                icon_url=self.RYUJIN_LOGO
            )
            embed.set_author(
                name="Ryujin",
                icon_url=self.RYUJIN_LOGO
            )
            await interaction.response.send_message(embed=embed, ephemeral=True)

def setup(bot):
    bot.add_cog(BlacklistCog(bot)) 