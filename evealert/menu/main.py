import os
import threading
from datetime import datetime
from threading import Thread

import customtkinter
import pyautogui
from PIL import Image
from pynput import keyboard
from screeninfo import get_monitors

from evealert import __version__
from evealert.manager.alertmanager import AlertAgent
from evealert.menu.config import ConfigModeMenu
from evealert.menu.setting import SettingMenu
from evealert.server.server import ServerAgent
from evealert.settings.helper import ICON, get_resource_path
from evealert.settings.logger import logging
from evealert.tools.overlay import OverlaySystem

log_alert = logging.getLogger("alert")
log_menu = logging.getLogger("menu")
log_main = logging.getLogger("main")
log_tools = logging.getLogger("tools")
log_test = logging.getLogger("test")

customtkinter.set_appearance_mode("dark")
customtkinter.set_default_color_theme("dark-blue")

WINDOW_WIDTH = 500
WINDOW_HEIGHT = 350


class MainMenuButtons:
    def __init__(self, main: "MainMenu"):
        self.main = main
        self.init_buttons()

    def init_buttons(self):
        # Create Settings System
        self.settings_label_frame = customtkinter.CTkFrame(self.main)
        self.alert_label_frame = customtkinter.CTkFrame(self.main)

        self.config_mode_menu = customtkinter.CTkButton(
            self.settings_label_frame,
            text="Config Mode",
            command=self.config_mode_toggle,
        )

        self.setting_menu = customtkinter.CTkButton(
            self.settings_label_frame,
            text="Settings",
            command=self.settings_mode_toggle,
        )

        self.socket_server = customtkinter.CTkButton(
            self.settings_label_frame,
            text="Start Socket Server",
            command=self.socket_mode_toggle,
        )
        self.config_mode_menu.grid(row=0, column=1, padx=(0, 10))
        self.setting_menu.grid(row=0, column=2, padx=(0, 10))
        self.socket_server.grid(row=0, column=3)

        # Create Buttons
        self.show_alert_button = customtkinter.CTkButton(
            self.alert_label_frame,
            text="Show Alert Region",
            command=self.main.display_alert_region,
        )
        self.show_faction_button = customtkinter.CTkButton(
            self.alert_label_frame,
            text="Show Faction Region",
            command=self.main.display_faction_region,
        )
        self.show_status_label = customtkinter.CTkLabel(
            self.alert_label_frame,
            text="",
            compound="left",
            font=customtkinter.CTkFont(size=15, weight="bold"),
        )

        self.show_status_label.grid(row=0, column=0, padx=20, pady=20)
        self.show_alert_button.grid(row=0, column=1, padx=(0, 10))
        self.show_faction_button.grid(row=0, column=2, padx=(0, 10))

    def config_mode_toggle(self):
        try:
            self.main.menu.config.open_menu()
        except AttributeError as e:
            log_menu.exception("Config Menu Error: %s", e)
            self.main.write_message(
                "Config Menu: Error read logs for more information.", "red"
            )

    def settings_mode_toggle(self):
        try:
            self.main.menu.setting.open_menu()
        except AttributeError as e:
            log_menu.exception("Setting Menu Error: %s", e)
            self.main.write_message(
                "Setting Menu: Error read logs for more information.", "red"
            )

    def socket_mode_toggle(self):
        try:
            self.main.start_socket_system()
        except AttributeError as e:
            log_menu.exception("Socket Menu Error: %s", e)
            self.main.write_message(
                "Socket Menu: Error read logs for more information.", "red"
            )


class MenuManager:
    def __init__(self, main: "MainMenu"):
        self.mainmenu = main
        self.config = ConfigModeMenu(self.mainmenu)
        self.setting = SettingMenu(self.mainmenu)


