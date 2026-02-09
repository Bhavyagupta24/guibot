import discord

class AddButtonModal(discord.ui.Modal, title="Add Embed Button"):
    def __init__(self):
        super().__init__()

        self.label_input = discord.ui.TextInput(
            label="Button Label",
            placeholder="Buy Robux",
            max_length=80,
            required=True
        )

        self.url_input = discord.ui.TextInput(
            label="Button URL",
            placeholder="https://example.com",
            required=True
        )

        self.emoji_input = discord.ui.TextInput(
            label="Emoji (optional)",
            placeholder="💰",
            required=False,
            max_length=10
        )

        self.add_item(self.label_input)
        self.add_item(self.url_input)
        self.add_item(self.emoji_input)
