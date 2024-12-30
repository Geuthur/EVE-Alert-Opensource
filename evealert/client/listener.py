import json
from tkinter import messagebox

import customtkinter

from evealert.client import SocketClient
from evealert.settings.helper import get_resource_path

CONFIG_PATH = get_resource_path("client.json")

DEFAULT_SETTINGS = {
    "server": {"host": "127.0.0.1", "port": 27215},
}


class MainMenu:
    def __init__(self, root: customtkinter.CTk):
        self.root = root
        self.root.title("EveLocal Client")
        self.root.geometry("450x150")

        self.init_widgets()
        self.place_widgets()

        self.client = None
        self.apply_settings()

    def save_settings(self, settings):
        with open(CONFIG_PATH, encoding="utf-8", mode="w") as config_file:
            json.dump(settings, config_file, indent=4)
        print("Settings saved.")

    def load_settings(self):
        try:
            with open(CONFIG_PATH, encoding="utf-8") as config_file:
                return json.load(config_file)
        except (FileNotFoundError, json.JSONDecodeError):
            self.save_settings(DEFAULT_SETTINGS)
            return DEFAULT_SETTINGS

    def apply_settings(self):
        settings = self.load_settings()
        self.host_entry.delete(0, "end")
        self.host_entry.insert(0, settings["server"]["host"])
        self.port_entry.delete(0, "end")
        self.port_entry.insert(0, settings["server"]["port"])

    def on_save_button_click(self):
        settings = self.load_settings()
        settings["server"]["host"] = self.host_entry.get()
        settings["server"]["port"] = self.port_entry.get()
        self.save_settings(settings)

    def on_connect_button_click(self):
        self.on_save_button_click()

    def init_widgets(self):
        self.setting_frame = customtkinter.CTkFrame(self.root)
        self.button_frame = customtkinter.CTkFrame(self.root)
        self.status_frame = customtkinter.CTkFrame(self.root)

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
        )
        self.save_button = customtkinter.CTkButton(
            self.button_frame, text="Save", command=self.on_save_button_click
        )

        self.status_label = customtkinter.CTkLabel(
            self.status_frame, text="Status: Inactive"
        )

        self.log_field = customtkinter.CTkTextbox(
            self.status_frame, height=100, width=450
        )
        self.log_field.tag_config("normal", foreground="white")
        self.log_field.tag_config("green", foreground="lightgreen")
        self.log_field.tag_config("red", foreground="orange")

    def place_widgets(self):
        self.host_label.grid(row=0, column=0, padx=(0, 10))

        self.host_entry.grid(row=0, column=1, padx=(0, 10))

        self.port_label.grid(row=0, column=2, padx=(0, 10))

        self.port_entry.grid(row=0, column=3)

        self.connect_button.grid(row=1, column=0, padx=(0, 10))
        self.disconnect_button.grid(row=1, column=1, padx=(0, 10))
        self.save_button.grid(row=1, column=2)

        self.status_label.grid(row=2, column=0, pady=10)

        self.setting_frame.pack(pady=(0, 10))
        self.button_frame.pack(pady=(0, 10))
        self.status_frame.pack(pady=(0, 10))

    def start_connection(self):
        host = self.host_entry.get()
        port = self.port_entry.get()

        if not port.isdigit():
            messagebox.showerror("Error", "Port must be a number.")
            return

        self.client = SocketClient(host, int(port))
        if self.client.connect():
            self.status_label.configure(text="Status: Active")
            self.client.login()
        else:
            self.status_label.configure(text="Status: Inactive")
            messagebox.showerror("Error", "Connection failed.")

    def on_disconnect_button_click(self):
        self.client.sock.close()
        self.status_label.configure(text="Status: Inactive")
        self.client = None
