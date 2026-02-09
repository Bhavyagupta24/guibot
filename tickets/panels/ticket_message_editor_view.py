import discord
from modals.embed_modals import (
    TitleModal,
    DescriptionModal,
    ColorModal,
    FooterModal,
    ImagesModal,
    AddFieldModal,
    RemoveFieldModal
)
from tickets.constants import DEFAULT_TICKET_TEMPLATE


class TicketMessageEditorView(discord.ui.View):
    """
    Per-option Ticket Message Editor (Embed-style)
    """

    def __init__(self, option: dict, refresh_callback):
        super().__init__(timeout=600)

        self.option = option
        self.refresh_callback = refresh_callback

        # Ensure template exists
        if "ticket_message" not in self.option:
            self.option["ticket_message"] = DEFAULT_TICKET_TEMPLATE.copy()

        self.template = self.option["ticket_message"]

    async def refresh(self):
        await self.refresh_callback()

    # ───────────── ROW 0 ─────────────
    @discord.ui.button(label="Title", style=discord.ButtonStyle.secondary, row=0)
    async def edit_title(self, interaction: discord.Interaction, _):
        modal = TitleModal(self.template["title"])
        await interaction.response.send_modal(modal)
        await modal.wait()
        self.template["title"] = modal.title_input.value
        await self.refresh()

    @discord.ui.button(label="Description", style=discord.ButtonStyle.secondary, row=0)
    async def edit_desc(self, interaction: discord.Interaction, _):
        modal = DescriptionModal(self.template["description"])
        await interaction.response.send_modal(modal)
        await modal.wait()
        self.template["description"] = modal.description_input.value
        await self.refresh()

    @discord.ui.button(label="Color", style=discord.ButtonStyle.secondary, row=0)
    async def edit_color(self, interaction: discord.Interaction, _):
        modal = ColorModal(self.template["color"])
        await interaction.response.send_modal(modal)
        await modal.wait()
        self.template["color"] = modal.color_input.value
        await self.refresh()

    # ───────────── ROW 1 ─────────────
    @discord.ui.button(label="Footer", style=discord.ButtonStyle.secondary, row=1)
    async def edit_footer(self, interaction: discord.Interaction, _):
        modal = FooterModal(
            self.template["footer_text"],
            self.template["footer_icon"]
        )
        await interaction.response.send_modal(modal)
        await modal.wait()
        self.template["footer_text"] = modal.footer_text.value
        self.template["footer_icon"] = modal.footer_icon.value
        await self.refresh()

    @discord.ui.button(label="Images", style=discord.ButtonStyle.secondary, row=1)
    async def edit_images(self, interaction: discord.Interaction, _):
        modal = ImagesModal(
            self.template["image_url"],
            self.template["thumbnail_url"]
        )
        await interaction.response.send_modal(modal)
        await modal.wait()
        self.template["image_url"] = modal.image_url.value
        self.template["thumbnail_url"] = modal.thumbnail_url.value
        await self.refresh()

    @discord.ui.button(label="Add Field", style=discord.ButtonStyle.secondary, row=1)
    async def add_field(self, interaction: discord.Interaction, _):
        modal = AddFieldModal()
        await interaction.response.send_modal(modal)
        await modal.wait()

        inline = modal.field_inline.value.lower() in ("yes", "y", "true", "1")

        self.template["fields"].append({
            "name": modal.field_name.value,
            "value": modal.field_value.value,
            "inline": inline
        })
        await self.refresh()

    @discord.ui.button(label="Remove Field", style=discord.ButtonStyle.secondary, row=1)
    async def remove_field(self, interaction: discord.Interaction, _):
        if not self.template["fields"]:
            await interaction.response.send_message(
                "❌ No fields to remove.",
                ephemeral=True
            )
            return

        modal = RemoveFieldModal(len(self.template["fields"]))
        await interaction.response.send_modal(modal)
        await modal.wait()

        try:
            self.template["fields"].pop(int(modal.field_index.value) - 1)
            await self.refresh()
        except Exception:
            await interaction.followup.send(
                "❌ Invalid field index.",
                ephemeral=True
            )

    # ───────────── ROW 2 ─────────────
    @discord.ui.button(label="Reset", style=discord.ButtonStyle.danger, row=2)
    async def reset(self, interaction: discord.Interaction, _):
        self.option["ticket_message"] = DEFAULT_TICKET_TEMPLATE.copy()
        self.template = self.option["ticket_message"]

        await interaction.response.send_message(
            "🔄 Ticket message reset to default.",
            ephemeral=True
        )
        await self.refresh()

    @discord.ui.button(label="Close Editor", style=discord.ButtonStyle.secondary, row=2)
    async def close(self, interaction: discord.Interaction, _):
        for item in self.children:
            item.disabled = True

        await interaction.response.send_message(
            "✅ Ticket message editor closed.",
            ephemeral=True
        )
        self.stop()
