import json
import os
from datetime import datetime

import customtkinter
from CTkMessagebox import CTkMessagebox as messagebox

from evealert import __version__
from evealert.client.client import SocketClient
from evealert.client.logger import setup_logger
from evealert.settings.helper import ICON, get_resource_path

CONFIG_PATH = get_resource_path("client.json")

DEFAULT_SETTINGS = {
    "server": {"host": "127.0.0.1", "port": 27215},
    "log_level": "INFO",
}

log_main = setup_logger("main")


class MainMenu(customtkinter.CTk):
    """Main menu for the EveLocal Client."""

    def __init__(self):
        super().__init__()
        self.title(f"EveLocal Client - {__version__}")

        self.init_widgets()
        self.place_widgets()

        self.client = None
        self.default = DEFAULT_SETTINGS
        self.load_settings()

    def init_widgets(self):
        self.set_icon(ICON)
        self.geometry("550x250")

        self.log_field = customtkinter.CTkTextbox(self, height=100, width=450)
        self.log_field.tag_config("normal", foreground="white")
        self.log_field.tag_config("green", foreground="lightgreen")
        self.log_field.tag_config("red", foreground="orange")

        self.setting_frame = customtkinter.CTkFrame(self)
        self.button_frame = customtkinter.CTkFrame(self)

        self.host_label = customtkinter.CTkLabel(self.setting_frame, text="Host:")
        self.host_entry = customtkinter.CTkEntry(self.setting_frame)

        self.port_label = customtkinter.CTkLabel(self.setting_frame, text="Port:")
        self.port_entry = customtkinter.CTkEntry(self.setting_frame)

        self.connect_button = customtkinter.CTkButton(
            self.button_frame, text="Connect", command=self.start_connection
        )
        self.disconnect_button = customtkinter.CTkButton(
            self.button_frame,
            text="Disconnect",
            command=self.on_disconnect_button_click,
            state="disabled",
            fg_color="#fa0202",
            hover_color="#bd291e",
        )
        self.save_button = customtkinter.CTkButton(
            self.button_frame, text="Save", command=self.on_save_button_click
        )

    def place_widgets(self):
        self.host_label.grid(row=0, column=0, padx=(0, 10))

        self.host_entry.grid(row=0, column=1, padx=(0, 10))

        self.port_label.grid(row=0, column=2, padx=(0, 10))

        self.port_entry.grid(row=0, column=3)

        self.connect_button.grid(row=2, column=0, padx=(0, 10))
        self.disconnect_button.grid(row=2, column=1, padx=(0, 10))
        self.save_button.grid(row=2, column=2)

        self.setting_frame.pack(pady=(10, 10))
        self.button_frame.pack(pady=(0, 10))
        self.log_field.pack(pady=(0, 10))

    def load_settings(self):
        try:
            with open(CONFIG_PATH, encoding="utf-8") as config_file:
                settings = json.load(config_file)
                settings = self.merge_settings_with_defaults(settings)
        except (FileNotFoundError, json.JSONDecodeError):
            log_main.error(
                "Settings file not found or invalid. Using default settings."
            )
            settings = self.default
            self.save_settings(DEFAULT_SETTINGS)
        self.apply_settings(settings)
        return settings

    def apply_settings(self, settings):
        try:
            self.host_entry.delete(0, "end")
            self.host_entry.insert(0, settings["server"]["host"])
            self.port_entry.delete(0, "end")
            self.port_entry.insert(0, settings["server"]["port"])
        except KeyError as e:
            log_main.error("Settings Error: %s", e, exc_info=True)
            self.write_message("Settings Error: Check Logs", "red")

    def save_settings(self, settings):
        if settings is None:
            settings = self.default

        os.makedirs(os.path.dirname(CONFIG_PATH), exist_ok=True)
        with open(CONFIG_PATH, encoding="utf-8", mode="w") as config_file:
            json.dump(settings, config_file, indent=4)

        self.apply_settings(settings)

    def merge_settings_with_defaults(self, settings):
        """Merge the loaded settings with the default settings."""
        merged_settings = self.default.copy()
        merged_settings.update(settings)
        return merged_settings

    def write_message(self, text, color="normal"):
        """Write a message to the log field."""
        now = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        try:
            self.log_field.insert("1.0", f"[{now}] {text}\n", color)
            print(f"[{now}] {text}")
        except Exception as e:
            log_main.error("Write Message Error: %s", e, exc_info=True)

    def on_save_button_click(self):
        try:
            settings = self.default.copy()
            settings.update(
                {
                    "server": {
                        "host": self.host_entry.get(),
                        "port": self.port_entry.get(),
                    }
                }
            )
        except ValueError as e:
            log_main.error("Save Button Error: %s", e, exc_info=True)
            self.write_message("Save Button Error: Check Logs", "red")

        self.save_settings(settings)

    def on_connect_button_click(self):
        self.on_save_button_click()

    def on_disconnect_button_click(self):
        if self.client:
            self.client.clean_up()
        self.client = None

    def start_connection(self):
        host = self.host_entry.get()
        port = self.port_entry.get()

        if not port.isdigit():
            messagebox(title="Error", message="Port must be a number", icon="cancel")
            return

        self.client = SocketClient(self, host, int(port))
        if self.client.connect():
            self.connect_button.configure(
                state="disabled", fg_color="#fa0202", hover_color="#bd291e"
            )
            self.disconnect_button.configure(
                state="normal", fg_color="#1f538d", hover_color="#14375e"
            )
            self.client.start_system()

    def set_icon(self, icon):
        """Set the icon for the main window."""
        try:
            icon_path = get_resource_path(icon)
            if icon_path and os.path.exists(icon_path):
                self.iconbitmap(icon_path)
            else:
                log_main.warning("Icon file not found: %s", icon_path)

            self.iconbitmap(default=icon_path)
        except Exception as e:
            log_main.exception("Error setting icon: %s", e)
