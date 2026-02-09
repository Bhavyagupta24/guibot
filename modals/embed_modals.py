import discord


class TitleModal(discord.ui.Modal):
    """Modal for editing embed title."""

    def __init__(self, current_title: str = ""):
        super().__init__(title="Edit Embed Title")

        self.title_input = discord.ui.TextInput(
            label="Title",
            placeholder="Enter embed title...",
            default=current_title,
            required=False,
            max_length=256
        )
        self.add_item(self.title_input)

    async def on_submit(self, interaction: discord.Interaction):
        await interaction.response.defer()


class DescriptionModal(discord.ui.Modal):
    """Modal for editing embed description."""

    def __init__(self, current_description: str = ""):
        super().__init__(title="Edit Description")

        self.description_input = discord.ui.TextInput(
            label="Description",
            placeholder="Enter embed description...",
            style=discord.TextStyle.paragraph,
            default=current_description,
            required=False,
            max_length=4000
        )
        self.add_item(self.description_input)

    async def on_submit(self, interaction: discord.Interaction):
        await interaction.response.defer()


class ColorModal(discord.ui.Modal):
    """Modal for editing embed color."""

    def __init__(self, current_color: str = ""):
        super().__init__(title="Edit Color")

        self.color_input = discord.ui.TextInput(
            label="Color (Hex Code)",
            placeholder="#5865F2 or 5865F2 or leave empty for default",
            default=current_color,
            required=False,
            max_length=7
        )
        self.add_item(self.color_input)

    async def on_submit(self, interaction: discord.Interaction):
        await interaction.response.defer()

    @staticmethod
    def parse_color(color_input: str) -> discord.Color:
        if not color_input:
            return discord.Color.blurple()

        color_input = color_input.strip().lstrip("#")
        try:
            return discord.Color(int(color_input, 16))
        except ValueError:
            return discord.Color.blurple()


class AuthorModal(discord.ui.Modal):
    """Modal for editing embed author."""

    def __init__(self, current_name: str = "", current_url: str = "", current_icon: str = ""):
        super().__init__(title="Edit Author")

        self.author_name = discord.ui.TextInput(
            label="Author Name",
            placeholder="Enter author name...",
            default=current_name,
            required=False,
            max_length=256
        )

        self.author_url = discord.ui.TextInput(
            label="Author URL (optional)",
            placeholder="https://example.com",
            default=current_url,
            required=False,
            max_length=512
        )

        self.author_icon = discord.ui.TextInput(
            label="Author Icon URL (optional)",
            placeholder="https://example.com/icon.png",
            default=current_icon,
            required=False,
            max_length=512
        )

        self.add_item(self.author_name)
        self.add_item(self.author_url)
        self.add_item(self.author_icon)

    async def on_submit(self, interaction: discord.Interaction):
        await interaction.response.defer()


class FooterModal(discord.ui.Modal):
    """Modal for editing embed footer."""

    def __init__(self, current_text: str = "", current_icon: str = ""):
        super().__init__(title="Edit Footer")

        self.footer_text = discord.ui.TextInput(
            label="Footer Text",
            placeholder="Enter footer text...",
            default=current_text,
            required=False,
            max_length=2048
        )

        self.footer_icon = discord.ui.TextInput(
            label="Footer Icon URL (optional)",
            placeholder="https://example.com/icon.png",
            default=current_icon,
            required=False,
            max_length=512
        )

        self.add_item(self.footer_text)
        self.add_item(self.footer_icon)

    async def on_submit(self, interaction: discord.Interaction):
        await interaction.response.defer()


class ImagesModal(discord.ui.Modal):
    """Modal for editing embed images."""

    def __init__(self, current_image: str = "", current_thumbnail: str = ""):
        super().__init__(title="Edit Images")

        self.image_url = discord.ui.TextInput(
            label="Image URL",
            placeholder="https://example.com/image.png",
            default=current_image,
            required=False,
            max_length=512
        )

        self.thumbnail_url = discord.ui.TextInput(
            label="Thumbnail URL",
            placeholder="https://example.com/thumbnail.png",
            default=current_thumbnail,
            required=False,
            max_length=512
        )

        self.add_item(self.image_url)
        self.add_item(self.thumbnail_url)

    async def on_submit(self, interaction: discord.Interaction):
        await interaction.response.defer()


class AddFieldModal(discord.ui.Modal):
    """Modal for adding a new field."""

    def __init__(self):
        super().__init__(title="Add Field")

        self.field_name = discord.ui.TextInput(
            label="Field Name",
            placeholder="Enter field name...",
            required=True,
            max_length=256
        )

        self.field_value = discord.ui.TextInput(
            label="Field Value",
            placeholder="Enter field value...",
            style=discord.TextStyle.paragraph,
            required=True,
            max_length=1024
        )

        self.field_inline = discord.ui.TextInput(
            label="Inline? (yes/no)",
            placeholder="yes or no",
            default="no",
            required=False,
            max_length=3
        )

        self.add_item(self.field_name)
        self.add_item(self.field_value)
        self.add_item(self.field_inline)

    async def on_submit(self, interaction: discord.Interaction):
        await interaction.response.defer()


class RemoveFieldModal(discord.ui.Modal):
    """Modal for removing a field by index."""

    def __init__(self, field_count: int):
        super().__init__(title="Remove Field")

        self.field_index = discord.ui.TextInput(
            label=f"Field Number (1-{field_count})",
            placeholder=f"Enter a number from 1 to {field_count}",
            required=True,
            max_length=2
        )

        self.add_item(self.field_index)

    async def on_submit(self, interaction: discord.Interaction):
        await interaction.response.defer()


# ======================================================
# ✅ NEW: Add Button Modal (REQUIRED FOR BUTTON FEATURE)
# ======================================================

class AddButtonModal(discord.ui.Modal):
    """Modal for adding a link button to the embed."""

    def __init__(self):
        super().__init__(title="Add Embed Button")

        self.label_input = discord.ui.TextInput(
            label="Button Label",
            placeholder="Buy Robux",
            required=True,
            max_length=80
        )

        self.url_input = discord.ui.TextInput(
            label="Button URL",
            placeholder="https://example.com",
            required=True
        )

        self.emoji_input = discord.ui.TextInput(
            label="Emoji (Unicode or Custom)",
            placeholder="😄 or <:robux:1234567890>",
            required=False,
            max_length=100  # 🔥 LONG emoji support
        )

        self.add_item(self.label_input)
        self.add_item(self.url_input)
        self.add_item(self.emoji_input)

    async def on_submit(self, interaction: discord.Interaction):
        await interaction.response.defer()

class RemoveButtonModal(discord.ui.Modal):
    """Modal for removing a button by index."""

    def __init__(self, button_count: int):
        super().__init__(title="Remove Button")

        self.index_input = discord.ui.TextInput(
            label=f"Button Number (1-{button_count})",
            placeholder="Enter button number to delete",
            required=True,
            max_length=2
        )

        self.add_item(self.index_input)

    async def on_submit(self, interaction: discord.Interaction):
        await interaction.response.defer()

