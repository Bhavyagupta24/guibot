import discord

class LinkButtonView(discord.ui.View):
    def __init__(self, buttons: list[dict]):
        super().__init__(timeout=None)

        for btn in buttons:
            self.add_item(
                discord.ui.Button(
                    label=btn["label"],
                    url=btn["url"],
                    emoji=btn.get("emoji"),
                    style=discord.ButtonStyle.link
                )
            )
