import discord
from tickets.utils.emoji_parser import parse_emoji


class TicketOptionSelect(discord.ui.Select):
    def __init__(self, options: list[dict], on_select):
        self.on_select_callback = on_select

        select_options = [
            discord.SelectOption(
                label=opt["label"][:100],
                value=opt["id"],
                emoji=parse_emoji(opt.get("emoji"))
            )
            for opt in options
        ]

        super().__init__(
            placeholder="Select a ticket option…",
            min_values=1,
            max_values=1,
            options=select_options,
            custom_id="ticket_option_selector"
        )

    async def callback(self, interaction: discord.Interaction):
        # ✅ DON'T defer here - let the callback handle the response
        try:
            await self.on_select_callback(interaction, self.values[0])
        except Exception as e:
            if not interaction.response.is_done():
                await interaction.response.send_message(
                    f"❌ Error: {str(e)}",
                    ephemeral=True
                )


class TicketOptionSelectorView(discord.ui.View):
    def __init__(self, options: list[dict], on_select):
        super().__init__(timeout=60)
        self.add_item(TicketOptionSelect(options, on_select))