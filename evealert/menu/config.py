from typing import TYPE_CHECKING

import customtkinter

if TYPE_CHECKING:
    from evealert.menu.main import MainMenu


class ConfigModeMenu:
    """Description Menu for the configuration mode."""

    def __init__(self, main: "MainMenu"):
        self.main = main
        self.open = False
        self.changed = False

        self.alert_region = False
        self.faction_region = False

        self.description_window = customtkinter.CTkToplevel(self.main)
        self.description_window.title("Config Mode")
        self.description_window.withdraw()

        description_text = "Alert Region: Press F1 to activate.\n"
        description_text += "Faction Mode: Press F2 to activate.\n"
        description_text += (
            "\nAfter pressing F1 or F2 set your region with Marquee Selection.\n"
        )
        description_text += "\nTo abort everything Press ESC.\n"

        menu_frame = customtkinter.CTkFrame(self.description_window)
        menu_frame.pack(side="left", padx=20, pady=20)

        description_label = customtkinter.CTkLabel(
            menu_frame, text=description_text, justify="left"
        )
        description_label.pack(padx=20, pady=20)

        close_button = customtkinter.CTkButton(
            menu_frame, text="Close", command=self.clean_up
        )
        close_button.pack(pady=10)

        self.description_window.protocol("WM_DELETE_WINDOW", self.clean_up)

    @property
    def is_open(self):
        """Returns True if the description window is open."""
        return self.open

    @property
    def is_alert_region(self):
        """Returns True if the alert region is active."""
        return self.alert_region

    @property
    def is_faction_region(self):
        """Returns True if the faction region is active."""
        return self.faction_region

    @property
    def is_changed(self):
        """Returns True if the configuration mode has been changed."""
        return self.changed

    def clean_up(self):
        """Closes the description window if it is open."""
        if self.is_open:
            self.open = False
            self.main.mainmenu_buttons.config_mode_menu.configure(
                fg_color="#1f538d", hover_color="#14375e"
            )
            # hide the description window
            self.description_window.withdraw()

    def open_menu(self):
        """Opens the description window for the configuration mode."""
        if not self.is_open:
            self.open = True
            self.main.mainmenu_buttons.config_mode_menu.configure(
                fg_color="#fa0202", hover_color="#bd291e"
            )

            # position the description window to the right of the main menu
            main_menu_x, main_menu_y = (
                self.main.winfo_x(),
                self.main.winfo_y(),
            )
            main_menu_width, _ = (
                self.main.winfo_width(),
                self.main.winfo_height(),
            )

            description_window_width = 435
            description_window_height = 300

            description_window_x = main_menu_x + main_menu_width + 10
            description_window_y = main_menu_y

            self.description_window.geometry(
                f"{description_window_width}x{description_window_height}+{description_window_x}+{description_window_y}"
            )

            # show the description window
            self.description_window.deiconify()
        else:
            self.clean_up()
