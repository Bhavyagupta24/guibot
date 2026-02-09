import discord
from modals.embed_modals import ColorModal
from views.link_button_view import LinkButtonView


class ChannelSelectorView(discord.ui.View):
    """
    Dropdown menu for selecting which channel to send the embed to.
    """

    def __init__(self, author_id: int, embed_state: dict):
        super().__init__(timeout=60)
        self.author_id = author_id
        self.embed_state = embed_state

        self.add_item(ChannelSelect(author_id, embed_state))


class ChannelSelect(discord.ui.ChannelSelect):
    """
    Dropdown menu populated with available text channels.
    """

    def __init__(self, author_id: int, embed_state: dict):
        super().__init__(
            placeholder="Choose a channel...",
            min_values=1,
            max_values=1,
            channel_types=[discord.ChannelType.text]
        )
        self.author_id = author_id
        self.embed_state = embed_state

    async def callback(self, interaction: discord.Interaction):
        # ✅ ALWAYS acknowledge first
        await interaction.response.defer(ephemeral=True)

        # Author check
        if interaction.user.id != self.author_id:
            await interaction.followup.send(
                "❌ This is not your embed.",
                ephemeral=True
            )
            return

        selected_channel = self.values[0]

        # Permission check
        perms = selected_channel.permissions_for(interaction.guild.me)
        if not perms.send_messages or not perms.embed_links:
            await interaction.followup.send(
                f"❌ I can’t send embeds in {selected_channel.mention}",
                ephemeral=True
            )
            return

        # Build embed
        color = ColorModal.parse_color(self.embed_state.get("color", ""))

        embed = discord.Embed(
            title=self.embed_state.get("title") or None,
            description=self.embed_state.get("description") or None,
            color=color,
            timestamp=discord.utils.utcnow()
        )

        if self.embed_state.get("author_name"):
            embed.set_author(
                name=self.embed_state["author_name"],
                url=self.embed_state.get("author_url") or None,
                icon_url=self.embed_state.get("author_icon") or None
            )

        if self.embed_state.get("footer_text"):
            embed.set_footer(
                text=self.embed_state["footer_text"],
                icon_url=self.embed_state.get("footer_icon") or None
            )

        if self.embed_state.get("image_url"):
            embed.set_image(url=self.embed_state["image_url"])

        if self.embed_state.get("thumbnail_url"):
            embed.set_thumbnail(url=self.embed_state["thumbnail_url"])

        for field in self.embed_state.get("fields", []):
            embed.add_field(
                name=field["name"],
                value=field["value"],
                inline=field["inline"]
            )

        # Attach buttons
        buttons = self.embed_state.get("buttons", [])
        view = LinkButtonView(buttons) if buttons else None

        # Send embed
        try:
            await selected_channel.send(
                embed=embed,
                view=view
            )

            await interaction.followup.send(
                f"✅ Embed sent to {selected_channel.mention}",
                ephemeral=True
            )

        except Exception as e:
            await interaction.followup.send(
                f"❌ Failed to send embed:\n`{e}`",
                ephemeral=True
            )
