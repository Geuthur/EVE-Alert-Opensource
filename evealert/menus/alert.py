import customtkinter
import pyautogui
from pynput import keyboard, mouse

from evealert.alert import AlertAgent, wincap
from evealert.exceptions import ScreenshotError
from evealert.functions import (
    create_alert_region,
    create_faction_region,
    create_screenshot_region,
)
from evealert.menus.configuration import ConfigMenu
from evealert.menus.description import DescriptionMenu
from evealert.settings.logger import logging
from evealert.settings.settings import SettingsManager

logger = logging.getLogger("alert")

customtkinter.set_appearance_mode("dark")
customtkinter.set_default_color_theme("dark-blue")

WINDOW_WIDTH = 500
WINDOW_HEIGHT = 300


class Screenshot:
    """Screenshot Class for the Alert System"""

    def __init__(self, main):
        self.main = main
        self.taking_screenshot = False
        self.screenshot_overlay = None
        self.screenshot_mode = 0
        self.start_x, self.start_y = None, None
        self.end_x, self.end_y = None, None


class AlertButton:
    def __init__(self, main):
        self.main = main
        self.init_buttons()

    def init_buttons(self):
        self.save_button = customtkinter.CTkButton(
            self.main.settings_label_frame,
            text="Save",
            command=self.save_button_clicked,
        )

        self.description_button = customtkinter.CTkButton(
            self.main.settings_label_frame,
            text="Config Mode",
            command=self.description_mode_toggle,
        )

        self.config_button = customtkinter.CTkButton(
            self.main.settings_label_frame,
            text="Settings",
            command=self.config_mode_toggle,
        )
        self.save_button.grid(row=0, column=0, padx=(0, 10))
        self.description_button.grid(row=0, column=1, padx=(0, 10))
        self.config_button.grid(row=0, column=2)

    def save_button_clicked(self):
        self.main.system_label.configure(
            text="System: ✅ Settings Saved.", text_color="green"
        )

        self.main.save_settings()

    def description_mode_toggle(self):
        self.main.descmenu.open_description_window()

    def config_mode_toggle(self):
        self.main.configmenu.open_description_window()


