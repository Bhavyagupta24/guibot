import discord
import re
from datetime import datetime
from io import BytesIO

from tickets.constants import DEFAULT_TICKET_TEMPLATE
from tickets.utils.ticket_embed_builder import build_ticket_embed
from tickets.utils.transcript_generator import TranscriptGenerator
from tickets.panels.panel_storage import PanelStorage
from utils.embed_storage import EmbedStorage


class TicketCloseView(discord.ui.View):
    """View with close button for tickets"""

    def __init__(self, ticket_owner_id: int, panel_name: str, guild_id: int):
        super().__init__(timeout=None)
        self.ticket_owner_id = ticket_owner_id
        self.panel_name = panel_name
        self.guild_id = guild_id

    @discord.ui.button(
        label="Close Ticket",
        style=discord.ButtonStyle.danger,
        emoji="🔒",
        custom_id="ticket_close_button"
    )
    async def close_ticket(self, interaction: discord.Interaction, button: discord.ui.Button):
        """Close ticket and generate transcript"""
        await interaction.response.defer(ephemeral=True)

        channel = interaction.channel
        ticket_owner = await interaction.client.fetch_user(self.ticket_owner_id)

        # ───────────── RESOLVE PANEL NAME (SOURCE OF TRUTH) ─────────────
        panel_name = self.panel_name
        if channel.topic and channel.topic.startswith("panel:"):
            panel_name = channel.topic.replace("panel:", "").strip()

        # ───────────── LOAD PANEL CONFIG ─────────────
        storage = PanelStorage()
        panel = storage.get_panel(self.guild_id, panel_name)
        transcript_channel_id = panel.get("transcript_channel_id") if panel else None

        if not transcript_channel_id:
            await interaction.followup.send(
                "❌ No transcript channel configured for this panel!\n"
                "💡 Use `/ticket set-transcript <channel>` to set one.",
                ephemeral=True
            )
            return

        transcript_channel = interaction.guild.get_channel(transcript_channel_id)
        if not transcript_channel:
            await interaction.followup.send(
                "❌ Transcript channel not found!",
                ephemeral=True
            )
            return

        try:
            # ───────────── GENERATE TRANSCRIPT ─────────────
            await interaction.followup.send("⏳ Generating transcript...", ephemeral=True)

            print(f"DEBUG: Generating transcript for {channel.name} (panel={panel_name})")

            html_bytes, users_in_transcript = await TranscriptGenerator.generate_transcript(
                channel=channel,
                ticket_owner=ticket_owner,
                panel_name=panel_name,
                server_logo_url=interaction.guild.icon.url if interaction.guild.icon else None
            )

            # ───────────── TRANSCRIPT EMBED ─────────────
            user_list = "\n".join(
                [f"• {u.mention} - @{u.name}#{u.discriminator}" for u in list(users_in_transcript)[:15]]
            )
            if len(users_in_transcript) > 15:
                user_list += f"\n... and {len(users_in_transcript) - 15} more"

            transcript_embed = discord.Embed(
                title=f"📑 Ticket Transcript: #{channel.name}",
                color=discord.Color.blurple(),
                timestamp=datetime.now()
            )
            transcript_embed.add_field(
                name="Ticket Owner",
                value=f"{ticket_owner.mention}\n@{ticket_owner.name}#{ticket_owner.discriminator}",
                inline=True
            )
            transcript_embed.add_field(
                name="Panel Name",
                value=panel_name,
                inline=True
            )
            transcript_embed.add_field(
                name="Ticket Name",
                value=channel.name,
                inline=True
            )
            transcript_embed.add_field(
                name="Created At",
                value=f"<t:{int(channel.created_at.timestamp())}:F>",
                inline=True
            )
            transcript_embed.add_field(
                name=f"Users in Transcript ({len(users_in_transcript)})",
                value=user_list or "No users",
                inline=False
            )
            transcript_embed.set_thumbnail(
                url=interaction.guild.icon.url if interaction.guild.icon else None
            )
            transcript_embed.set_footer(
                text=f"Closed by {interaction.user.name}",
                icon_url=interaction.user.display_avatar.url
            )

            file = discord.File(
                BytesIO(html_bytes),
                filename=f"transcript-{channel.name}-{datetime.now().strftime('%Y%m%d-%H%M%S')}.html"
            )

            await transcript_channel.send(embed=transcript_embed, file=file)

            # ───────────── RENAME CHANNEL ─────────────
            new_name = f"closed-{ticket_owner.name}".lower()
            await channel.edit(name=new_name)

            await interaction.followup.send(
                f"✅ Ticket closed!\n"
                f"📑 Transcript sent to {transcript_channel.mention}\n"
                f"📝 Channel renamed to `{new_name}`",
                ephemeral=True
            )

        except discord.Forbidden:
            await interaction.followup.send(
                "❌ I don't have permission to rename the channel or send to the transcript channel!",
                ephemeral=True
            )
        except Exception as e:
            print(f"ERROR closing ticket: {type(e).__name__}: {e}")
            import traceback
            traceback.print_exc()
            await interaction.followup.send(
                f"❌ Error closing ticket: {str(e)}",
                ephemeral=True
            )


