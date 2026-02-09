import re

CUSTOM_EMOJI_REGEX = re.compile(r"<a?:([a-zA-Z0-9_]+):([0-9]+)>")

def parse_emoji(raw: str | None):
    """
    Returns:
    - None if empty
    - discord.PartialEmoji-compatible dict
    """
    if not raw:
        return None

    raw = raw.strip()

    # Unicode emoji (single char or surrogate pair)
    if len(raw) <= 4 and not raw.startswith("<"):
        return raw

    # Custom emoji <a:name:id> or <:name:id>
    match = CUSTOM_EMOJI_REGEX.match(raw)
    if match:
        name, emoji_id = match.groups()
        return {
            "name": name,
            "id": int(emoji_id)
        }

    return None  # Invalid emoji
