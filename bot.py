import discord
from discord.ext import commands
import os
from dotenv import load_dotenv

from tickets.panels.panel_storage import PanelStorage
from tickets.views.ticket_button_view import TicketButtonView
from tickets.ticket_manager import TicketCloseView
from tickets.views.ticket_dropdown_view import TicketDropdownView

# Load environment variables
load_dotenv()

# ───────────── BOT SETUP ─────────────
intents = discord.Intents.default()
intents.guilds = True

bot = commands.Bot(
    command_prefix="!",  # required but unused
    intents=intents,
    help_command=None
)


@bot.event
async def on_ready():
    print(f"✅ Logged in as {bot.user} (ID: {bot.user.id})")
    print(f"📊 Connected to {len(bot.guilds)} server(s)")

    # ───────────── REGISTER PERSISTENT VIEWS ─────────────
    storage = PanelStorage()
    registered = 0

    bot.add_view(
        TicketCloseView(
            ticket_owner_id=0,
            panel_name="dummy",
            guild_id=0
        )
    )
    print("🔁 Registered persistent TicketCloseView")    

    for guild in bot.guilds:
        panels = storage.load_panels(guild.id)

        for panel_name, panel in panels.items():
            options = panel.get("options", [])
            if not options:
                continue

            style = panel.get("style", "buttons")

            if style == "dropdown":
                bot.add_view(
                    TicketDropdownView(
                        guild_id=guild.id,
                        panel_name=panel_name
                    )
                )
            else:
                bot.add_view(
                    TicketButtonView(
                        guild_id=guild.id,
                        panel_name=panel_name
                    )
                )

            registered += 1
            print(
                f"🔁 Registered {style} view for panel "
                f"'{panel_name}' in {guild.name}"
            )

    print(f"✅ Total persistent panels restored: {registered}")

    # ───────────── SYNC SLASH COMMANDS ─────────────
    try:
        synced = await bot.tree.sync()
        print(f"🔄 Synced {len(synced)} command(s)")
    except Exception as e:
        print(f"❌ Failed to sync commands: {e}")

    # ───────────── BOT STATUS ─────────────
    await bot.change_presence(
        activity=discord.Activity(
            type=discord.ActivityType.watching,
            name="/ticket panel create"
        )
    )

    print("✨ Bot is fully ready and stable!")


# ───────────── LOAD COGS ─────────────
async def load_cogs():
    cogs_to_load = [
        "cogs.embed",
        "cogs.tickets"
    ]

    for cog in cogs_to_load:
        try:
            await bot.load_extension(cog)
            print(f"📦 Loaded cog: {cog}")
        except Exception as e:
            print(f"❌ Failed to load {cog}: {e}")


# ───────────── MAIN ─────────────
async def main():
    async with bot:
        await load_cogs()

        token = os.getenv("DISCORD_TOKEN")
        if not token:
            print("❌ ERROR: DISCORD_TOKEN not found in .env file")
            return

        await bot.start(token)


if __name__ == "__main__":
    import asyncio
    asyncio.run(main())