class TicketManager:

    @staticmethod
    async def create_ticket(
        interaction: discord.Interaction,
        option: dict
    ):
        """
        Handles BOTH:
        - ticket options  -> creates channel
        - embed options   -> sends embed ephemerally
        """

        option_type = option.get("type", "ticket")

        # ───────────────── EMBED OPTION ─────────────────
        if option_type == "embed":
            embed_name = option.get("embed_name")
            embed = EmbedStorage().get_embed(
                interaction.guild.id,
                embed_name
            )

            if not embed:
                if not interaction.response.is_done():
                    await interaction.response.send_message(
                        "❌ Attached embed not found.",
                        ephemeral=True
                    )
                return

            if interaction.response.is_done():
                await interaction.followup.send(embed=embed, ephemeral=True)
            else:
                await interaction.response.send_message(
                    embed=embed,
                    ephemeral=True
                )
            return

        # ───────────── VALIDATION ─────────────
        if not option.get("panel_name"):
            raise ValueError("panel_name missing from ticket option")

        # ───────────────── TICKET OPTION ─────────────────
        guild = interaction.guild
        user = interaction.user

        # ───────────── SANITIZE CHANNEL NAME ─────────────
        prefix_raw = option.get("ticket_prefix") or option.get("label", "ticket")
        prefix = re.sub(r"[^a-zA-Z0-9-]", "-", prefix_raw.lower()).strip("-")

        username = re.sub(r"[^a-zA-Z0-9-]", "-", user.name.lower()).strip("-")
        channel_name = f"{prefix}-{username}"

        # ───────────── CATEGORY LOGIC ─────────────
        category = None
        category_id = option.get("category_id")

        if category_id:
            category = guild.get_channel(category_id)

        if category is None:
            category = interaction.channel.category

        # ───────────── LIMIT CHECK ─────────────
        limit = option.get("limit")  # None = unlimited
        if limit is not None:
            existing = [
                c for c in guild.text_channels
                if c.category == category
                and c.name.startswith(prefix)
                and user in c.members
            ]

            if len(existing) >= limit:
                if not interaction.response.is_done():
                    await interaction.response.send_message(
                        f"❌ You can only have **{limit}** open ticket(s) for **{option['label']}**.",
                        ephemeral=True
                    )
                return

        # ───────────── PERMISSIONS ─────────────
        overwrites = {
            guild.default_role: discord.PermissionOverwrite(view_channel=False),
            user: discord.PermissionOverwrite(
                view_channel=True,
                send_messages=True,
                read_message_history=True
            ),
            guild.me: discord.PermissionOverwrite(
                view_channel=True,
                send_messages=True,
                manage_channels=True
            )
        }

        # ───────────── CREATE CHANNEL ─────────────
        channel = await guild.create_text_channel(
            name=channel_name,
            category=category,
            overwrites=overwrites,
            reason=f"Ticket opened by {user}"
        )

        # 🔐 STORE PANEL NAME (CRITICAL)
        await channel.edit(topic=f"panel:{option['panel_name']}")

        # ───────────── INTRO EMBED ─────────────
        template = option.get("ticket_message") or DEFAULT_TICKET_TEMPLATE

        embed = build_ticket_embed(
            template=template,
            interaction=interaction,
            option=option
        )

        await channel.send(embed=embed)

        # ───────────── CLOSE BUTTON ─────────────
        close_view = TicketCloseView(
            ticket_owner_id=user.id,
            panel_name=option["panel_name"],
            guild_id=guild.id
        )

        await channel.send(
            "Click the button below to close this ticket and generate a transcript:",
            view=close_view
        )

        # ───────────── CONFIRM USER ─────────────
        if interaction.response.is_done():
            await interaction.followup.send(
                f"✅ Ticket created: {channel.mention}",
                ephemeral=True
            )
        else:
            await interaction.response.send_message(
                f"✅ Ticket created: {channel.mention}",
                ephemeral=True
            )
