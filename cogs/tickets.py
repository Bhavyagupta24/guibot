import discord
from discord import app_commands
from discord.ext import commands

from modals.embed_modals import ColorModal
from tickets.panels.panel_editor_view import TicketPanelEditorView
from tickets.panels.panel_storage import PanelStorage
from tickets.views.ticket_button_view import TicketButtonView
from tickets.views.ticket_dropdown_view import TicketDropdownView


class TicketCog(commands.Cog):
    def __init__(self, bot):
        self.bot = bot
        self.storage = PanelStorage()

    # ===============================
    # /ticket
    # ===============================
    ticket = app_commands.Group(
        name="ticket",
        description="Ticket system commands"
    )

    # ===============================
    # /ticket panel
    # ===============================
    panel = app_commands.Group(
        name="panel",
        description="Ticket panel management",
        parent=ticket
    )

    # ───────────── CREATE PANEL ─────────────
    @panel.command(name="create")
    async def panel_create(self, interaction: discord.Interaction, name: str):
        if not interaction.guild:
            await interaction.response.send_message(
                "❌ This command can only be used in a server.",
                ephemeral=True
            )
            return

        if not interaction.user.guild_permissions.manage_guild:
            await interaction.response.send_message(
                "❌ You need **Manage Server** permission.",
                ephemeral=True
            )
            return

        if self.storage.get_panel(interaction.guild.id, name):
            await interaction.response.send_message(
                f"❌ Panel **{name}** already exists.",
                ephemeral=True
            )
            return

        view = TicketPanelEditorView(
            author_id=interaction.user.id,
            guild_id=interaction.guild.id,
            panel_name=name
        )

        embed = view.build_preview()
        await interaction.response.send_message(embed=embed, view=view)

        view.message = await interaction.original_response()
        await view.refresh()

    # ───────────── EDIT PANEL ─────────────
    @panel.command(name="edit")
    async def panel_edit(self, interaction: discord.Interaction, name: str):
        panel = self.storage.get_panel(interaction.guild.id, name)
        if not panel:
            await interaction.response.send_message(
                f"❌ Panel **{name}** not found.",
                ephemeral=True
            )
            return

        view = TicketPanelEditorView(
            author_id=interaction.user.id,
            guild_id=interaction.guild.id,
            panel_name=name
        )
        view.panel = panel

        embed = view.build_preview()
        await interaction.response.send_message(embed=embed, view=view)

        view.message = await interaction.original_response()
        await view.refresh()

    # ───────────── LIST PANELS ─────────────
    @panel.command(name="list")
    async def panel_list(self, interaction: discord.Interaction):
        panels = self.storage.load_panels(interaction.guild.id)
        if not panels:
            await interaction.response.send_message(
                "❌ No ticket panels created yet.",
                ephemeral=True
            )
            return

        embed = discord.Embed(
            title="🎫 Ticket Panels",
            description="\n".join(f"• `{name}`" for name in panels.keys()),
            color=discord.Color.blurple()
        )

        await interaction.response.send_message(embed=embed, ephemeral=True)

    # ───────────── DELETE PANEL ─────────────
    @panel.command(name="delete")
    async def panel_delete(self, interaction: discord.Interaction, name: str):
        panels = self.storage.load_panels(interaction.guild.id)
        if name not in panels:
            await interaction.response.send_message(
                f"❌ Panel **{name}** not found.",
                ephemeral=True
            )
            return

        panels.pop(name)
        self.storage.save_panels(interaction.guild.id, panels)

        await interaction.response.send_message(
            f"🗑 Deleted panel **{name}**.",
            ephemeral=True
        )

    # ───────────── SEND PANEL ─────────────
    @panel.command(name="send")
    async def panel_send(
        self,
        interaction: discord.Interaction,
        name: str,
        channel: discord.TextChannel | None = None
    ):
        await interaction.response.defer(ephemeral=True)

        panel = self.storage.get_panel(interaction.guild.id, name)
        if not panel:
            await interaction.followup.send(
                f"❌ Panel **{name}** not found.",
                ephemeral=True
            )
            return

        target_channel = channel or interaction.channel

        try:
            color = ColorModal.parse_color(panel.get("color", ""))
            embed = discord.Embed(
                title=panel.get("title"),
                description=panel.get("description"),
                color=color
            )

            if panel.get("footer_text"):
                embed.set_footer(
                    text=panel["footer_text"],
                    icon_url=panel.get("footer_icon") or None
                )

            if panel.get("image_url"):
                embed.set_image(url=panel["image_url"])

            if panel.get("thumbnail_url"):
                embed.set_thumbnail(url=panel["thumbnail_url"])

            for field in panel.get("fields", []):
                embed.add_field(
                    name=field["name"],
                    value=field["value"],
                    inline=field["inline"]
                )

            options = panel.get("options", [])
            if not options:
                await interaction.followup.send(
                    "❌ Panel has no ticket options.",
                    ephemeral=True
                )
                return

            if panel.get("style") == "dropdown" and len(options) > 1:
                view = TicketDropdownView(
                    guild_id=interaction.guild.id,
                    panel_name=name
                )
            else:
                view = TicketButtonView(
                    guild_id=interaction.guild.id,
                    panel_name=name
                )

            await target_channel.send(embed=embed, view=view)

        except Exception as e:
            print("❌ PANEL SEND ERROR:", e)
            await interaction.followup.send(
                "❌ An internal error occurred while sending the panel.",
                ephemeral=True
            )
            return

        await interaction.followup.send(
            f"✅ Panel **{name}** sent in {target_channel.mention}",
            ephemeral=True
        )

    # ===============================
    # /ticket set-transcript
    # ===============================
    @ticket.command(name="set-transcript")
    @app_commands.default_permissions(administrator=True)
    async def set_transcript_channel(
        self,
        interaction: discord.Interaction,
        panel_name: str,
        channel: discord.TextChannel
    ):
        panel = self.storage.get_panel(interaction.guild.id, panel_name)
        if not panel:
            await interaction.response.send_message(
                f"❌ Panel **{panel_name}** not found.",
                ephemeral=True
            )
            return

        if not channel.permissions_for(interaction.guild.me).send_messages:
            await interaction.response.send_message(
                f"❌ I can’t send messages in {channel.mention}.",
                ephemeral=True
            )
            return

        panel["transcript_channel_id"] = channel.id
        self.storage.save_panel(interaction.guild.id, panel_name, panel)

        await interaction.response.send_message(
            f"✅ Transcript channel for **{panel_name}** set to {channel.mention}",
            ephemeral=True
        )

    # ===============================
    # /ticket view-config
    # ===============================
    @ticket.command(name="view-config")
    @app_commands.default_permissions(administrator=True)
    async def view_panel_config(
        self,
        interaction: discord.Interaction,
        panel_name: str
    ):
        panel = self.storage.get_panel(interaction.guild.id, panel_name)
        if not panel:
            await interaction.response.send_message(
                f"❌ Panel **{panel_name}** not found.",
                ephemeral=True
            )
            return

        transcript_id = panel.get("transcript_channel_id")
        transcript_channel = (
            interaction.guild.get_channel(transcript_id)
            if transcript_id else None
        )

        embed = discord.Embed(
            title=f"📋 Panel Configuration: {panel_name}",
            color=discord.Color.blurple(),
            description=panel.get("description", "No description")
        )

        embed.add_field(name="Title", value=panel.get("title", "Not set"), inline=True)
        embed.add_field(name="Style", value=panel.get("style", "buttons"), inline=True)
        embed.add_field(name="Options", value=str(len(panel.get("options", []))), inline=True)
        embed.add_field(
            name="Transcript Channel",
            value=transcript_channel.mention if transcript_channel else "❌ Not set",
            inline=False
        )

        await interaction.response.send_message(embed=embed, ephemeral=True)

    # ===============================
    # AUTOCOMPLETE
    # ===============================
    async def panel_autocomplete(
        self,
        interaction: discord.Interaction,
        current: str
    ):
        panels = self.storage.load_panels(interaction.guild.id)
        return [
            app_commands.Choice(name=name, value=name)
            for name in panels
            if current.lower() in name.lower()
        ][:25]


async def setup(bot):
    await bot.add_cog(TicketCog(bot))
