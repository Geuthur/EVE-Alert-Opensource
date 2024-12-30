import json
from typing import TYPE_CHECKING

import customtkinter

from evealert.settings.helper import get_resource_path
from evealert.settings.logger import logging

if TYPE_CHECKING:
    from evealert.menu.main import MainMenu

logger = logging.getLogger("menu")

DEFAULT_SETTINGS = {
    "logging": "INFO",
    "alert_region_1": {"x": 0, "y": 0},
    "alert_region_2": {"x": 0, "y": 0},
    "faction_region_1": {"x": 0, "y": 0},
    "faction_region_2": {"x": 0, "y": 0},
    "detectionscale": {"value": 90},
    "faction_scale": {"value": 90},
    "cooldown_timer": {"value": 30},
    "server": {
        "host": "127.0.0.1",
        "port": 27215,
        "admin_password": "1234",
        "server_mode": True,
    },
}


class SettingMenu:
    """Setting menu for the Alert System."""

    def __init__(self, main: "MainMenu"):
        self.main = main
        self.open = False
        self.default = DEFAULT_SETTINGS
        self.changed = False

        self.setting_window = customtkinter.CTkToplevel(self.main)
        self.setting_window.title("Settings")
        self.setting_window.withdraw()

        self.server_mode = customtkinter.BooleanVar()

        self.create_menu()
        self.load_settings()

    @property
    def is_changed(self):
        """Returns True if the settings have been changed."""
        return self.changed

    @property
    def is_open(self):
        """Returns True if the settings window is open."""
        return self.open

    def load_settings(self):
        config_path = get_resource_path("settings.json")
        try:
            with open(config_path, encoding="utf-8") as config_file:
                settings = json.load(config_file)
                settings = self.merge_settings_with_defaults(settings)
        except (FileNotFoundError, json.JSONDecodeError):
            logger.error(
                "Setting Menu: Error reading settings file. Using default settings."
            )
            settings = self.default
            self.save_settings(settings)

        self.apply_settings(settings)
        return settings

    def merge_settings_with_defaults(self, settings):
        """Merge the loaded settings with the default settings."""
        merged_settings = self.default.copy()
        merged_settings.update(settings)
        return merged_settings

    def apply_settings(self, settings):
        try:
            self.logging.delete(0, customtkinter.END)
            self.logging.insert(0, settings["logging"])

            self.alert_region_x_first.delete(0, customtkinter.END)
            self.alert_region_x_first.insert(0, settings["alert_region_1"]["x"])

            self.alert_region_y_first.delete(0, customtkinter.END)
            self.alert_region_y_first.insert(0, settings["alert_region_1"]["y"])

            self.alert_region_x_second.delete(0, customtkinter.END)
            self.alert_region_x_second.insert(0, settings["alert_region_2"]["x"])
            self.alert_region_y_second.delete(0, customtkinter.END)
            self.alert_region_y_second.insert(0, settings["alert_region_2"]["y"])

            self.faction_region_x_first.delete(0, customtkinter.END)
            self.faction_region_x_first.insert(0, settings["faction_region_1"]["x"])
            self.faction_region_y_first.delete(0, customtkinter.END)
            self.faction_region_y_first.insert(0, settings["faction_region_1"]["y"])

            self.faction_region_x_second.delete(0, customtkinter.END)
            self.faction_region_x_second.insert(0, settings["faction_region_2"]["x"])
            self.faction_region_y_second.delete(0, customtkinter.END)
            self.faction_region_y_second.insert(0, settings["faction_region_2"]["y"])

            self.detectionscale.set(settings["detectionscale"]["value"])
            self.slider_event(settings["detectionscale"]["value"])
            self.faction_scale.set(settings["faction_scale"]["value"])
            self.factionslider_event(settings["faction_scale"]["value"])

            self.cooldown_timer.delete(0, customtkinter.END)
            self.cooldown_timer.insert(0, settings["cooldown_timer"]["value"])

            self.socket_server_host.delete(0, customtkinter.END)
            self.socket_server_host.insert(0, settings["server"]["host"])

            self.socket_server_port.delete(0, customtkinter.END)
            self.socket_server_port.insert(0, settings["server"]["port"])

            self.socket_server_alerter.delete(0, customtkinter.END)
            self.socket_server_alerter.insert(0, settings["server"]["admin_password"])

            self.server_mode.set(settings["server"]["server_mode"])

        except KeyError as e:
            logger.exception(e)
            self.main.write_message(
                "Setting Menu: Error reading settings file. read logs for more information",
                "red",
            )

    def save_settings(self, settings=None):
        if settings is None:
            settings = self.default

        config_path = get_resource_path("settings.json")
        with open(config_path, encoding="utf-8", mode="w") as config_file:
            json.dump(settings, config_file, indent=4)

        self.apply_settings(settings)
        # Set the changed flag to True
        self.changed = True

    def save(self):
        try:
            settings = DEFAULT_SETTINGS.copy()
            settings.update(
                {
                    "logging": self.logging.get(),
                    "alert_region_1": {
                        "x": int(self.alert_region_x_first.get()),
                        "y": int(self.alert_region_y_first.get()),
                    },
                    "alert_region_2": {
                        "x": int(self.alert_region_x_second.get()),
                        "y": int(self.alert_region_y_second.get()),
                    },
                    "faction_region_1": {
                        "x": int(self.faction_region_x_first.get()),
                        "y": int(self.faction_region_y_first.get()),
                    },
                    "faction_region_2": {
                        "x": int(self.faction_region_x_second.get()),
                        "y": int(self.faction_region_y_second.get()),
                    },
                    "detectionscale": {"value": int(self.detectionscale.get())},
                    "faction_scale": {"value": int(self.faction_scale.get())},
                    "cooldown_timer": {"value": int(self.cooldown_timer.get())},
                    "server": {
                        "host": self.socket_server_host.get(),
                        "port": int(self.socket_server_port.get()),
                        "admin_password": self.socket_server_alerter.get(),
                        "server_mode": self.server_mode.get(),
                    },
                }
            )
        except ValueError as e:
            self.main.write_message(
                "Setting Menu: Error saving settings. Please check the values.", "red"
            )
            logger.error(e)
        self.save_settings(settings)

    def clean_up(self):
        """Cleans up the settings window."""
        if self.is_open:
            self.open = False
            self.main.mainmenu_buttons.setting_menu.configure(
                fg_color="#1f538d", hover_color="#14375e"
            )
            # hide the settings window
            self.setting_window.withdraw()
            # self.save_settings()  # Save settings when closing

    def create_menu(self):
        """Load the settings from the settings file."""

        # Verwende ein eigenes Frame für das Menü
        self.menu_frame = customtkinter.CTkFrame(self.setting_window)
        self.menu_frame.pack(side="left", padx=20, pady=20)

        self.logging = customtkinter.CTkEntry(self.menu_frame)

        # 1 Row - Init
        self.label_x_axis = customtkinter.CTkLabel(self.menu_frame, text="X-Achse")
        self.label_y_axis = customtkinter.CTkLabel(self.menu_frame, text="Y-Achse")

        # 2 Row - Init
        # Alert Region Position 1
        self.alert_region_label_1 = customtkinter.CTkLabel(
            self.menu_frame, text="Alert Region Left Upper Corner:", justify="left"
        )
        self.alert_region_x_first = customtkinter.CTkEntry(self.menu_frame)
        self.alert_region_y_first = customtkinter.CTkEntry(self.menu_frame)

        # 3 Row - Init
        # Alert Region Position 2
        self.alert_region_label_2 = customtkinter.CTkLabel(
            self.menu_frame, text="Alert Region Right Lower Corner:", justify="left"
        )
        self.alert_region_x_second = customtkinter.CTkEntry(self.menu_frame)
        self.alert_region_y_second = customtkinter.CTkEntry(self.menu_frame)

        # 4 Row - Init
        # Alert Region Position 1
        self.faction_region_label_1 = customtkinter.CTkLabel(
            self.menu_frame, text="Faction Region Left Upper Corner:", justify="left"
        )
        self.faction_region_x_first = customtkinter.CTkEntry(self.menu_frame)
        self.faction_region_y_first = customtkinter.CTkEntry(self.menu_frame)

        # 5 Row - Init
        # Alert Region Position 2
        self.faction_region_label_2 = customtkinter.CTkLabel(
            self.menu_frame, text="Faction Region Right Lower Corner:", justify="left"
        )
        self.faction_region_x_second = customtkinter.CTkEntry(self.menu_frame)
        self.faction_region_y_second = customtkinter.CTkEntry(self.menu_frame)

        # Row 6 - Init
        # Slider
        self.slider_label = customtkinter.CTkLabel(
            self.menu_frame, text="Detection Threshold"
        )
        self.detectionscale = customtkinter.DoubleVar()
        self.slider = customtkinter.CTkSlider(
            self.menu_frame,
            from_=1,
            to=100,
            orientation="horizontal",
            number_of_steps=99,
            variable=self.detectionscale,
            command=self.slider_event,
        )

        # Row 7 - Init
        # Slider
        self.faction_slider_label = customtkinter.CTkLabel(
            self.menu_frame, text="Faction Detection Threshold"
        )
        self.faction_scale = customtkinter.DoubleVar()
        self.slider2 = customtkinter.CTkSlider(
            self.menu_frame,
            from_=1,
            to=100,
            orientation="horizontal",
            number_of_steps=99,
            variable=self.faction_scale,
            command=self.factionslider_event,
        )

        self.cooldown_timer_label = customtkinter.CTkLabel(
            self.menu_frame, text="Cooldown Timer:", justify="left"
        )
        self.cooldown_timer = customtkinter.CTkEntry(self.menu_frame)
        self.cooldown_timer_text = customtkinter.CTkLabel(
            self.menu_frame, text="Seconds", justify="left"
        )

        self.save_button = customtkinter.CTkButton(
            self.menu_frame, text="Save", command=self.save
        )

        self.close_button = customtkinter.CTkButton(
            self.menu_frame, text="Close", command=self.clean_up
        )

        self.empty_label_1 = customtkinter.CTkLabel(
            self.menu_frame, text=self.slider.get()
        )

        self.empty_label_2 = customtkinter.CTkLabel(
            self.menu_frame, text=self.slider2.get()
        )

        self.socket_server_label = customtkinter.CTkLabel(
            self.menu_frame, text="Socket Server:", justify="left"
        )
        self.socket_server_host = customtkinter.CTkEntry(self.menu_frame)
        self.socket_server_port = customtkinter.CTkEntry(self.menu_frame)

        self.socket_server_alerter_label = customtkinter.CTkLabel(
            self.menu_frame, text="Alerter Password:", justify="left"
        )
        self.socket_server_alerter = customtkinter.CTkEntry(self.menu_frame)

        self.socket_server_mode_checkbox = customtkinter.CTkCheckBox(
            self.menu_frame, text="Server Mode", variable=self.server_mode
        )

        # Init Visuals

        self.label_x_axis.grid(row=0, column=1)
        self.label_y_axis.grid(row=0, column=2)

        # Alert Region 1 Visual
        self.alert_region_label_1.grid(row=1, column=0, padx=20)
        self.alert_region_x_first.grid(row=1, column=1)
        self.alert_region_y_first.grid(row=1, column=2)

        # Alert Region 2 Visual
        self.alert_region_label_2.grid(row=2, column=0, padx=20)
        self.alert_region_x_second.grid(row=2, column=1, padx=20)
        self.alert_region_y_second.grid(row=2, column=2, padx=20)

        # Faction Region 1 Visual
        self.faction_region_label_1.grid(row=3, column=0, padx=20)
        self.faction_region_x_first.grid(row=3, column=1, padx=20)
        self.faction_region_y_first.grid(row=3, column=2, padx=20)

        # Faction Region 2 Visual
        self.faction_region_label_2.grid(row=4, column=0, padx=20)
        self.faction_region_x_second.grid(row=4, column=1, padx=20)
        self.faction_region_y_second.grid(row=4, column=2, padx=20)

        # Faction Region 2 Visual
        self.cooldown_timer_label.grid(row=5, column=0, padx=20)
        self.cooldown_timer.grid(row=5, column=1, padx=20)
        self.cooldown_timer_text.grid(row=5, column=2)

        # Slider Visual
        self.empty_label_1.grid(row=6, column=2)

        # Slider Visual
        self.slider_label.grid(row=6, column=0)
        self.slider.grid(row=6, column=1)

        # Slider Visual
        self.empty_label_2.grid(row=7, column=2)

        # Slider Visual
        self.faction_slider_label.grid(row=7, column=0)
        self.slider2.grid(row=7, column=1)

        # Socket Server Visual
        self.socket_server_label.grid(row=8, column=0)
        self.socket_server_host.grid(row=8, column=1)
        self.socket_server_port.grid(row=8, column=2)

        self.socket_server_alerter_label.grid(row=9, column=0)
        self.socket_server_alerter.grid(row=9, column=1)
        self.socket_server_mode_checkbox.grid(row=9, column=2)

        # Save Button
        self.save_button.grid(row=10, column=0, pady=10)
        # Close Button
        self.close_button.grid(row=10, column=2, pady=10)

        self.setting_window.protocol("WM_DELETE_WINDOW", self.clean_up)

    def open_menu(self):
        """Opens the settings window."""
        if not self.is_open:
            self.open = True
            self.main.mainmenu_buttons.setting_menu.configure(
                fg_color="#fa0202", hover_color="#bd291e"
            )

            # Position des Beschreibungsfensters rechts neben dem Hauptmenü
            config_menu_x, config_menu_y = (
                self.main.winfo_x(),
                self.main.winfo_y(),
            )
            config_menu_width, config_menu_height = (
                self.main.winfo_width(),
                self.main.winfo_height(),
            )

            config_window_width = 650
            config_window_height = 370
            config_window_x = config_menu_x + config_menu_width + 10
            config_window_y = config_menu_y + config_menu_height + 40

            self.setting_window.geometry(
                f"{config_window_width}x{config_window_height}+{config_window_x}+{config_window_y}"
            )

            self.setting_window.deiconify()
        else:
            self.clean_up()

    def slider_event(self, slider_value):
        self.empty_label_1.configure(text=slider_value)

    def factionslider_event(self, slider_value):
        self.empty_label_2.configure(text=slider_value)