class AlertMenu:
    """Main Menu for the Alert System"""

    def __init__(self, root: customtkinter.CTk):
        self.root = root
        self.init_menu()
        self.settings = SettingsManager()
        self.alarm = AlertAgent()
        self.configmenu = ConfigMenu(self)
        self.descmenu = DescriptionMenu(self)
        self.screenshot = Screenshot(self)
        self.buttons = AlertButton(self)
        self.config_mode = False
        self.set_alert_region = False
        self.alert_region_mode = 0
        self.set_faction_region = False
        self.faction_region_mode = 0
        self.taking_screenshot = False

    def init_menu(self):
        """Initializes the Main Menu for the Alert System."""
        # Setze die Größe des Fensters
        self.root.geometry(f"{WINDOW_WIDTH}x{WINDOW_HEIGHT}")

        # 1 Row - Init
        self.mouse_position_label = customtkinter.CTkLabel(
            self.root, text="", justify="left"
        )
        self.timer_var = customtkinter.CTkEntry(self.root)

        # Row 12
        # System Info
        # self.system_label = customtkinter.CTkLabel(root, text="System: ")
        credit_label = customtkinter.CTkLabel(self.root, text="Powered by Geuthur")

        self.mouse_position_label.pack()

        # Settings System
        self.settings_label_frame = customtkinter.CTkFrame(self.root)

        self.settings_label_frame.pack()

        empty_label = customtkinter.CTkLabel(self.root, text="")
        empty_label.pack()

        # Alert System
        alert_label_frame = customtkinter.CTkFrame(self.root)

        # Erstellen Sie das system_label im Frame
        show_alert_button = customtkinter.CTkButton(
            alert_label_frame,
            text="Show Alert Region",
            command=self.display_alert_region,
        )
        show_faction_button = customtkinter.CTkButton(
            alert_label_frame,
            text="Show Faction Region",
            command=self.display_faction_region,
        )

        # Platzieren Sie das Frame mit pack oder grid, je nach Ihren Anforderungen
        show_alert_button.grid(row=0, column=1, padx=(0, 10))
        show_faction_button.grid(
            row=0,
            column=2,
        )

        alert_label_frame.pack()

        empty_label = customtkinter.CTkLabel(self.root, text="")
        empty_label.pack()

        # Start Stopp System
        engine_label_frame = customtkinter.CTkFrame(self.root)

        start_button = customtkinter.CTkButton(
            engine_label_frame,
            text="Start Script",
            command=lambda: self.start_alert_script(self.system_label),
        )
        stop_button = customtkinter.CTkButton(
            engine_label_frame, text="Stop Script", command=self.stop_alert_script
        )
        exit_button = customtkinter.CTkButton(
            engine_label_frame, text="Exit", command=self.exit_button_clicked
        )

        # Platzieren Sie das Frame mit pack oder grid, je nach Ihren Anforderungen
        start_button.grid(row=0, column=0, padx=(0, 10))
        stop_button.grid(row=0, column=1, padx=(0, 10))
        exit_button.grid(row=0, column=2)

        engine_label_frame.pack()

        # System Info Label
        system_label_frame = customtkinter.CTkFrame(self.root)

        # Erstellen Sie das system_label im Frame
        self.system_label = customtkinter.CTkLabel(system_label_frame, text="")

        # Platzieren Sie das Frame mit pack oder grid, je nach Ihren Anforderungen
        self.system_label.grid(row=1, column=2)

        system_label_frame.pack()

        credit_label.pack()

        # Other
        mouse_listener = mouse.Listener(on_click=self.on_click)
        mouse_listener.start()

        keyboard_listener = keyboard.Listener(on_release=self.on_key_release)
        keyboard_listener.start()

        self.update_mouse_position_label()

    # Save Files
    def save_settings(self):
        """Save the settings to the settings.json file."""
        if not (
            self.configmenu.alert_region_x_first.get()
            and self.configmenu.alert_region_y_first.get()
        ) or not (
            self.configmenu.alert_region_x_second.get()
            and self.configmenu.alert_region_y_second.get()
        ):
            self.system_label.configure(
                text="System: ❎ Empty Fields. Minimum is Alert Region",
                text_color="red",
            )
            return
        self.settings.save_settings(
            {
                "logging": self.configmenu.logging.get(),
                "alert_region_x_first": self.configmenu.alert_region_x_first.get(),
                "alert_region_y_first": self.configmenu.alert_region_y_first.get(),
                "alert_region_x_second": self.configmenu.alert_region_x_second.get(),
                "alert_region_y_second": self.configmenu.alert_region_y_second.get(),
                "faction_region_x_first": self.configmenu.faction_region_x_first.get(),
                "faction_region_y_first": self.configmenu.faction_region_y_first.get(),
                "faction_region_x_second": self.configmenu.faction_region_x_second.get(),
                "faction_region_y_second": self.configmenu.faction_region_y_second.get(),
                "detectionscale": self.configmenu.detectionscale.get(),
                "mode_var": self.configmenu.mode_var.get(),
                "cooldown_timer": self.configmenu.cooldown_timer.get(),
            }
        )
        self.alarm.set_settings()

    def is_configmode(self):
        """Returns the current config mode."""
        return self.config_mode

    def toggle_configmode(self):
        """Toggle the config mode."""
        if self.is_configmode():
            self.config_mode = False
            self.set_alert_region = False
            self.alert_region_mode = 0
            self.set_faction_region = False
            self.faction_region_mode = 0
            self.taking_screenshot = False

    def display_alert_region(self):
        """Display the alert region on the screen."""
        selected_mode = self.configmenu.mode_var.get()
        if selected_mode == "picture":
            self.root.after(0, self.alarm.set_vision)
        else:
            self.root.after(0, create_alert_region(self.root, self.system_label))

    def display_faction_region(self):
        """Display the faction region on the screen."""
        selected_mode = self.configmenu.mode_var.get()
        if selected_mode == "picture":
            self.root.after(0, self.alarm.set_vision_faction)
        else:
            self.root.after(0, create_faction_region(self.root, self.system_label))

    def display_screenshot_region(self, x, y, width, height):
        """Display the screenshot region on the screen."""
        self.screenshot.screenshot_overlay = create_screenshot_region(
            x,
            y,
            width,
            height,
            self.root,
            self.system_label,
            self.screenshot.screenshot_overlay,
        )
        self.root.after(0)

    # Mouse Functions
    def update_mouse_position_label(self):
        """Update the mouse position label."""
        x, y = pyautogui.position()
        self.mouse_position_label.configure(text=f"Mausposition: X={x}, Y={y}")
        self.root.after(100, self.update_mouse_position_label)

    def on_click(self, x, y, button, pressed):
        if self.config_mode:
            if (
                pressed
                and self.set_alert_region
                and not self.set_faction_region
                and not self.taking_screenshot
                and button == mouse.Button.middle
            ):
                y, x = pyautogui.position()
                self.alert_region_mode = (self.alert_region_mode) % 2

                if self.alert_region_mode == 0:
                    print("First Region Set.")
                    self.configmenu.alert_region_x_first.delete(0, customtkinter.END)
                    self.configmenu.alert_region_y_first.delete(0, customtkinter.END)
                    self.configmenu.alert_region_x_first.insert(0, str(y))
                    self.configmenu.alert_region_y_first.insert(0, str(x))
                    self.alert_region_mode = self.alert_region_mode + 1
                else:
                    print("Second Region Set")
                    self.configmenu.alert_region_x_second.delete(0, customtkinter.END)
                    self.configmenu.alert_region_y_second.delete(0, customtkinter.END)
                    self.configmenu.alert_region_x_second.insert(0, str(y))
                    self.configmenu.alert_region_y_second.insert(0, str(x))
                    self.set_alert_region = False
                    self.alert_region_mode = 0
                    self.save_settings()
                    self.system_label.configure(
                        text="✅ Positions Saved", text_color="green"
                    )

            if (
                pressed
                and self.set_faction_region
                and not self.set_alert_region
                and not self.taking_screenshot
                and button == mouse.Button.middle
            ):
                y, x = pyautogui.position()
                self.faction_region_mode = (self.faction_region_mode) % 2

                if self.faction_region_mode == 0:
                    print("First Region Set.")
                    self.configmenu.faction_region_x_first.delete(0, customtkinter.END)
                    self.configmenu.faction_region_y_first.delete(0, customtkinter.END)
                    self.configmenu.faction_region_x_first.insert(0, str(y))
                    self.configmenu.faction_region_y_first.insert(0, str(x))
                    self.faction_region_mode = self.faction_region_mode + 1
                else:
                    print("Second Region Set")
                    self.configmenu.faction_region_x_second.delete(0, customtkinter.END)
                    self.configmenu.faction_region_y_second.delete(0, customtkinter.END)
                    self.configmenu.faction_region_x_second.insert(0, str(y))
                    self.configmenu.faction_region_y_second.insert(0, str(x))
                    self.set_faction_region = False
                    self.faction_region_mode = 0
                    self.save_settings()
                    self.system_label.configure(
                        text="✅ Positions Saved", text_color="green"
                    )

            if (
                pressed
                and self.taking_screenshot
                and not self.set_faction_region
                and not self.set_alert_region
                and button == mouse.Button.middle
            ):
                x, y = pyautogui.position()
                self.screenshot.screenshot_mode = (self.screenshot.screenshot_mode) % 2

                if self.screenshot.screenshot_mode == 0:
                    if self.screenshot.screenshot_overlay:
                        self.screenshot.screenshot_overlay.destroy()
                    self.screenshot.start_x, self.screenshot.start_y = x, y
                    print("Screenshot Position Set")
                    self.screenshot.screenshot_mode = (
                        self.screenshot.screenshot_mode + 1
                    )
                elif self.screenshot.screenshot_mode == 1:
                    self.screenshot.end_x, self.screenshot.end_y = x, y
                    print("Screenshot Position 2 Set")
                    self.system_label.configure(text="Press F3 to confirm")
                    self.screenshot.screenshot_mode = 0
                    try:
                        self.display_screenshot_region(
                            self.screenshot.start_x,
                            self.screenshot.start_y,
                            abs(self.screenshot.end_x - self.screenshot.start_x),
                            abs(self.screenshot.end_y - self.screenshot.start_y),
                        )
                    except Exception as e:
                        logger.error("Screenshot Error: %s", e)
                        self.system_label.configure(
                            text="System: ❎ Draw Screenshot something Wrong.",
                            text_color="red",
                        )

    # pylint: disable=too-many-nested-blocks
    # Keyboard Functions
    def on_key_release(self, key):
        if self.config_mode:
            if key == keyboard.Key.f1:
                if not self.set_alert_region:
                    self.taking_screenshot = False
                    self.set_faction_region = False
                    self.set_alert_region = True
                    self.system_label.configure(
                        text="Alert Mode: ✅ Active.", text_color="yellow"
                    )
                else:
                    self.set_alert_region = False
            if key == keyboard.Key.f2:
                if not self.set_faction_region:
                    self.taking_screenshot = False
                    self.set_alert_region = False
                    self.set_faction_region = True
                    self.system_label.configure(
                        text="Faction Mode: ✅ Active.", text_color="yellow"
                    )
                else:
                    self.set_faction_region = False
            if key == keyboard.Key.f3:
                if not self.taking_screenshot:
                    self.taking_screenshot = True
                    self.set_faction_region = False
                    self.set_alert_region = False
                    self.screenshot.start_x, self.screenshot.start_y = None, None
                    self.screenshot.end_x, self.screenshot.end_y = None, None
                    self.system_label.configure(
                        text="Screenshot Mode: ✅ Active.", text_color="yellow"
                    )
                else:
                    self.taking_screenshot = False
                    if (
                        self.screenshot.start_x is not None
                        and self.screenshot.start_y is not None
                        and self.screenshot.end_x is not None
                        and self.screenshot.end_y is not None
                    ):
                        try:
                            if self.screenshot.screenshot_overlay:
                                self.screenshot.screenshot_overlay.destroy()
                            screenshot = wincap.take_screenshot(
                                self.screenshot.start_x,
                                self.screenshot.start_y,
                                self.screenshot.end_y - self.screenshot.start_y,
                                self.screenshot.end_x - self.screenshot.start_x,
                            )
                            # screenshot = pyautogui.screenshot(region=(start_x, start_y, end_x - start_x, end_y - start_y))
                            if screenshot:
                                self.system_label.configure(
                                    text="✅ Screenshot Saved.", text_color="green"
                                )
                            else:
                                raise ScreenshotError("Screenshot Error")
                        except Exception as e:
                            print(e)
                            self.system_label.configure(
                                text="Screenshot Mode: ❎ Positions wrong.",
                                text_color="red",
                            )

    # Menu Button Section

    def exit_button_clicked(self):
        if self.alarm.is_running():
            self.alarm.stop()
            self.system_label.configure(
                text="System: ❎ EVE Alert stopped.", text_color="red"
            )
        else:
            self.system_label.configure(
                text="System: ❎ EVE Alert isn't running.", text_color="red"
            )
        self.root.destroy()

    # Starten Sie den Alert-Thread, indem Sie die Alert-Funktion aus alert.py aufrufen
    def start_alert_script(self, system_label):
        if self.settings:
            if not self.alarm.is_running():
                self.alarm.set_system_label(system_label)
                alarm = self.alarm.start()
                if alarm:
                    self.system_label.configure(
                        text="System: ✅ EVE Alert started", text_color="green"
                    )
                else:
                    self.system_label.configure(
                        text="System: ❎ Wrong Alert settings.", text_color="red"
                    )
            else:
                self.system_label.configure(
                    text="System: ❎ EVE Alert is already running.", text_color="green"
                )
        else:
            self.system_label.configure(
                text="System: ❎ No Settings found.", text_color="red"
            )

    def stop_alert_script(self):
        if self.alarm.is_running():
            self.alarm.set_system_label(self.system_label)
            self.alarm.stop()
            self.system_label.configure(
                text="System: ❎ EVE Alert stopped.", text_color="red"
            )
            return
        self.system_label.configure(
            text="System: ❎ EVE Alert isn't running.", text_color="red"
        )
