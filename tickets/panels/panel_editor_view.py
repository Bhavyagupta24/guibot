import discord
import uuid

from modals.embed_modals import (
    TitleModal,
    DescriptionModal,
    ColorModal,
    FooterModal,
    ImagesModal,
    AddFieldModal,
    RemoveFieldModal
)

from tickets.modals.panel_modals import (
    AddTicketOptionModal,
    AddTicketOptionAdvancedModal,
    RemoveTicketOptionModal
)

from tickets.panels.panel_storage import PanelStorage
from tickets.panels.option_selector_view import TicketOptionSelectorView
from tickets.panels.ticket_message_editor_view import TicketMessageEditorView


class TicketPanelEditorView(discord.ui.View):
    """
    Full Ticket Panel Editor
    Supports:
    - Ticket options
    - Embed-only options
    """

    def __init__(self, author_id: int, guild_id: int, panel_name: str):
        super().__init__(timeout=600)

        self.author_id = author_id
        self.guild_id = guild_id
        self.panel_name = panel_name
        self.storage = PanelStorage()
        self.message: discord.Message | None = None

        # Panel data
        self.panel = {
            "title": "Support Panel",
            "description": "Select an option below",
            "color": "",
            "footer_text": "",
            "footer_icon": "",
            "image_url": "",
            "thumbnail_url": "",
            "fields": [],
            "style": "buttons",
            "options": []
        }

    # ───────────── ACCESS CONTROL ─────────────
    async def interaction_check(self, interaction: discord.Interaction) -> bool:
        if interaction.user.id != self.author_id:
            await interaction.response.send_message(
                "❌ This panel editor is not yours.",
                ephemeral=True
            )
            return False
        return True

    # ───────────── PREVIEW ─────────────
    def build_preview(self) -> discord.Embed:
        embed = discord.Embed(
            title=self.panel["title"] or None,
            description=self.panel["description"] or None,
            color=ColorModal.parse_color(self.panel["color"])
        )

        if self.panel["footer_text"]:
            embed.set_footer(
                text=self.panel["footer_text"],
                icon_url=self.panel["footer_icon"] or None
            )

        if self.panel["image_url"]:
            embed.set_image(url=self.panel["image_url"])

        if self.panel["thumbnail_url"]:
            embed.set_thumbnail(url=self.panel["thumbnail_url"])

        for field in self.panel["fields"]:
            embed.add_field(
                name=field["name"],
                value=field["value"],
                inline=field["inline"]
            )

        if self.panel["options"]:
            embed.add_field(
                name="📌 Panel Options",
                value="\n".join(
                    f"{opt.get('emoji','')} **{opt['label']}** — {opt['description']}"
                    for opt in self.panel["options"]
                ),
                inline=False
            )

        return embed

    async def refresh(self):
        if self.message:
            await self.message.edit(embed=self.build_preview(), view=self)

    # ───────────── BASIC EMBED EDITING ─────────────
    @discord.ui.button(label="Title", style=discord.ButtonStyle.secondary, row=0)
    async def edit_title(self, interaction: discord.Interaction, _):
        modal = TitleModal(self.panel["title"])
        await interaction.response.send_modal(modal)
        await modal.wait()
        self.panel["title"] = modal.title_input.value
        await self.refresh()

    @discord.ui.button(label="Description", style=discord.ButtonStyle.secondary, row=0)
    async def edit_description(self, interaction: discord.Interaction, _):
        modal = DescriptionModal(self.panel["description"])
        await interaction.response.send_modal(modal)
        await modal.wait()
        self.panel["description"] = modal.description_input.value
        await self.refresh()

    @discord.ui.button(label="Color", style=discord.ButtonStyle.secondary, row=0)
    async def edit_color(self, interaction: discord.Interaction, _):
        modal = ColorModal(self.panel["color"])
        await interaction.response.send_modal(modal)
        await modal.wait()
        self.panel["color"] = modal.color_input.value
        await self.refresh()

    # ───────────── MEDIA & FIELDS ─────────────
    @discord.ui.button(label="Footer", style=discord.ButtonStyle.secondary, row=1)
    async def edit_footer(self, interaction: discord.Interaction, _):
        modal = FooterModal(
            self.panel["footer_text"],
            self.panel["footer_icon"]
        )
        await interaction.response.send_modal(modal)
        await modal.wait()
        self.panel["footer_text"] = modal.footer_text.value
        self.panel["footer_icon"] = modal.footer_icon.value
        await self.refresh()

    @discord.ui.button(label="Images", style=discord.ButtonStyle.secondary, row=1)
    async def edit_images(self, interaction: discord.Interaction, _):
        modal = ImagesModal(
            self.panel["image_url"],
            self.panel["thumbnail_url"]
        )
        await interaction.response.send_modal(modal)
        await modal.wait()
        self.panel["image_url"] = modal.image_url.value
        self.panel["thumbnail_url"] = modal.thumbnail_url.value
        await self.refresh()

    @discord.ui.button(label="Add Field", style=discord.ButtonStyle.secondary, row=1)
    async def add_field(self, interaction: discord.Interaction, _):
        modal = AddFieldModal()
        await interaction.response.send_modal(modal)
        await modal.wait()

        self.panel["fields"].append({
            "name": modal.field_name.value,
            "value": modal.field_value.value,
            "inline": modal.field_inline.value.lower() in ("yes", "y", "true", "1")
        })
        await self.refresh()

    @discord.ui.button(label="Remove Field", style=discord.ButtonStyle.secondary, row=1)
    async def remove_field(self, interaction: discord.Interaction, _):
        if not self.panel["fields"]:
            await interaction.response.send_message("❌ No fields to remove.", ephemeral=True)
            return

        modal = RemoveFieldModal(len(self.panel["fields"]))
        await interaction.response.send_modal(modal)
        await modal.wait()

        try:
            self.panel["fields"].pop(int(modal.field_index.value) - 1)
            await self.refresh()
        except Exception:
            await interaction.followup.send("❌ Invalid field index.", ephemeral=True)

    @discord.ui.button(label="Add Option", style=discord.ButtonStyle.success, row=2)
    async def add_option(self, interaction: discord.Interaction, _):
        print("DEBUG: add_option button clicked!")
        
        modal = AddTicketOptionModal()
        await interaction.response.send_modal(modal)
        await modal.wait()
        print("DEBUG: Modal submitted!")

        try:
            category_raw = (modal.category_id.value or "").strip()
            print(f"DEBUG: category_raw = '{category_raw}'")

            option = {
                "id": uuid.uuid4().hex[:8],
                "label": modal.label.value.strip(),
                "description": modal.description.value.strip(),
                "emoji": modal.emoji.value.strip() or None,
            }
            print(f"DEBUG: Basic option created: {option}")

            # Ticket option
            if category_raw:
                print("DEBUG: Creating ticket option...")
                if not category_raw.isdigit():
                    await interaction.followup.send(
                        "❌ Category ID must be numeric or empty.",
                        ephemeral=True
                    )
                    return

                option.update({
                    "type": "ticket",
                    "category_id": int(category_raw),
                    "ticket_prefix": None,  # Can be added via edit later
                    "limit": None  # Unlimited tickets
                })
                print(f"DEBUG: Ticket option finalized: {option}")

            # Embed-only option
            else:
                print("DEBUG: Creating embed option...")
                embed_name_input = modal.embed_name.value.strip() if modal.embed_name.value else ""
                print(f"DEBUG: embed_name_input = '{embed_name_input}'")
                
                if not embed_name_input:
                    await interaction.followup.send(
                        "❌ For embed-type options, you must provide an embed name!\n"
                        "💡 Use `/embed create` to create an embed first.\n"
                        "📝 Then enter the exact embed name in the 'Embed Name' field.",
                        ephemeral=True
                    )
                    return
                
                from utils.embed_storage import EmbedStorage
                storage = EmbedStorage()
                if not storage.embed_exists(self.guild_id, embed_name_input):
                    await interaction.followup.send(
                        f"❌ Embed **{embed_name_input}** not found!\n"
                        f"💡 Use `/embed list` to see available embeds.",
                        ephemeral=True
                    )
                    return
                
                option.update({
                    "type": "embed",
                    "embed_name": embed_name_input
                })
                print(f"DEBUG: Embed option finalized: {option}")
            
            # 🔐 CRITICAL: Add panel_name so ticket creation knows which panel it belongs to
            option["panel_name"] = self.panel_name
            
            print(f"DEBUG: About to append option to panel...")
            self.panel["options"].append(option)
            print(f"DEBUG: Option appended! Panel now has {len(self.panel['options'])} options")
            
            print(f"DEBUG: Sending followup message...")
            await interaction.followup.send(
                f"✅ Option **{option['label']}** added!",
                ephemeral=True
            )
            print(f"DEBUG: Followup sent!")
            
            print(f"DEBUG: About to call refresh...")
            await self.refresh()
            print(f"DEBUG: Refresh complete!")
            
        except Exception as e:
            print(f"ERROR in add_option: {type(e).__name__}: {e}")
            import traceback
            traceback.print_exc()
            try:
                await interaction.followup.send(
                    f"❌ Error: {str(e)}",
                    ephemeral=True
                )
            except:
                print("Could not send error message")

    @discord.ui.button(label="Remove Option", style=discord.ButtonStyle.danger, row=2)
    async def remove_option(self, interaction: discord.Interaction, _):
        if not self.panel["options"]:
            await interaction.response.send_message("❌ No options to remove.", ephemeral=True)
            return

        modal = RemoveTicketOptionModal(len(self.panel["options"]))
        await interaction.response.send_modal(modal)
        await modal.wait()

        try:
            self.panel["options"].pop(int(modal.index.value) - 1)
            await self.refresh()
        except Exception:
            await interaction.followup.send("❌ Invalid option index.", ephemeral=True)

    @discord.ui.button(label="Toggle Style", style=discord.ButtonStyle.secondary, row=2)
    async def toggle_style(self, interaction: discord.Interaction, _):
        self.panel["style"] = "dropdown" if self.panel["style"] == "buttons" else "buttons"
        await interaction.response.send_message(
            f"🔁 Style set to **{self.panel['style']}**",
            ephemeral=True
        )

    # ───────────── EDIT TICKET MESSAGE ─────────────
    @discord.ui.button(label="Edit Ticket Message", style=discord.ButtonStyle.primary, row=3)
    async def edit_ticket_message(self, interaction: discord.Interaction, _):
        await interaction.response.defer(ephemeral=True)

        ticket_options = [o for o in self.panel["options"] if o.get("type") == "ticket"]
        if not ticket_options:
            await interaction.followup.send(
                "❌ No ticket options available.\n💡 Add a ticket option first by clicking 'Add Option'.",
                ephemeral=True
            )
            return

        async def on_select(select_inter, option_id):
            try:
                option = next((o for o in ticket_options if o.get("id") == option_id), None)
                if not option:
                    if not select_inter.response.is_done():
                        await select_inter.response.send_message(
                            "❌ Option not found.",
                            ephemeral=True
                        )
                    else:
                        await select_inter.followup.send(
                            "❌ Option not found.",
                            ephemeral=True
                        )
                    return

                editor = TicketMessageEditorView(option, self.refresh)
                
                if not select_inter.response.is_done():
                    await select_inter.response.send_message(
                        f"✏️ Editing ticket message for **{option['label']}**",
                        view=editor,
                        ephemeral=True
                    )
                else:
                    await select_inter.followup.send(
                        f"✏️ Editing ticket message for **{option['label']}**",
                        view=editor,
                        ephemeral=True
                    )
            except Exception as e:
                print(f"Error in on_select: {e}")
                if not select_inter.response.is_done():
                    await select_inter.response.send_message(
                        f"❌ Error: {str(e)}",
                        ephemeral=True
                    )
                else:
                    await select_inter.followup.send(
                        f"❌ Error: {str(e)}",
                        ephemeral=True
                    )

        selector = TicketOptionSelectorView(ticket_options, on_select)
        await interaction.followup.send(
            "📌 Select a ticket option to edit:",
            view=selector,
            ephemeral=True
        )

    # ───────────── SAVE / CLOSE ─────────────
    @discord.ui.button(label="Save", style=discord.ButtonStyle.primary, row=3)
    async def save_panel(self, interaction: discord.Interaction, _):
        self.storage.save_panel(self.guild_id, self.panel_name, self.panel)
        await interaction.response.send_message(
            f"✅ Panel **{self.panel_name}** saved.",
            ephemeral=True
        )

    @discord.ui.button(label="Send", style=discord.ButtonStyle.success, row=3)
    async def send_panel(self, interaction: discord.Interaction, _):
        await interaction.response.send_message(
            "ℹ️ Use `/ticket panel send` to deploy this panel.",
            ephemeral=True
        )

    @discord.ui.button(label="Close Editor", style=discord.ButtonStyle.secondary, row=3)
    async def close_editor(self, interaction: discord.Interaction, _):
        for child in self.children:
            child.disabled = True
        await self.message.edit(embed=self.build_preview(), view=self)
        self.stop()
