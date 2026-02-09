import discord
from discord import app_commands
from discord.ext import commands

from views.embed_editor_view import EmbedEditorView
from utils.embed_storage import EmbedStorage
from views.link_button_view import LinkButtonView



class EmbedCog(commands.Cog):
    """
    Cog for embed creation, editing, and sending.
    """

    def __init__(self, bot):
        self.bot = bot
        self.storage = EmbedStorage()

    # ===============================
    # /embed command group
    # ===============================
    embed_group = app_commands.Group(
        name="embed",
        description="Create and manage embeds"
    )

    # ===============================
    # /embed create
    # ===============================
    @embed_group.command(
        name="create",
        description="Create and edit a custom embed interactively"
    )
    @app_commands.describe(
        embed_name="Name for your embed (for saving/loading)"
    )
    async def embed_create(
        self,
        interaction: discord.Interaction,
        embed_name: str
    ):
        if not interaction.guild:
            await interaction.response.send_message(
                "❌ This command can only be used in a server!",
                ephemeral=True
            )
            return

        editor = EmbedEditorView(
            author_id=interaction.user.id,
            embed_name=embed_name,
            guild_id=interaction.guild.id,
            storage=self.storage
        )

        initial_embed = editor.build_embed()

        await interaction.response.send_message(
            content=(
                f"🎨 **Embed Editor: {embed_name}**\n"
                "Use the buttons below to customize your embed!"
            ),
            embed=initial_embed,
            view=editor
        )

        editor.message = await interaction.original_response()

    # ===============================
    # /embed load
    # ===============================
    @embed_group.command(
        name="load",
        description="Load a saved embed to edit"
    )
    @app_commands.describe(
        embed_name="Name of the saved embed"
    )
    async def embed_load(
        self,
        interaction: discord.Interaction,
        embed_name: str
    ):
        if not interaction.guild:
            await interaction.response.send_message(
                "❌ This command can only be used in a server!",
                ephemeral=True
            )
            return

        embed_state = self.storage.load_embed(
            interaction.guild.id,
            embed_name
        )

        if not embed_state:
            await interaction.response.send_message(
                f"❌ No saved embed found with name **{embed_name}**!",
                ephemeral=True
            )
            return

        editor = EmbedEditorView(
            author_id=interaction.user.id,
            embed_name=embed_name,
            guild_id=interaction.guild.id,
            storage=self.storage
        )

        editor.embed_state = embed_state
        loaded_embed = editor.build_embed()

        await interaction.response.send_message(
            content=(
                f"📂 **Loaded Embed: {embed_name}**\n"
                "Edit and save your changes!"
            ),
            embed=loaded_embed,
            view=editor
        )

        editor.message = await interaction.original_response()

    # ===============================
    # /embed list
    # ===============================
    @embed_group.command(
        name="list",
        description="List all saved embeds in this server"
    )
    async def embed_list(
        self,
        interaction: discord.Interaction
    ):
        if not interaction.guild:
            await interaction.response.send_message(
                "❌ This command can only be used in a server!",
                ephemeral=True
            )
            return

        embed_names = self.storage.list_embeds(
            interaction.guild.id
        )

        if not embed_names:
            await interaction.response.send_message(
                "📭 No saved embeds found in this server!",
                ephemeral=True
            )
            return

        list_embed = discord.Embed(
            title="📚 Saved Embeds",
            description=(
                f"**{len(embed_names)}** saved embed(s) "
                "in this server:"
            ),
            color=discord.Color.blurple()
        )

        for i, name in enumerate(embed_names[:25], start=1):
            list_embed.add_field(
                name=f"{i}. {name}",
                value="Use `/embed load` to edit",
                inline=False
            )

        await interaction.response.send_message(
            embed=list_embed,
            ephemeral=True
        )

    # ===============================
    # /embed delete
    # ===============================
    @embed_group.command(
        name="delete",
        description="Delete a saved embed"
    )
    @app_commands.describe(
        embed_name="Name of the embed to delete"
    )
    async def embed_delete(
        self,
        interaction: discord.Interaction,
        embed_name: str
    ):
        if not interaction.guild:
            await interaction.response.send_message(
                "❌ This command can only be used in a server!",
                ephemeral=True
            )
            return

        success = self.storage.delete_embed(
            interaction.guild.id,
            embed_name
        )

        if success:
            await interaction.response.send_message(
                f"✅ Deleted embed **{embed_name}**!",
                ephemeral=True
            )
        else:
            await interaction.response.send_message(
                f"❌ No saved embed found with name **{embed_name}**!",
                ephemeral=True
            )

    # ===============================
    # /embed send  ✅ NEW COMMAND
    # ===============================
    @embed_group.command(
        name="send",
        description="Send a saved embed to a channel"
    )
    @app_commands.describe(
        embed_name="Name of the embed to send",
        channel="Channel to send the embed in (optional)"
    )
    async def embed_send(
        self,
        interaction: discord.Interaction,
        embed_name: str,
        channel: discord.TextChannel | None = None
    ):
        if not interaction.guild:
            await interaction.response.send_message(
                "❌ This command can only be used in a server!",
                ephemeral=True
            )
            return

        if not interaction.user.guild_permissions.manage_messages:
            await interaction.response.send_message(
                "❌ You need **Manage Messages** permission.",
                ephemeral=True
            )
            return

        embed_state = self.storage.load_embed(
            interaction.guild.id,
            embed_name
        )

        if not embed_state:
            await interaction.response.send_message(
                f"❌ No saved embed found with name **{embed_name}**!",
                ephemeral=True
            )
            return

        editor = EmbedEditorView(
            author_id=interaction.user.id,
            embed_name=embed_name,
            guild_id=interaction.guild.id,
            storage=self.storage
        )

        editor.embed_state = embed_state
        final_embed = editor.build_embed()

        target_channel = channel or interaction.channel
        buttons = embed_state.get("buttons", [])
        
        view = LinkButtonView(buttons) if buttons else None
        await target_channel.send(embed=final_embed, view=view)


        await interaction.response.send_message(
            f"✅ Embed **{embed_name}** sent in {target_channel.mention}",
            ephemeral=True
        )

    # ===============================
    # Autocomplete (load, delete, send)
    # ===============================
    @embed_load.autocomplete("embed_name")
    @embed_delete.autocomplete("embed_name")
    @embed_send.autocomplete("embed_name")
    async def embed_autocomplete(
        self,
        interaction: discord.Interaction,
        current: str
    ) -> list[app_commands.Choice[str]]:

        if not interaction.guild:
            return []

        embed_names = self.storage.list_embeds(
            interaction.guild.id
        )

        return [
            app_commands.Choice(
                name=name,
                value=name
            )
            for name in embed_names
            if current.lower() in name.lower()
        ][:25]


async def setup(bot):
    """Load the EmbedCog."""
    await bot.add_cog(EmbedCog(bot))
