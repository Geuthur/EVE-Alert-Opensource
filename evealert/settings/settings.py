import json
import os

# Pfad zur JSON-Datei für die Einstellungen
SETTINGS_FILE = "settings.json"


class SettingsManager:
    """Settings class for the Alert System."""

    def __init__(self):
        pass

    def open_settings(self):
        default_settings = {
            "logging": "ERROR",
            "alert_region_1": {"x": "0", "y": "0"},
            "alert_region_2": {"x": "0", "y": "0"},
            "faction_region_1": {"x": "0", "y": "0"},
            "faction_region_2": {"x": "0", "y": "0"},
            "detectionscale": {"value": 90.0},
            "detection_mode": {"value": "picture"},
            "cooldown_timer": {"value": "60"},
        }

        try:
            with open(SETTINGS_FILE, encoding="utf-8") as file:
                settings_data = json.load(file)
            return settings_data
        except FileNotFoundError:
            if os.path.exists(SETTINGS_FILE):  # Überprüfen, ob die Datei existiert
                # Wenn die Datei existiert, lösche sie
                os.remove(SETTINGS_FILE)

            # Erstelle die Datei mit den Standardwerten
            with open(SETTINGS_FILE, "w", encoding="utf-8") as file:
                json.dump(default_settings, file, indent=4)

            return default_settings

    def save_settings(self, config_dict):
        settings_data = {
            "logging": config_dict["logging"],
            "alert_region_1": {
                "x": config_dict["alert_region_x_first"],
                "y": config_dict["alert_region_y_first"],
            },
            "alert_region_2": {
                "x": config_dict["alert_region_x_second"],
                "y": config_dict["alert_region_y_second"],
            },
            "faction_region_1": {
                "x": config_dict["faction_region_x_first"],
                "y": config_dict["faction_region_y_first"],
            },
            "faction_region_2": {
                "x": config_dict["faction_region_x_second"],
                "y": config_dict["faction_region_y_second"],
            },
            "detectionscale": {"value": config_dict["detectionscale"]},
            "detection_mode": {"value": config_dict["mode_var"]},
            "cooldown_timer": {"value": config_dict["cooldown_timer"]},
        }
        with open(SETTINGS_FILE, "w", encoding="utf-8") as file:
            json.dump(settings_data, file, indent=4)

    def set_system_label(self):
        pass
