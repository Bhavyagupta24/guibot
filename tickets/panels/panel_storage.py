import json
import os

DATA_DIR = "data/ticket_panels"


class PanelStorage:
    def __init__(self):
        os.makedirs(DATA_DIR, exist_ok=True)

    def _file(self, guild_id: int) -> str:
        return os.path.join(DATA_DIR, f"{guild_id}.json")

    # ===============================
    # LOAD ALL PANELS
    # ===============================
    def load_panels(self, guild_id: int) -> dict:
        path = self._file(guild_id)
        if not os.path.exists(path):
            return {}

        try:
            with open(path, "r", encoding="utf-8") as f:
                return json.load(f)
        except json.JSONDecodeError:
            return {}

    # ===============================
    # SAVE ALL PANELS
    # ===============================
    def save_panels(self, guild_id: int, panels: dict):
        with open(self._file(guild_id), "w", encoding="utf-8") as f:
            json.dump(panels, f, indent=4, ensure_ascii=False)

    # ===============================
    # SAVE SINGLE PANEL
    # ===============================
    def save_panel(self, guild_id: int, panel_name: str, panel_data: dict):
        panels = self.load_panels(guild_id)
        panels[panel_name] = panel_data
        self.save_panels(guild_id, panels)

    # ===============================
    # GET SINGLE PANEL
    # ===============================
    def get_panel(self, guild_id: int, panel_name: str):
        return self.load_panels(guild_id).get(panel_name)

    # ===============================
    # GET ALL PANELS (NEW)
    # ===============================
    def get_all_panels(self, guild_id: int) -> dict:
        """
        Returns all panels for a guild.
        Used for autocomplete, config viewing, etc.
        """
        return self.load_panels(guild_id)
