import nextcord
from nextcord.ext import commands
from nextcord import SlashOption
import logging

class Category(commands.Cog):
    def __init__(self, bot):
        self.bot = bot

    def check_blacklist(self, user_id):
        """Check if user is blacklisted"""
        if hasattr(self.bot, 'blacklist'):
            return user_id in self.bot.blacklist, self.bot.blacklist.get(user_id)
        return False, None

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
            icon_url=self.bot.RYUJIN_LOGO
        )
        return embed

    @nextcord.slash_command(
        name="category",
        description="Create or delete a category. 📋",
        default_member_permissions=nextcord.Permissions(manage_channels=True)
    )
    async def category(
        self,
        interaction: nextcord.Interaction,
        action: str = SlashOption(
            name="action",
            description="Action to perform (create/delete)",
            required=True,
            choices={"create": "create", "delete": "delete"}
        ),
        name: str = SlashOption(
            name="name",
            description="Name for the new category (for create)",
            required=False
        ),
        position: int = SlashOption(
            name="position",
            description="Position for the new category (for create)",
            required=False
        ),
        category: nextcord.CategoryChannel = SlashOption(
            name="category",
            description="Category to delete (for delete)",
            required=False
        )
    ):
        is_blacklisted, reason = self.check_blacklist(interaction.user.id)
        if is_blacklisted:
            embed = self.create_blacklist_embed(reason)
            await interaction.send(embed=embed, ephemeral=True)
            return

        if not interaction.user.guild_permissions.manage_channels:
            await interaction.send("❌ You don't have permission to use this command.", ephemeral=True)
            return

        if action == "create":
            if not name:
                await interaction.send("❌ You must provide a name for the new category.", ephemeral=True)
                return
            if len(name) < 1 or len(name) > 100:
                await interaction.send("❌ Category name must be between 1 and 100 characters.", ephemeral=True)
                return
            existing_category = nextcord.utils.get(interaction.guild.categories, name=name)
            if existing_category:
                await interaction.send(f"❌ A category named **{name}** already exists.", ephemeral=True)
                return
            try:
                category_obj = await interaction.guild.create_category(
                    name=name,
                    position=position,
                    reason=f"Category created by {interaction.user}"
                )
                embed = nextcord.Embed(
                    title="✅ Category Created Successfully",
                    description=f"Successfully created category **{name}**",
                    color=nextcord.Color.green()
                )
                embed.add_field(name="Category", value=f"{category_obj.mention} ({category_obj.name})", inline=True)
                embed.add_field(name="Position", value=f"{category_obj.position}", inline=True)
                embed.add_field(name="Created by", value=f"{interaction.user.mention}", inline=True)
                embed.add_field(name="ID", value=f"`{category_obj.id}`", inline=True)
                embed.add_field(name="Created at", value=f"<t:{int(category_obj.created_at.timestamp())}:R>", inline=True)
                embed.set_footer(text="© Ryujin Bot (2023-2025) | Moderation System")
                embed.set_author(name="Ryujin", icon_url=self.bot.RYUJIN_LOGO)
                await interaction.send(embed=embed, ephemeral=True)
                await self.bot.maybe_send_ad(interaction)
            except Exception as e:
                await interaction.send(f"❌ Failed to create category: `{e}`", ephemeral=True)
        elif action == "delete":
            if not category:
                await interaction.send("❌ You must select a category to delete.", ephemeral=True)
                return
            if category.channels:
                channel_list = "\n".join([f"• {ch.mention} ({ch.name})" for ch in category.channels[:10]])
                msg = f"⚠️ The category **{category.name}** has **{len(category.channels)}** channels.\n\n**Channels:**\n{channel_list}"
                if len(category.channels) > 10:
                    msg += f"\nAnd {len(category.channels) - 10} more..."
                msg += "\n\nDeleting this category will also delete all channels within it!"
                await interaction.send(msg, ephemeral=True)
                return
            try:
                category_name = category.name
                category_id = category.id
                channel_count = len(category.channels)
                await category.delete(reason=f"Category deleted by {interaction.user}")
                embed = nextcord.Embed(
                    title="✅ Category Deleted Successfully",
                    description=f"Successfully deleted category **{category_name}**",
                    color=nextcord.Color.green()
                )
                embed.add_field(name="Category Name", value=f"{category_name}", inline=True)
                embed.add_field(name="Channels Deleted", value=f"{channel_count} channels", inline=True)
                embed.add_field(name="Deleted by", value=f"{interaction.user.mention}", inline=True)
                embed.add_field(name="Category ID", value=f"`{category_id}`", inline=True)
                embed.set_footer(text="© Ryujin Bot (2023-2025) | Moderation System")
                embed.set_author(name="Ryujin", icon_url=self.bot.RYUJIN_LOGO)
                await interaction.send(embed=embed, ephemeral=True)
                await self.bot.maybe_send_ad(interaction)
            except Exception as e:
                await interaction.send(f"❌ Failed to delete category: `{e}`", ephemeral=True)
        else:
            await interaction.send("❌ Invalid action. Use 'create' or 'delete'!", ephemeral=True)

def setup(bot):
    bot.add_cog(Category(bot)) 