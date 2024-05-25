import json
import os

# Pfad zur JSON-Datei für die Einstellungen
SETTINGS_FILE = "settings.json"


class SettingsManager:
    """Settings class for the Alert System."""

    def __init__(self, root=None):
        self.root = root

    def open_settings(self):
        default_settings = {
            "settings": {
                "logging": "ERROR",
                "alarm_locations": [
                    {"vision_1": {"x1": 0, "y1": 0, "x2": 0, "y2": 0}},
                    {"vision_2": {"x1": 0, "y1": 0, "x2": 0, "y2": 0}},
                ],
                "faction_region_1": {"x": 0, "y": 0},
                "faction_region_2": {"x": 0, "y": 0},
                "detectionscale": {"value": 90.0},
                "detection_mode": {"value": "picture"},
                "cooldown_timer": {"value": 60},
            }
        }

        try:
            with open(SETTINGS_FILE, encoding="utf-8") as file:
                settings_data = json.load(file)
            return settings_data["settings"]
        except FileNotFoundError:
            if os.path.exists(SETTINGS_FILE):  # Überprüfen, ob die Datei existiert
                # Wenn die Datei existiert, lösche sie
                os.remove(SETTINGS_FILE)

            # Erstelle die Datei mit den Standardwerten
            with open(SETTINGS_FILE, "w", encoding="utf-8") as file:
                json.dump(default_settings, file, indent=4)

            return default_settings

    def save_settings(self):
        if not self.root.configmenu.entries:
            return "Empty Fields. Minimum is Alert Region."

        alarm_locations = []
        for i in range(0, len(self.root.configmenu.entries), 4):
            alarm_location = {
                f"vision_{i // 4 + 1}": {
                    "x1": int(self.root.configmenu.entries[i].get()),
                    "y1": int(self.root.configmenu.entries[i + 1].get()),
                    "x2": int(self.root.configmenu.entries[i + 2].get()),
                    "y2": int(self.root.configmenu.entries[i + 3].get()),
                }
            }
            alarm_locations.append(alarm_location)

        settings = {
            "settings": {
                "logging": self.root.configmenu.logging.get(),
                "alarm_locations": alarm_locations,
                "faction_region_1": {
                    "x": int(self.root.configmenu.faction_region_x_first.get()),
                    "y": int(self.root.configmenu.faction_region_y_first.get()),
                },
                "faction_region_2": {
                    "x": int(self.root.configmenu.faction_region_x_second.get()),
                    "y": int(self.root.configmenu.faction_region_y_second.get()),
                },
                "detectionscale": {
                    "value": float(self.root.configmenu.detectionscale.get())
                },
                "detection_mode": {"value": self.root.configmenu.mode_var.get()},
                "cooldown_timer": {
                    "value": int(self.root.configmenu.cooldown_timer.get())
                },
            }
        }

        # Hier speichern Sie die Einstellungen in einer Datei oder Datenbank
        # Zum Beispiel:
        with open("settings.json", "w", encoding="utf-8") as f:
            json.dump(settings, f, indent=4)

        return "Settings saved successfully"

    def load_settings(self):
        # Settings Menu
        settings_data = self.open_settings()
        if settings_data:
            return settings_data
        return None
