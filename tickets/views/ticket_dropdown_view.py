# tickets/views/ticket_dropdown_view.py
import discord

from tickets.ticket_manager import TicketManager
from tickets.panels.panel_storage import PanelStorage
from tickets.utils.emoji_parser import parse_emoji
from utils.embed_storage import EmbedStorage


class TicketDropdownView(discord.ui.View):
    """
    Persistent dropdown view for ticket panels.
    Supports:
    - ticket options (create ticket)
    - embed options (send embed ephemerally)
    """

    def __init__(self, guild_id: int, panel_name: str):
        super().__init__(timeout=None)

        self.guild_id = guild_id
        self.panel_name = panel_name
        self.storage = PanelStorage()

        panel = self.storage.get_panel(guild_id, panel_name)
        if not panel:
            return

        options = panel.get("options", [])
        if not options:
            return

        self.add_item(TicketDropdown(options))


class TicketDropdown(discord.ui.Select):
    def __init__(self, options: list[dict]):
        self.options_data: dict[str, dict] = {}

        select_options: list[discord.SelectOption] = []

        for index, opt in enumerate(options):
            # ───────────── STABLE OPTION ID ─────────────
            option_id = opt.get("id")
            if not option_id:
                option_id = f"legacy_{index}"
                opt["id"] = option_id

            self.options_data[option_id] = opt

            select_options.append(
                discord.SelectOption(
                    label=opt.get("label", "Option")[:100],
                    description=(opt.get("description") or "")[:100],
                    emoji=parse_emoji(opt.get("emoji")),
                    value=option_id
                )
            )

        super().__init__(
            placeholder="Select an option…",
            min_values=1,
            max_values=1,
            custom_id="panel_dropdown",  # ✅ PERSISTENT ID
            options=select_options
        )

    async def callback(self, interaction: discord.Interaction):
        option_id = self.values[0]
        option = self.options_data.get(option_id)

        if not option:
            await interaction.response.send_message(
                "❌ This option is no longer valid.",
                ephemeral=True
            )
            return

        option_type = option.get("type", "ticket")

        # ───────────── TICKET OPTION ─────────────
        if option_type == "ticket":
            await TicketManager.create_ticket(interaction, option)
            return

# ───────────── EMBED OPTION ─────────────
        if option_type == "embed":
            embed_name = option.get("embed_name")

            if not embed_name:
                await interaction.response.send_message(
                    "❌ No embed linked to this option.",
                    ephemeral=True
                )
                return

            storage = EmbedStorage()
            embed_data = storage.load_embed(interaction.guild.id, embed_name)

            if not embed_data:
                await interaction.response.send_message(
                    f"❌ Embed **{embed_name}** no longer exists.",
                    ephemeral=True
                )
                return
            
            # ✅ FIX: Build the actual embed from stored data
            from modals.embed_modals import ColorModal
            
            embed = discord.Embed(
                title=embed_data.get("title") or None,
                description=embed_data.get("description") or None,
                color=ColorModal.parse_color(embed_data.get("color", ""))
            )
            
            if embed_data.get("author_name"):
                embed.set_author(
                    name=embed_data["author_name"],
                    url=embed_data.get("author_url") or None,
                    icon_url=embed_data.get("author_icon") or None
                )
            
            if embed_data.get("footer_text"):
                embed.set_footer(
                    text=embed_data["footer_text"],
                    icon_url=embed_data.get("footer_icon") or None
                )
            
            if embed_data.get("image_url"):
                embed.set_image(url=embed_data["image_url"])
            
            if embed_data.get("thumbnail_url"):
                embed.set_thumbnail(url=embed_data["thumbnail_url"])
            
            for field in embed_data.get("fields", []):
                embed.add_field(
                    name=field["name"],
                    value=field["value"],
                    inline=field["inline"]
                )

            await interaction.response.send_message(
                embed=embed,
                ephemeral=True
            )
            return

        # ───────────── FALLBACK ─────────────
        await interaction.response.send_message(
            "❌ Invalid panel option type.",
            ephemeral=True
        )
