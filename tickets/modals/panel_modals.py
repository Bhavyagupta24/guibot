import discord


class PanelInfoModal(discord.ui.Modal):
    """Edit panel title and description"""

    def __init__(self, title: str = "", description: str = ""):
        super().__init__(title="Edit Panel Info")

        self.title_input = discord.ui.TextInput(
            label="Panel Title",
            default=title,
            required=True,
            max_length=256
        )

        self.description_input = discord.ui.TextInput(
            label="Panel Description",
            default=description,
            style=discord.TextStyle.paragraph,
            required=True,
            max_length=4000
        )

        self.add_item(self.title_input)
        self.add_item(self.description_input)

    async def on_submit(self, interaction: discord.Interaction):
        await interaction.response.defer(ephemeral=True)


# ─────────────────────────────
# ADD TICKET OPTION MODAL - PART 1 (Basic Info - 5 fields max)
# ─────────────────────────────
class AddTicketOptionModal(discord.ui.Modal):
    """Add a ticket option to a panel - Part 1"""

    def __init__(self):
        super().__init__(title="Add Ticket Option - Part 1")

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

        self.category_id = discord.ui.TextInput(
            label="Category ID (leave empty for embed)",
            placeholder="Paste category ID or leave empty",
            required=False,
            max_length=20
        )

        self.embed_name = discord.ui.TextInput(
            label="Embed Name (if no category ID)",
            placeholder="my-embed-name",
            required=False,
            max_length=100
        )

        self.add_item(self.label)
        self.add_item(self.description)
        self.add_item(self.emoji)
        self.add_item(self.category_id)
        self.add_item(self.embed_name)

    async def on_submit(self, interaction: discord.Interaction):
        await interaction.response.defer(ephemeral=True)


# ��────────────────────────────
# ADD TICKET OPTION MODAL - PART 2 (Advanced Options)
# ─────────────────────────────
class AddTicketOptionAdvancedModal(discord.ui.Modal):
    """Add a ticket option to a panel - Part 2 (Advanced)"""

    def __init__(self):
        super().__init__(title="Add Ticket Option - Part 2 (Advanced)")

        self.ticket_prefix = discord.ui.TextInput(
            label="Ticket Prefix (optional)",
            placeholder="support / order / help",
            required=False,
            max_length=50
        )

        self.limit = discord.ui.TextInput(
            label="Max Tickets Per User (optional)",
            placeholder="Leave empty for unlimited",
            required=False,
            max_length=3
        )

        self.add_item(self.ticket_prefix)
        self.add_item(self.limit)

    async def on_submit(self, interaction: discord.Interaction):
        await interaction.response.defer(ephemeral=True)


class RemoveTicketOptionModal(discord.ui.Modal):
    """Remove a ticket option by index"""

    def __init__(self, count: int):
        super().__init__(title="Remove Ticket Option")

        self.index = discord.ui.TextInput(
            label=f"Option Number (1-{count})",
            placeholder="Enter option number",
            required=True,
            max_length=2
        )

        self.add_item(self.index)

    async def on_submit(self, interaction: discord.Interaction):
        await interaction.response.defer(ephemeral=True)