class MainMenu(customtkinter.CTk):
    """Main Menu for the Alert System"""

    def __init__(self):
        super().__init__()
        self.title(f"Alert - {__version__}")
        self.mainmenu_buttons = MainMenuButtons(self)
        self.init_widgets()
        self.init_menu()

        # Menu System
        self.menu = MenuManager(self)
        # Overlay System
        self.overlay_system = OverlaySystem(self)
        # Alert System
        self.alert = AlertAgent(self)
        # Server Settings
        self.socket = ServerAgent(self)
        # Status System
        self.current_status = False
        self.check_status()

    def clean_up(self):
        """Cleanup the main system."""
        self.overlay_system.clean_up()
        self.menu.config.clean_up()
        self.alert.clean_up()
        self.socket.clean_up()
        self.destroy()

    def init_widgets(self):
        # Create the main window
        self.set_icon(ICON)
        self.geometry(f"{WINDOW_WIDTH}x{WINDOW_HEIGHT}")

        self.log_field = customtkinter.CTkTextbox(self, height=100, width=450)
        self.log_field.tag_config("normal", foreground="white")
        self.log_field.tag_config("green", foreground="lightgreen")
        self.log_field.tag_config("red", foreground="orange")

        # Create mouse position label
        self.mouse_position_label = customtkinter.CTkLabel(
            self, text="", justify="left"
        )

        # Create Empty Space
        self.empty_label = customtkinter.CTkLabel(self, text="")
        # Create Empty Space
        self.empty_label2 = customtkinter.CTkLabel(self, text="")
        # Create Empty Space
        self.empty_label3 = customtkinter.CTkLabel(self, text="")

        # Start Stopp System
        self.engine_label_frame = customtkinter.CTkFrame(self)

        # Status Label
        self.show_status_label = customtkinter.CTkLabel(
            self.mainmenu_buttons.alert_label_frame,
            text="",
            compound="left",
            font=customtkinter.CTkFont(size=15, weight="bold"),
        )
        # Status Icons
        self.online = customtkinter.CTkImage(
            Image.open(get_resource_path("img/online.png")), size=(24, 24)
        )
        self.offline = customtkinter.CTkImage(
            Image.open(get_resource_path("img/offline.png")), size=(24, 24)
        )
        # Start Stop Buttons
        self.start_button = customtkinter.CTkButton(
            self.engine_label_frame,
            text="Start Script",
            command=self.start_alert_script,
        )
        self.stop_button = customtkinter.CTkButton(
            self.engine_label_frame, text="Stop Script", command=self.stop_alert_script
        )
        self.exit_button = customtkinter.CTkButton(
            self.engine_label_frame, text="Exit", command=self.clean_up
        )
        # Close Button per Window Exit
        self.protocol("WM_DELETE_WINDOW", self.clean_up)

    def init_menu(self):
        """Initializes the Main Menu for the Alert System."""
        # Mouse Position Label
        self.mouse_position_label.pack()
        # Settings Label
        self.mainmenu_buttons.settings_label_frame.pack()
        # Empty Label
        self.empty_label.pack()
        # Alert Buttons Label
        self.mainmenu_buttons.alert_label_frame.pack()
        # Empty Label
        self.empty_label2.pack()
        # Engine Label
        self.engine_label_frame.pack()
        # Create Empty Space
        self.empty_label3.pack()
        # Log Field Label
        self.log_field.pack()
        # Status Label
        self.mainmenu_buttons.show_status_label.configure(image=self.offline)
        self.mainmenu_buttons.show_status_label.image = self.offline
        # Start Stop Buttons
        self.start_button.grid(row=0, column=0, padx=(0, 10))
        self.stop_button.grid(row=0, column=1, padx=(0, 10))
        self.exit_button.grid(row=0, column=2)

        keyboard_listener = keyboard.Listener(on_release=self.on_key_release)
        keyboard_listener.start()

        self.update_mouse_position_label()

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

    def write_message(self, text, color="normal"):
        """Write a message to the log field."""
        now = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        try:
            self.log_field.insert("1.0", f"[{now}] {text}\n", color)
        except Exception as e:
            log_main.error("Write Message Error: %s", e, exc_info=True)

    # Mouse Functions
    def update_mouse_position_label(self):
        """Update the mouse position label."""
        x, y = pyautogui.position()
        self.mouse_position_label.configure(text=f"Mausposition: X={x}, Y={y}")
        self.after(100, self.update_mouse_position_label)

    def start_overlay(self):
        """Generate the overlay."""
        monitor = self.get_current_monitor()
        if monitor:
            self.overlay_system.create_overlay(monitor)

    def get_current_monitor(self):
        """Get the current monitor where the mouse is."""
        mouse_x, mouse_y = pyautogui.position()
        for monitor in get_monitors():
            if (
                monitor.x <= mouse_x <= monitor.x + monitor.width
                and monitor.y <= mouse_y <= monitor.y + monitor.height
            ):
                return monitor
        return None

    def check_status(self):
        """Check the status of the alert."""
        if self.alert.is_running != self.current_status:
            if self.alert.is_running:
                self.mainmenu_buttons.show_status_label.configure(image=self.online)
                self.mainmenu_buttons.show_status_label.image = self.offline
            else:
                self.mainmenu_buttons.show_status_label.configure(image=self.offline)
                self.mainmenu_buttons.show_status_label.image = self.offline

            self.current_status = self.alert.is_running

        # Check the status again after (1 seconds)
        self.mainmenu_buttons.show_status_label.after(1000, self.check_status)

    def update_alert_button(self):
        if self.alert.alert_vision.is_vision_open and self.alert.is_running:
            self.mainmenu_buttons.show_alert_button.configure(
                fg_color="#fa0202", hover_color="#bd291e"
            )
        else:
            self.mainmenu_buttons.show_alert_button.configure(
                fg_color="#1f538d", hover_color="#14375e"
            )

    def display_alert_region(self):
        """Display the alert region on the screen."""
        self.after(0, self.alert.set_vision)

    def update_faction_button(self):
        if (
            self.alert.alert_vision_faction.is_faction_vision_open
            and self.alert.is_running
        ):
            self.mainmenu_buttons.show_faction_button.configure(
                fg_color="#fa0202", hover_color="#bd291e"
            )
        else:
            self.mainmenu_buttons.show_faction_button.configure(
                fg_color="#1f538d", hover_color="#14375e"
            )

    def display_faction_region(self):
        """Display the faction region on the screen."""
        self.after(0, self.alert.set_vision_faction)

    # pylint: disable=too-many-nested-blocks
    # Keyboard Functions
    def on_key_release(self, key):
        """Handle the key release event."""
        if self.menu.config.is_open:
            if key == keyboard.Key.f1:
                if (
                    not self.menu.config.is_alert_region
                    and not self.menu.config.is_faction_region
                ):
                    self.menu.config.faction_region = False
                    self.menu.config.alert_region = True
                    self.write_message("Settings: Enemy Active.")
                    self.after(0, self.start_overlay)
            if key == keyboard.Key.f2:
                if (
                    not self.menu.config.is_faction_region
                    and not self.menu.config.is_alert_region
                ):
                    self.menu.config.alert_region = False
                    self.menu.config.faction_region = True
                    self.write_message("Settings: Faction Active.")
                    self.after(0, self.start_overlay)
            elif key == keyboard.Key.esc:
                if self.overlay_system.overlay:
                    self.overlay_system.clean_up()
                    self.write_message("Settings: Aborted.")

    def start_alert_script(self):
        """Start the Alert System (Thread)."""
        try:
            if not self.alert.is_running:
                Thread(target=self.alert.start).start()
            else:
                self.write_message("System: EVE Alert is already running.")
        except Exception as e:
            log_alert.error("Start Alert Error: %s", e, exc_info=True)
            self.write_message("System: Something went wrong.", "red")

    def stop_alert_script(self):
        """Stop the Alert System."""
        if self.alert.is_running:
            self.alert.stop()
            self.write_message("System: EVE Alert stopped.", "red")
            return
        self.write_message("System: EVE Alert isn't running.")

    def start_socket_system(self):
        """Start the socket server in a new thread."""
        try:
            if not self.socket.running:
                self.socket_thread = threading.Thread(target=self.socket.start_server)
                self.socket_thread.start()
                self.mainmenu_buttons.socket_server.configure(
                    fg_color="#fa0202", hover_color="#bd291e"
                )
            else:
                self.socket.clean_up()
                self.write_message("Socket Server stopped.", "red")
        except Exception as e:
            log_main.error("Start Socket Error: %s", e, exc_info=True)
            self.write_message("System: Something went wrong.", "red")
