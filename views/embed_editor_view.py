import discord
from modals.embed_modals import (
    TitleModal, DescriptionModal, ColorModal, AuthorModal,
    FooterModal, ImagesModal, AddFieldModal, RemoveFieldModal,
    AddButtonModal, RemoveButtonModal
)


class EmbedEditorView(discord.ui.View):
    """
    Interactive control panel for editing embeds.
    """

    def __init__(self, author_id: int, embed_name: str, guild_id: int, storage):
        super().__init__(timeout=600)

        self.author_id = author_id
        self.embed_name = embed_name
        self.guild_id = guild_id
        self.storage = storage
        self.message = None

        self.embed_state = {
            "title": f"Embed: {embed_name}",
            "description": "Click the buttons below to edit this embed.",
            "color": "",
            "author_name": "",
            "author_url": "",
            "author_icon": "",
            "footer_text": "",
            "footer_icon": "",
            "image_url": "",
            "thumbnail_url": "",
            "fields": [],
            "buttons": []
        }

    async def interaction_check(self, interaction: discord.Interaction) -> bool:
        if interaction.user.id != self.author_id:
            await interaction.response.send_message(
                "❌ This embed editor is not yours!",
                ephemeral=True
            )
            return False
        return True

    # ───────────── EMBED BUILDER ─────────────
    def build_embed(self) -> discord.Embed:
        color = ColorModal.parse_color(self.embed_state["color"])

        embed = discord.Embed(
            title=self.embed_state["title"] or None,
            description=self.embed_state["description"] or None,
            color=color,
            timestamp=discord.utils.utcnow()
        )

        if self.embed_state["author_name"]:
            embed.set_author(
                name=self.embed_state["author_name"],
                url=self.embed_state["author_url"] or None,
                icon_url=self.embed_state["author_icon"] or None
            )

        if self.embed_state["footer_text"]:
            embed.set_footer(
                text=self.embed_state["footer_text"],
                icon_url=self.embed_state["footer_icon"] or None
            )

        if self.embed_state["image_url"]:
            embed.set_image(url=self.embed_state["image_url"])

        if self.embed_state["thumbnail_url"]:
            embed.set_thumbnail(url=self.embed_state["thumbnail_url"])

        for field in self.embed_state["fields"]:
            embed.add_field(
                name=field["name"],
                value=field["value"],
                inline=field["inline"]
            )

        return embed

    async def update_embed(self):
        if self.message:
            await self.message.edit(embed=self.build_embed(), view=self)

    # ───────────── ROW 0 ─────────────
    @discord.ui.button(label="Title", style=discord.ButtonStyle.secondary, row=0)
    async def title_button(self, interaction: discord.Interaction, _):
        modal = TitleModal(self.embed_state["title"])
        await interaction.response.send_modal(modal)
        await modal.wait()
        self.embed_state["title"] = modal.title_input.value
        await self.update_embed()

    @discord.ui.button(label="Description", style=discord.ButtonStyle.secondary, row=0)
    async def description_button(self, interaction: discord.Interaction, _):
        modal = DescriptionModal(self.embed_state["description"])
        await interaction.response.send_modal(modal)
        await modal.wait()
        self.embed_state["description"] = modal.description_input.value
        await self.update_embed()

    @discord.ui.button(label="Color", style=discord.ButtonStyle.secondary, row=0)
    async def color_button(self, interaction: discord.Interaction, _):
        modal = ColorModal(self.embed_state["color"])
        await interaction.response.send_modal(modal)
        await modal.wait()
        self.embed_state["color"] = modal.color_input.value
        await self.update_embed()

    @discord.ui.button(label="Author", style=discord.ButtonStyle.secondary, row=0)
    async def author_button(self, interaction: discord.Interaction, _):
        modal = AuthorModal(
            self.embed_state["author_name"],
            self.embed_state["author_url"],
            self.embed_state["author_icon"]
        )
        await interaction.response.send_modal(modal)
        await modal.wait()
        self.embed_state["author_name"] = modal.author_name.value
        self.embed_state["author_url"] = modal.author_url.value
        self.embed_state["author_icon"] = modal.author_icon.value
        await self.update_embed()

    # ───────────── ROW 1 ─────────────
    @discord.ui.button(label="Footer", style=discord.ButtonStyle.secondary, row=1)
    async def footer_button(self, interaction: discord.Interaction, _):
        modal = FooterModal(
            self.embed_state["footer_text"],
            self.embed_state["footer_icon"]
        )
        await interaction.response.send_modal(modal)
        await modal.wait()
        self.embed_state["footer_text"] = modal.footer_text.value
        self.embed_state["footer_icon"] = modal.footer_icon.value
        await self.update_embed()

    @discord.ui.button(label="Images", style=discord.ButtonStyle.secondary, row=1)
    async def images_button(self, interaction: discord.Interaction, _):
        modal = ImagesModal(
            self.embed_state["image_url"],
            self.embed_state["thumbnail_url"]
        )
        await interaction.response.send_modal(modal)
        await modal.wait()
        self.embed_state["image_url"] = modal.image_url.value
        self.embed_state["thumbnail_url"] = modal.thumbnail_url.value
        await self.update_embed()

    @discord.ui.button(label="Add Field", style=discord.ButtonStyle.secondary, row=1)
    async def add_field_button(self, interaction: discord.Interaction, _):
        if len(self.embed_state["fields"]) >= 25:
            await interaction.response.send_message("❌ Max 25 fields.", ephemeral=True)
            return

        modal = AddFieldModal()
        await interaction.response.send_modal(modal)
        await modal.wait()

        inline = modal.field_inline.value.lower() in ("yes", "y", "true", "1")
        self.embed_state["fields"].append({
            "name": modal.field_name.value,
            "value": modal.field_value.value,
            "inline": inline
        })
        await self.update_embed()

    @discord.ui.button(label="Remove Field", style=discord.ButtonStyle.secondary, row=1)
    async def remove_field_button(self, interaction: discord.Interaction, _):
        if not self.embed_state["fields"]:
            await interaction.response.send_message("❌ No fields.", ephemeral=True)
            return

        modal = RemoveFieldModal(len(self.embed_state["fields"]))
        await interaction.response.send_modal(modal)
        await modal.wait()

        try:
            index = int(modal.field_index.value) - 1
            self.embed_state["fields"].pop(index)
            await self.update_embed()
        except Exception:
            await interaction.followup.send("❌ Invalid index.", ephemeral=True)

    # ───────────── ROW 2 : BUTTON MANAGEMENT ─────────────
    @discord.ui.button(label="Buttons", style=discord.ButtonStyle.secondary, row=2)
    async def buttons_button(self, interaction: discord.Interaction, _):
        buttons = self.embed_state["buttons"]

        info = "**Current Buttons:**\n"
        if not buttons:
            info += "• None\n"
        else:
            for i, b in enumerate(buttons, 1):
                info += f"{i}. {b.get('emoji','')} {b['label']}\n"

        info += "\nChoose an action:"

        await interaction.response.send_message(
            info,
            view=ButtonManagerView(self),
            ephemeral=True
        )

    @discord.ui.button(label="Save", style=discord.ButtonStyle.secondary, row=2)
    async def save_button(self, interaction: discord.Interaction, _):
        success = self.storage.save_embed(
            self.guild_id,
            self.embed_name,
            self.embed_state
        )
        await interaction.response.send_message(
            "✅ Embed saved!" if success else "❌ Failed to save embed.",
            ephemeral=True
        )

    @discord.ui.button(label="Close Editor", style=discord.ButtonStyle.secondary, row=2)
    async def close_button(self, interaction: discord.Interaction, _):
        await interaction.response.send_message("✅ Editor closed.", ephemeral=True)
        for item in self.children:
            item.disabled = True
        await self.message.edit(embed=self.build_embed(), view=self)
        self.stop()


