import discord


# ───────────────── PANEL INFO ─────────────────
class PanelInfoModal(discord.ui.Modal):
    def __init__(self, title="", description=""):
        super().__init__(title="Edit Panel Info")

        self.title_input = discord.ui.TextInput(
            label="Panel Title",
            default=title,
            required=True,
            max_length=256
        )

        self.desc_input = discord.ui.TextInput(
            label="Panel Description",
            default=description,
            style=discord.TextStyle.paragraph,
            required=True,
            max_length=4000
        )

        self.add_item(self.title_input)
        self.add_item(self.desc_input)

    async def on_submit(self, interaction: discord.Interaction):
        await interaction.response.defer(ephemeral=True)


# ───────────────── ADD OPTION ─────────────────
class AddTicketOptionModal(discord.ui.Modal):
    def __init__(self):
        super().__init__(title="Add Panel Option")

        self.label = discord.ui.TextInput(
            label="Option Label",
            placeholder="Order Support",
            required=True,
            max_length=80
        )

        self.description = discord.ui.TextInput(
            label="Option Description",
            placeholder="Get help with your order",
            required=True,
            max_length=100
        )

        self.emoji = discord.ui.TextInput(
            label="Emoji (Unicode or Custom)",
            placeholder="📦 or <:order:123456789>",
            required=False,
            max_length=100
        )

        self.action = discord.ui.TextInput(
            label="Action Type",
            placeholder="ticket or embed",
            default="ticket",
            required=True,
            max_length=10
        )

        self.embed_name = discord.ui.TextInput(
            label="Embed Name (only if embed)",
            placeholder="leave empty if ticket",
            required=False,
            max_length=100
        )

        self.category_id = discord.ui.TextInput(
            label="Category ID (only if ticket)",
            placeholder="Paste category ID",
            required=False,
            max_length=20
        )

        self.ticket_prefix = discord.ui.TextInput(
            label="Ticket Prefix (optional)",
            placeholder="support",
            required=False,
            max_length=32
        )

        self.add_item(self.label)
        self.add_item(self.description)
        self.add_item(self.emoji)
        self.add_item(self.action)
        self.add_item(self.embed_name)
        self.add_item(self.category_id)
        self.add_item(self.ticket_prefix)

    async def on_submit(self, interaction: discord.Interaction):
        await interaction.response.defer(ephemeral=True)


# ───────────────── REMOVE OPTION ─────────────────
class RemoveTicketOptionModal(discord.ui.Modal):
    def __init__(self, count: int):
        super().__init__(title="Remove Panel Option")

        self.index = discord.ui.TextInput(
            label=f"Option Number (1–{count})",
            placeholder="Enter option number",
            required=True,
            max_length=3
        )

        self.add_item(self.index)

    async def on_submit(self, interaction: discord.Interaction):
        await interaction.response.defer(ephemeral=True)
