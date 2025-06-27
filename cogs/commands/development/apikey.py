import nextcord
from nextcord.ext import commands
import requests
from mysql.connector import Error

class ApiKeyCog(commands.Cog):
    def __init__(self, bot):
        self.bot = bot
        self.RYUJIN_LOGO = "https://cdn.discordapp.com/avatars/1059400568805785620/63a77f852ea29f37961f458c53fb5a97.png"

    @nextcord.slash_command(
        name="apikey",
        description="Manage API keys for the Remove Background feature",
        guild_ids=[1060144274722787328]
    )
    async def apikey(
        self,
        interaction: nextcord.Interaction,
        action: str = nextcord.SlashOption(
            name="action",
            description="Action to perform",
            choices={"Add": "add", "Remove": "remove", "List": "list", "Test": "test"},
            required=True
        ),
        api_key: str = nextcord.SlashOption(
            name="api_key",
            description="API key to add/remove",
            required=False
        )
    ):
        if interaction.user.id not in [977190163736322088, 1286323016061685779]:
            embed = nextcord.Embed(
                title="Error",
                description="You don't have permission to use this command.",
                color=0xff0000
            )
            embed.set_footer(
                text="© Ryujin Bot (2023-2025) | Remove Background System",
                icon_url=self.RYUJIN_LOGO
            )
            embed.set_author(
                name="Ryujin",
                icon_url=self.RYUJIN_LOGO
            )
            await interaction.response.send_message(embed=embed, ephemeral=True)
            return

        try:
            cursor = self.bot.connection.cursor()
            
            if action == "add":
                if not api_key:
                    raise ValueError("API key is required for add action")
                    
                cursor.execute(
                    "INSERT INTO removebgapi (api_key) VALUES (%s)",
                    (api_key,)
                )
                self.bot.connection.commit()
                description = "API key has been added successfully."
                
            elif action == "remove":
                if api_key == "all":
                    cursor.execute("DELETE FROM removebgapi")
                    self.bot.connection.commit()
                    description = "All API keys have been removed successfully."
                else:
                    if not api_key:
                        raise ValueError("API key is required for remove action")
                        
                    cursor.execute(
                        "DELETE FROM removebgapi WHERE api_key = %s",
                        (api_key,)
                    )
                    self.bot.connection.commit()
                    description = "API key has been removed successfully."
                
            elif action == "list":
                cursor.execute("SELECT api_key FROM removebgapi")
                keys = cursor.fetchall()
                if keys:
                    description = "Current API keys:\n"
                    for key in keys:
                        description += f"• {key[0]}\n"
                else:
                    description = "No API keys found."
            elif action == "test":
                if not api_key:
                    raise ValueError("API key is required for testing")
                    
                try:
                    response = requests.get(
                        "https://api.developer.pixelcut.ai/v1/credits",
                        headers={
                            'Accept': 'application/json',
                            "X-API-Key": api_key
                        }
                    )
                    if response.status_code == 200:
                        credits = response.json().get("credits", "Unknown")
                        description = f"API key is valid. Credits remaining: {credits}"
                    else:
                        description = "API key is invalid or expired"
                except:
                    description = "Error testing API key"
            
            cursor.close()

            embed = nextcord.Embed(
                title="API Key Management",
                description=description,
                color=0x2a2a2a
            )
            embed.set_footer(
                text="© Ryujin Bot (2023-2025) | Remove Background System",
                icon_url=self.RYUJIN_LOGO
            )
            embed.set_author(
                name="Ryujin",
                icon_url=self.RYUJIN_LOGO
            )
            await interaction.response.send_message(embed=embed, ephemeral=True)
            
        except ValueError as ve:
            embed = nextcord.Embed(
                title="Error", 
                description=str(ve),
                color=0xff0000
            )
            embed.set_footer(
                text="© Ryujin Bot (2023-2025) | Remove Background System",
                icon_url=self.RYUJIN_LOGO
            )
            embed.set_author(
                name="Ryujin",
                icon_url=self.RYUJIN_LOGO
            )
            await interaction.response.send_message(embed=embed, ephemeral=True)
            
        except Error as e:
            embed = nextcord.Embed(
                title="Error",
                description=f"Database error: {str(e)}",
                color=0xff0000
            )
            embed.set_footer(
                text="© Ryujin Bot (2023-2025) | Remove Background System",
                icon_url=self.RYUJIN_LOGO
            )
            embed.set_author(
                name="Ryujin",
                icon_url=self.RYUJIN_LOGO
            )
            await interaction.response.send_message(embed=embed, ephemeral=True)

def setup(bot):
    bot.add_cog(ApiKeyCog(bot)) 