# ─────────────────────────────────────────────
# 🔧 BUTTON MANAGER VIEW
# ─────────────────────────────────────────────
class ButtonManagerView(discord.ui.View):
    def __init__(self, editor: EmbedEditorView):
        super().__init__(timeout=120)
        self.editor = editor

    @discord.ui.button(label="➕ Add Button", style=discord.ButtonStyle.success)
    async def add_button(self, interaction: discord.Interaction, _):
        if len(self.editor.embed_state["buttons"]) >= 5:
            await interaction.response.send_message(
                "❌ Discord allows max 5 buttons.",
                ephemeral=True
            )
            return

        modal = AddButtonModal()
        await interaction.response.send_modal(modal)
        await modal.wait()

        url = modal.url_input.value.strip()
        if not url.startswith(("http://", "https://")):
            await interaction.followup.send(
                "❌ URL must start with http:// or https://",
                ephemeral=True
            )
            return

        data = {
            "label": modal.label_input.value.strip(),
            "url": url
        }

        if modal.emoji_input.value:
            data["emoji"] = modal.emoji_input.value.strip()

        self.editor.embed_state["buttons"].append(data)

        await interaction.followup.send(
            f"✅ Button **{data['label']}** added!",
            ephemeral=True
        )

    @discord.ui.button(label="🗑 Remove Button", style=discord.ButtonStyle.danger)
    async def remove_button(self, interaction: discord.Interaction, _):
        buttons = self.editor.embed_state["buttons"]
        if not buttons:
            await interaction.response.send_message(
                "❌ No buttons to remove.",
                ephemeral=True
            )
            return

        modal = RemoveButtonModal(len(buttons))
        await interaction.response.send_modal(modal)
        await modal.wait()

        try:
            index = int(modal.index_input.value) - 1
            removed = buttons.pop(index)
            await interaction.followup.send(
                f"🗑 Removed **{removed['label']}**",
                ephemeral=True
            )
        except Exception:
            await interaction.followup.send(
                "❌ Invalid button number.",
                ephemeral=True
            )
