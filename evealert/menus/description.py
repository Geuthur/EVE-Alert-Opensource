from typing import TYPE_CHECKING

import customtkinter

if TYPE_CHECKING:
    from .alert import AlertMenu


class DescriptionMenu:
    """Description Menu for the configuration mode."""

    def __init__(self, main: "AlertMenu"):
        self.main = main
        self.active = False

    def open_description_window(self):
        """Opoens the description window for the configuration mode."""
        if not self.active:
            self.active = True
            self.main.config_mode = True
            self.main.buttons.description_button.configure(
                fg_color="#fa0202", hover_color="#bd291e"
            )

            self.description_window = customtkinter.CTkToplevel(self.main)
            self.description_window.title("Config Mode")

            # Position des Beschreibungsfensters rechts neben dem Hauptmenü
            main_menu_x, main_menu_y = (
                self.main.winfo_x(),
                self.main.winfo_y(),
            )
            main_menu_width, main_menu_height = (
                self.main.winfo_width(),
                self.main.winfo_height(),
            )

            description_window_width = 420
            description_window_height = 300

            description_window_x = main_menu_x + main_menu_width + 10
            description_window_y = (
                main_menu_y + main_menu_height + 40
                if self.main.config_mode
                else main_menu_y
            )
            if not self.main.settingsmenu.active:
                description_window_y = main_menu_y

            self.description_window.geometry(
                f"{description_window_width}x{description_window_height}+{description_window_x}+{description_window_y}"
            )

            description_text = "Alert Region: Press F1 to activate.\n"
            description_text += "Faction Mode: Press F2 to activate.\n"
            description_text += (
                "\nAfter pressing F1 or F2 set your region with Marquee Selection.\n"
            )
            description_text += "\nTo abort everything you can Press ESC.\n"

            # Verwende ein eigenes Frame für das Menü
            menu_frame = customtkinter.CTkFrame(self.description_window)
            menu_frame.pack(side="left", padx=20, pady=20)

            description_label = customtkinter.CTkLabel(
                menu_frame, text=description_text, justify="left"
            )
            description_label.pack(padx=20, pady=20)

            def close_description_window():
                self.main.buttons.description_button.configure(
                    fg_color="#1f538d", hover_color="#14375e"
                )
                self.main.config_mode = False
                self.main.toggle_configmode()
                self.description_window.destroy()

            self.description_window.protocol(
                "WM_DELETE_WINDOW", close_description_window
            )

            close_button = customtkinter.CTkButton(
                menu_frame, text="Schließen", command=close_description_window
            )
            close_button.pack(pady=10)
        else:
            self.active = False
            self.main.buttons.description_button.configure(
                fg_color="#1f538d", hover_color="#14375e"
            )
            self.main.config_mode = False
            self.main.toggle_configmode()
            self.description_window.destroy()
