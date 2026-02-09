import discord

from tickets.ticket_manager import TicketManager
from tickets.utils.emoji_parser import parse_emoji
from tickets.panels.panel_storage import PanelStorage
from utils.embed_storage import EmbedStorage


class TicketButtonView(discord.ui.View):
    """
    Persistent view for ticket panel buttons.
    Supports BOTH:
    - ticket options (create ticket)
    - embed options (send embed ephemerally)
    """

    def __init__(self, guild_id: int, panel_name: str):
        super().__init__(timeout=None)
        
        self.guild_id = guild_id
        self.panel_name = panel_name
        self.storage = PanelStorage()
        
        # ✅ FIX: Load panel to get options
        panel = self.storage.get_panel(guild_id, panel_name)
        if not panel:
            return
        
        options = panel.get("options", [])
        if not options:
            return

        for option in options:
            self.add_item(TicketButton(option, guild_id))


class TicketButton(discord.ui.Button):
    def __init__(self, option: dict, guild_id: int):
        self.option = option
        self.guild_id = guild_id

        emoji = parse_emoji(option.get("emoji"))

        super().__init__(
            label=option.get("label", "Option"),
            style=discord.ButtonStyle.primary,
            emoji=emoji,
            custom_id=f"panel_option:{option['id']}"  # ✅ STABLE ID
        )

    async def callback(self, interaction: discord.Interaction):
        option_type = self.option.get("type", "ticket")

        # ───────────── TICKET OPTION ─────────────
        if option_type == "ticket":
            await TicketManager.create_ticket(interaction, self.option)
            return

        # ───────────── EMBED OPTION ─────────────
        if option_type == "embed":
            embed_name = self.option.get("embed_name")

            if not embed_name:
                await interaction.response.send_message(
                    "❌ No embed linked to this option.",
                    ephemeral=True
                )
                return

            storage = EmbedStorage()
            embed_data = storage.load_embed(self.guild_id, embed_name)

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