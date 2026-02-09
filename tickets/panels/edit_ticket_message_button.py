import discord
from tickets.panels.option_selector_view import TicketOptionSelectorView
from tickets.panels.ticket_message_editor_view import TicketMessageEditorView


class EditTicketMessageButton(discord.ui.Button):
    def __init__(self, panel_view):
        super().__init__(
            label="Edit Ticket Message",
            style=discord.ButtonStyle.primary,
            row=3
        )
        self.panel_view = panel_view

    async def callback(self, interaction: discord.Interaction):
        # ✅ Acknowledge ONCE
        await interaction.response.defer(ephemeral=True)

        if not self.panel_view.panel["options"]:
            await interaction.followup.send(
                "❌ No ticket options available.",
                ephemeral=True
            )
            return

        async def on_select(select_interaction, option_id):
            option = next(
                (o for o in self.panel_view.panel["options"] if o["id"] == option_id),
                None
            )

            if not option:
                await select_interaction.followup.send(
                    "❌ Option not found.",
                    ephemeral=True
                )
                return

            editor = TicketMessageEditorView(
                option=option,
                refresh_callback=self.panel_view.refresh
            )

            # ✅ FOLLOWUP (never response here)
            await select_interaction.followup.send(
                content=f"✏️ Editing ticket message for **{option['label']}**",
                view=editor,
                ephemeral=True
            )

        view = TicketOptionSelectorView(
            self.panel_view.panel["options"],
            on_select
        )

        # ✅ FOLLOWUP (not response)
        await interaction.followup.send(
            "📌 Select which ticket option you want to edit:",
            view=view,
            ephemeral=True
        )
