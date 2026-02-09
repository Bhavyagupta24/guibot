import discord
from discord import app_commands
from discord.ext import commands
import json
import os
from modals.embed_modals import EmbedModal
from views.embed_editor_view import EmbedPreviewView

class EmbedBuilder(commands.Cog):
    """
    Cog (module) for embed creation and management.
    
    What's a Cog?
    - Modular piece of bot functionality
    - Groups related commands together
    - Can be loaded/unloaded without restarting bot
    """
    
    def __init__(self, bot):
        self.bot = bot
        # Load presets from JSON file
        self.presets = self.load_presets()
    
    def load_presets(self) -> dict:
        """
        Load embed presets from JSON file.
        Returns empty dict if file doesn't exist or is invalid.
        """
        preset_path = "embeds/presets.json"
        try:
            with open(preset_path, 'r', encoding='utf-8') as f:
                return json.load(f)
        except FileNotFoundError:
            print(f"⚠️ Warning: {preset_path} not found. Presets disabled.")
            return {}
        except json.JSONDecodeError:
            print(f"⚠️ Warning: {preset_path} is invalid JSON. Presets disabled.")
            return {}
    
    # Command Group: /embed
    embed_group = app_commands.Group(
        name="embed",
        description="Create and manage custom embeds"
    )
    
    @embed_group.command(name="create", description="Create a custom embed with an interactive builder")
    @app_commands.checks.has_permissions(manage_messages=True)
    async def embed_create(self, interaction: discord.Interaction):
        """
        Main embed creation command.
        Opens a modal (popup form) for the user to fill out.
        
        Permission Required: Manage Messages
        """
        # Create and send the modal
        modal = EmbedModal()
        await interaction.response.send_modal(modal)
        
        # Wait for user to submit the modal
        await modal.wait()
        
        # Build embed from modal data
        color = modal.parse_color(modal.embed_color.value)
        
        embed = discord.Embed(
            title=modal.embed_title.value,
            description=modal.embed_description.value,
            color=color,
            timestamp=discord.utils.utcnow()  # Current time
        )
        
        # Add footer if provided
        if modal.embed_footer.value:
            embed.set_footer(text=modal.embed_footer.value)
        
        # Store embed data for editing/sending later
        embed_data = {
            "title": modal.embed_title.value,
            "description": modal.embed_description.value,
            "color_hex": modal.embed_color.value,
            "footer": modal.embed_footer.value
        }
        
        # Create view with buttons
        view = EmbedPreviewView(
            author_id=interaction.user.id,
            embed_data=embed_data
        )
        
        # Send preview with buttons
        # followup is used because we already responded with the modal
        preview_msg = await interaction.followup.send(
            content="✨ **Embed Preview:**\nReview your embed and choose an action below.",
            embed=embed,
            view=view,
            ephemeral=True  # Only visible to command user
        )
        
        # Store message reference for later deletion
        view.message = preview_msg
    
    @embed_group.command(name="preset", description="Use a pre-made embed template")
    @app_commands.describe(template="Choose an embed template")
    @app_commands.checks.has_permissions(manage_messages=True)
    async def embed_preset(
        self,
        interaction: discord.Interaction,
        template: str
    ):
        """
        Quick-send a pre-made embed template.
        
        Args:
            template: Name of the preset (announcement, payment, rules, welcome)
        """
        # Check if template exists
        if template not in self.presets:
            available = ", ".join(self.presets.keys())
            await interaction.response.send_message(
                f"❌ Template `{template}` not found!\n**Available:** {available}",
                ephemeral=True
            )
            return
        
        # Get preset data
        preset = self.presets[template]
        
        # Build embed from preset
        color_hex = preset.get("color", "5865F2")
        try:
            color = discord.Color(int(color_hex, 16))
        except ValueError:
            color = discord.Color.blurple()
        
        embed = discord.Embed(
            title=preset.get("title", ""),
            description=preset.get("description", ""),
            color=color,
            timestamp=discord.utils.utcnow()
        )
        
        # Add footer if exists
        if preset.get("footer"):
            embed.set_footer(text=preset["footer"])
        
        # Add thumbnail if exists
        if preset.get("thumbnail"):
            embed.set_thumbnail(url=preset["thumbnail"])
        
        # Add image if exists
        if preset.get("image"):
            embed.set_image(url=preset["image"])
        
        # Add fields if they exist
        if "fields" in preset:
            for field in preset["fields"]:
                embed.add_field(
                    name=field.get("name", "Field"),
                    value=field.get("value", "Value"),
                    inline=field.get("inline", False)
                )
        
        # Store data for the view
        embed_data = {
            "title": preset.get("title", ""),
            "description": preset.get("description", ""),
            "color_hex": color_hex,
            "footer": preset.get("footer", "")
        }
        
        # Create preview with buttons
        view = EmbedPreviewView(
            author_id=interaction.user.id,
            embed_data=embed_data
        )
        
        preview_msg = await interaction.response.send_message(
            content=f"✨ **Preset: {template.title()}**\nReview and choose an action below.",
            embed=embed,
            view=view,
            ephemeral=True
        )
        
        # Store message reference
        view.message = await interaction.original_response()
    
    @embed_preset.autocomplete('template')
    async def preset_autocomplete(
        self,
        interaction: discord.Interaction,
        current: str
    ) -> list[app_commands.Choice[str]]:
        """
        Autocomplete for template parameter.
        Shows available templates as user types.
        """
        # Filter templates based on what user has typed
        choices = [
            app_commands.Choice(name=name.title(), value=name)
            for name in self.presets.keys()
            if current.lower() in name.lower()
        ]
        return choices[:25]  # Discord limit: 25 choices
    
    @embed_group.command(name="info", description="Learn how to use the embed builder")
    async def embed_info(self, interaction: discord.Interaction):
        """
        Help command explaining how to use the embed builder.
        """
        embed = discord.Embed(
            title="📚 Embed Builder Guide",
            description="Learn how to create beautiful embeds!",
            color=discord.Color.blurple()
        )
        
        embed.add_field(
            name="🆕 Create Custom Embed",
            value="Use `/embed create` to open an interactive form. Fill in the fields and submit to see a preview!",
            inline=False
        )
        
        embed.add_field(
            name="📋 Use Presets",
            value="Use `/embed preset <template>` to quickly send pre-made embeds. Available templates: **announcement**, **payment**, **rules**, **welcome**",
            inline=False
        )
        
        embed.add_field(
            name="🎨 Color Codes",
            value="Use hex codes for colors (e.g., `#5865F2` or `5865F2`). Common colors:\n• `#5865F2` - Discord Blurple\n• `#57F287` - Green\n• `#FEE75C` - Yellow\n• `#ED4245` - Red",
            inline=False
        )
        
        embed.add_field(
            name="✨ Preview Features",
            value="After creating an embed:\n• ✅ **Confirm & Send** - Choose a channel to send\n• ✏️ **Edit** - Modify your embed\n• ❌ **Cancel** - Delete the preview",
            inline=False
        )
        
        embed.add_field(
            name="🔒 Permissions",
            value="You need **Manage Messages** permission to create embeds.",
            inline=False
        )
        
        embed.set_footer(text="Made with ❤️ using discord.py")
        
        await interaction.response.send_message(embed=embed, ephemeral=True)
    
    # Error Handling
    @embed_create.error
    @embed_preset.error
    async def embed_error(self, interaction: discord.Interaction, error: app_commands.AppCommandError):
        """
        Handle errors for embed commands.
        Most common: Missing permissions.
        """
        if isinstance(error, app_commands.MissingPermissions):
            await interaction.response.send_message(
                "❌ You need **Manage Messages** permission to use this command!",
                ephemeral=True
            )
        else:
            # Log unexpected errors
            print(f"Error in embed command: {error}")
            await interaction.response.send_message(
                "❌ An error occurred while processing your request.",
                ephemeral=True
            )

# Required function to load the cog
async def setup(bot):
    """
    Called by bot.load_extension() to add this cog to the bot.
    """
    await bot.add_cog(EmbedBuilder(bot))