import json

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
            "faction_scale": {"value": 90.0},
            "cooldown_timer": {"value": "60"},
        }

        try:
            with open(SETTINGS_FILE, encoding="utf-8") as file:
                settings_data = json.load(file)
        except (FileNotFoundError, json.JSONDecodeError):
            settings_data = default_settings

        # Überprüfe und füge fehlende Attribute hinzu
        updated = False
        for key, value in default_settings.items():
            if key not in settings_data:
                settings_data[key] = value
                updated = True
            elif isinstance(value, dict):
                for sub_key, sub_value in value.items():
                    if sub_key not in settings_data[key]:
                        settings_data[key][sub_key] = sub_value
                        updated = True

        # Speichere die aktualisierten Einstellungen, falls Änderungen vorgenommen wurden
        if updated:
            with open(SETTINGS_FILE, "w", encoding="utf-8") as file:
                json.dump(settings_data, file, indent=4)

        return settings_data

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
            "faction_scale": {"value": config_dict["faction_scale"]},
            "cooldown_timer": {"value": config_dict["cooldown_timer"]},
        }
        with open(SETTINGS_FILE, "w", encoding="utf-8") as file:
            json.dump(settings_data, file, indent=4)
