import discord
from modals.embed_modals import ColorModal

def build_ticket_embed(template: dict, interaction, option):
    def fmt(text):
        if not text:
            return None
        return (
            text
            .replace("{user}", interaction.user.mention)
            .replace("{username}", interaction.user.name)
            .replace("{option}", option["label"])
            .replace("{guild}", interaction.guild.name)
        )

    embed = discord.Embed(
        title=fmt(template.get("title")),
        description=fmt(template.get("description")),
        color=ColorModal.parse_color(template.get("color", ""))
    )

    if template.get("footer_text"):
        embed.set_footer(
            text=fmt(template["footer_text"]),
            icon_url=template.get("footer_icon") or None
        )

    if template.get("image_url"):
        embed.set_image(url=template["image_url"])

    if template.get("thumbnail_url"):
        embed.set_thumbnail(url=template["thumbnail_url"])

    for field in template.get("fields", []):
        embed.add_field(
            name=fmt(field["name"]),
            value=fmt(field["value"]),
            inline=field["inline"]
        )

    return embed
