import pyautogui, logging
import customtkinter
import tkinter as tk

from pynput import mouse, keyboard
from datetime import datetime

from evealert import __version__

from evealert.config import *
from evealert.alert import Alert_Agent, wincap
from evealert.functions import get_resource_path, create_alert_region, create_faction_region, create_screenshot_region

from customtkinter import CTkFrame, CTkLabel
from evealert.menus.settings import settings

customtkinter.set_appearance_mode("dark")
customtkinter.set_default_color_theme("dark-blue")

# Pfad zur JSON-Datei für die Einstellungen
logger = logging.getLogger('alert')
now = datetime.now()

logger.error("Error")

class DescriptionMenu:
    def __init__(self, root):
        self.root = root
        self.active = False
        self.description_window = None
        self.config_mode = False
        
        self.description_window_y = None
        
    def open_description_window(self):
        if not self.config_mode:
            self.config_mode = True
            app.config_mode = True
            app.description_button.configure(fg_color="#fa0202", hover_color="#bd291e")

            self.description_window = customtkinter.CTkToplevel(self.root)
            self.description_window.title("Config Mode")
            
            # Position des Beschreibungsfensters rechts neben dem Hauptmenü
            self.main_menu_x, self.main_menu_y = self.root.winfo_x(), self.root.winfo_y()
            self.main_menu_width, self.main_menu_height = self.root.winfo_width(), self.root.winfo_height()
            
            self.description_window_width = 400
            self.description_window_height = 300
            self.description_window_x = self.main_menu_x + self.main_menu_width + 10
            self.description_window_y = self.main_menu_y + self.main_menu_height + 40 if config.config_mode and desc.config_mode else self.main_menu_y
            if config.config_window_y and self.description_window_y == config.config_window_y:
                self.description_window_y = self.main_menu_y
            
            self.description_window.geometry(f"{self.description_window_width}x{self.description_window_height}+{self.description_window_x}+{self.description_window_y}")

            self.description_text = "Alert Region: Press F1 to activate.\n"
            self.description_text += "If activated Press MIDDLE Mouse Button to set positions.\n"
            self.description_text += "Faction Mode: Press F2 to activate.\n"
            self.description_text += "If activated Press MIDDLE Mouse Button to set positions.\n"
            self.description_text += "Screenshot Mode: Press F3 to activate.\n"
            self.description_text += "If activated Press MIDDLE Mouse Button to set positions.\n"
            self.description_text += "\nImportant: You must begin \nfrom the left upper corner to the right lower corner.\n"
            
            # Verwende ein eigenes Frame für das Menü
            menu_frame = customtkinter.CTkFrame(self.description_window)
            menu_frame.pack(side="left", padx=20, pady=20)
            
            self.description_label = customtkinter.CTkLabel(menu_frame, text=self.description_text, justify='left')
            self.description_label.pack(padx=20, pady=20)
            
            def close_description_window():
                app.description_button.configure(fg_color="#1f538d", hover_color="#14375e")
                self.config_mode = False
                app.toggle_configmode()
                app.system_label.configure(text="", text_color="green")
                self.description_window.destroy()

            self.description_window.protocol("WM_DELETE_WINDOW", close_description_window)

            self.close_button = customtkinter.CTkButton(menu_frame, text="Schließen", command=close_description_window)
            self.close_button.pack(pady=10)
        else:
            app.description_button.configure(fg_color="#1f538d", hover_color="#14375e")
            self.config_mode = False
            app.toggle_configmode()
            app.system_label.configure(text="", text_color="green")
            self.description_window.destroy()

class ConfigMenu:
    def __init__(self, root):
        self.root = root
        self.active = False
        self.settings = settings()
        self.config_mode = False

        self.config_window_y = None
        
        self.load_settings()

    def load_settings(self):
        self.config_window = customtkinter.CTkToplevel(self.root)
        self.config_window.title("Settings")

        self.config_window.withdraw()
        
        # Verwende ein eigenes Frame für das Menü
        self.menu_frame = customtkinter.CTkFrame(self.config_window)
        self.menu_frame.pack(side="left", padx=20, pady=20)

        self.logging = customtkinter.CTkEntry(self.menu_frame)
        
        # 1 Row - Init
        self.label_x_axis = customtkinter.CTkLabel(self.menu_frame, text="X-Achse")
        self.label_y_axis = customtkinter.CTkLabel(self.menu_frame, text="Y-Achse")

        # 2 Row - Init
        # Alert Region Position 1
        self.alert_region_label_1 = customtkinter.CTkLabel(self.menu_frame, text="Alert Region Left Upper Corner:", justify='left')
        self.alert_region_x_first = customtkinter.CTkEntry(self.menu_frame)
        self.alert_region_y_first = customtkinter.CTkEntry(self.menu_frame)

        # 3 Row - Init
        # Alert Region Position 2
        self.alert_region_label_2 = customtkinter.CTkLabel(self.menu_frame, text="Alert Region Right Lower Corner:", justify='left')
        self.alert_region_x_second = customtkinter.CTkEntry(self.menu_frame)
        self.alert_region_y_second = customtkinter.CTkEntry(self.menu_frame)
        
        # 4 Row - Init
        # Alert Region Position 1
        self.faction_region_label_1 = customtkinter.CTkLabel(self.menu_frame, text="Faction Region Left Upper Corner:", justify='left')
        self.faction_region_x_first = customtkinter.CTkEntry(self.menu_frame)
        self.faction_region_y_first = customtkinter.CTkEntry(self.menu_frame)

        # 5 Row - Init
        # Alert Region Position 2
        self.faction_region_label_2 = customtkinter.CTkLabel(self.menu_frame, text="Faction Region Right Lower Corner:", justify='left')
        self.faction_region_x_second = customtkinter.CTkEntry(self.menu_frame)
        self.faction_region_y_second = customtkinter.CTkEntry(self.menu_frame)
        
        # Row 6 - Init
        # Slider
        self.slider_label = customtkinter.CTkLabel(self.menu_frame, text="Detection Threshold")
        self.detectionscale = tk.DoubleVar()
        self.detectionscale.set(70)  # Setzen Sie den Standardwert auf 70
        self.slider = customtkinter.CTkSlider(self.menu_frame, from_=0, to=100, orientation="horizontal", number_of_steps=100, variable=self.detectionscale, command=self.slider_event)
        self.mode_var = customtkinter.StringVar(value="color")
        
        # Row 7
        # Config / Detection Mode- Init
        self.mode_checkbox = customtkinter.CTkCheckBox(self.menu_frame, text="Detection Mode", variable=self.mode_var, onvalue="color", offvalue="picture", command=self.update_mode)

        self.cooldown_timer_label = customtkinter.CTkLabel(self.menu_frame, text="Cooldown Timer:", justify='left')
        self.cooldown_timer = customtkinter.CTkEntry(self.menu_frame)
        self.cooldown_timer_text = customtkinter.CTkLabel(self.menu_frame, text="Seconds", justify='left')
        
        if self.settings:
            self.settingsvalue = self.settings.open_settings()
            self.logging.insert(0, self.settingsvalue["logging"])
            self.alert_region_x_first.insert(0, self.settingsvalue["alert_region_1"]["x"])
            self.alert_region_y_first.insert(0, self.settingsvalue["alert_region_1"]["y"])
            self.alert_region_x_second.insert(0, self.settingsvalue["alert_region_2"]["x"])
            self.alert_region_y_second.insert(0, self.settingsvalue["alert_region_2"]["y"])
            self.faction_region_x_first.insert(0, self.settingsvalue["faction_region_1"]["x"])
            self.faction_region_y_first.insert(0, self.settingsvalue["faction_region_1"]["y"])
            self.faction_region_x_second.insert(0, self.settingsvalue["faction_region_2"]["x"])
            self.faction_region_y_second.insert(0, self.settingsvalue["faction_region_2"]["y"])
            self.detectionscale.set(self.settingsvalue["detectionscale"]["value"])
            self.mode_var.set(self.settingsvalue["detection_mode"]["value"])
            self.cooldown_timer.insert(0, self.settingsvalue["cooldown_timer"]["value"])

    def open_description_window(self):
        if not self.config_mode:
            self.config_mode = True
            app.config_button.configure(fg_color="#fa0202", hover_color="#bd291e")

            # Position des Beschreibungsfensters rechts neben dem Hauptmenü
            self.main_menu_x, self.main_menu_y = self.root.winfo_x(), self.root.winfo_y()
            self.main_menu_width, self.main_menu_height = self.root.winfo_width(), self.root.winfo_height()
            
            self.config_window_width = 650
            self.config_window_height = 320
            self.config_window_x = self.main_menu_x + self.main_menu_width + 10
            self.config_window_y = self.main_menu_y + self.main_menu_height + 40 if desc.config_mode and config.config_mode else self.main_menu_y
            if desc.description_window_y and self.config_window_y == desc.description_window_y:
                self.config_window_y = self.main_menu_y
            
            self.config_window.geometry(f"{self.config_window_width}x{self.config_window_height}+{self.config_window_x}+{self.config_window_y}")

            self.config_window.deiconify()
                
            self.empty_label_1 = customtkinter.CTkLabel(self.menu_frame, text=self.slider.get())
            self.empty_label_00 = customtkinter.CTkLabel(self.menu_frame, text=self.mode_var.get())

            self.label_x_axis.grid(row=0, column=1)
            self.label_y_axis.grid(row=0, column=2)

            # Alert Region 1 Visual
            self.alert_region_label_1.grid(row=1, column=0, padx=20)
            self.alert_region_x_first.grid(row=1, column=1)
            self.alert_region_y_first.grid(row=1, column=2)

            # Alert Region 2 Visual
            self.alert_region_label_2.grid(row=2, column=0, padx=20)
            self.alert_region_x_second.grid(row=2, column=1)
            self.alert_region_y_second.grid(row=2, column=2)

            # Faction Region 1 Visual
            self.faction_region_label_1.grid(row=3, column=0, padx=20)
            self.faction_region_x_first.grid(row=3, column=1)
            self.faction_region_y_first.grid(row=3, column=2)

            # Faction Region 2 Visual
            self.faction_region_label_2.grid(row=4, column=0, padx=20)
            self.faction_region_x_second.grid(row=4, column=1)
            self.faction_region_y_second.grid(row=4, column=2)

            # Faction Region 2 Visual
            self.cooldown_timer_label.grid(row=5, column=0, padx=20)
            self.cooldown_timer.grid(row=5, column=1, padx=20)
            self.cooldown_timer_text.grid(row=5, column=2)
            
            # Slider Visual
            self.empty_label_1.grid(row=6, column=2)

            # Slider Visual
            self.slider_label.grid(row=6, column=0)
            self.slider.grid(row=6, column=1)
            
            # Mode Change
            self.mode_checkbox.grid(row=7, column=1)
            self.empty_label_00.grid(row=7, column=2)
            
            def close_config_window():
                app.config_button.configure(fg_color="#1f538d", hover_color="#14375e")
                self.config_mode = False
                self.config_window.withdraw()

            self.config_window.protocol("WM_DELETE_WINDOW", close_config_window)

            self.close_button = customtkinter.CTkButton(self.menu_frame, text="Schließen", command=close_config_window)
            self.close_button.grid(column=1, pady=10)
        else:
            self.config_mode = False
            app.config_button.configure(fg_color="#1f538d", hover_color="#14375e")
            self.config_window.withdraw()
            
    def update_mode(self):
        selected_mode = self.mode_var.get()
        if selected_mode == "color" and app.alarm.get_vision() == True:
            app.alarm.set_vision()
            app.alarm.set_vision_faction()
        app.save_settings()
        self.empty_label_00.configure(text=selected_mode)
         
    def slider_event(self, slider_value):
        self.empty_label_1.configure(text=slider_value)

class AlertMenu:
    def __init__(self, root):
        self.root = root
        self.settings = settings()
        self.alarm = Alert_Agent()
        self.config_mode = False
        self.set_alert_region = False
        self.alert_region_mode = 0
        self.set_faction_region = False
        self.faction_region_mode = 0
        self.taking_screenshot = False
        
        # Setze die Größe des Fensters
        self.root.geometry(f"{window_width}x{window_height}")
        
        # 1 Row - Init
        self.mouse_position_label = customtkinter.CTkLabel(root, text="", justify='left')
        self.timer_var = customtkinter.CTkEntry(root)

        # Row 12 
        # System Info
        #self.system_label = customtkinter.CTkLabel(root, text="System: ")
        self.credit_label = customtkinter.CTkLabel(root, text="Powered by Geuthur")

        self.mouse_position_label.pack()

        #self.save_button = customtkinter.CTkButton(self.engine_label_frame, text="Save", command=self.save_button_clicked)

        # Settings System
        self.settings_label_frame = CTkFrame(root)  # Stellen Sie sicher, dass Sie das Elternwidget korrekt ersetzen

        self.save_button = customtkinter.CTkButton(self.settings_label_frame, text="Save", command=self.save_button_clicked)
        self.description_button = customtkinter.CTkButton(self.settings_label_frame, text="Config Mode", command=self.description_mode_toggle)
        self.config_button = customtkinter.CTkButton(self.settings_label_frame, text="Settings", command=self.config_mode_toggle)

        # Platzieren Sie das Frame mit pack oder grid, je nach Ihren Anforderungen
        self.save_button.grid(row=0, column=0, padx=(0, 10))
        self.description_button.grid(row=0, column=1, padx=(0, 10))
        self.config_button.grid(row=0, column=2)

        self.settings_label_frame.pack()

        self.empty_label = customtkinter.CTkLabel(root, text="")
        self.empty_label.pack()

        # Alert System
        self.alert_label_frame = CTkFrame(root)  # Stellen Sie sicher, dass Sie das Elternwidget korrekt ersetzen

        # Erstellen Sie das system_label im Frame
        self.show_alert_button = customtkinter.CTkButton(self.alert_label_frame, text="Show Alert Region", command=self.display_alert_region)
        self.show_faction_button = customtkinter.CTkButton(self.alert_label_frame, text="Show Faction Region", command=self.display_faction_region)

        # Platzieren Sie das Frame mit pack oder grid, je nach Ihren Anforderungen
        self.show_alert_button.grid(row=0, column=1, padx=(0, 10))  # Beispiel für grid, passen Sie es an Ihre Bedürfnisse an
        self.show_faction_button.grid(row=0, column=2,)  # Beispiel für grid, passen Sie es an Ihre Bedürfnisse an

        self.alert_label_frame.pack()

        self.empty_label = customtkinter.CTkLabel(root, text="")
        self.empty_label.pack()
        
        # Start Stopp System
        self.engine_label_frame = CTkFrame(root)  # Stellen Sie sicher, dass Sie das Elternwidget korrekt ersetzen

        self.start_button = customtkinter.CTkButton(self.engine_label_frame, text="Start Script", command=lambda: self.start_alert_script(self.system_label))
        self.stop_button = customtkinter.CTkButton(self.engine_label_frame, text="Stop Script", command=self.stop_alert_script)
        self.exit_button = customtkinter.CTkButton(self.engine_label_frame, text="Exit", command=self.exit_button_clicked)

        # Platzieren Sie das Frame mit pack oder grid, je nach Ihren Anforderungen
        self.start_button.grid(row=0, column=0, padx=(0, 10))
        self.stop_button.grid(row=0, column=1, padx=(0, 10))
        self.exit_button.grid(row=0, column=2)

        self.engine_label_frame.pack()

        # System Info Label
        self.system_label_frame = CTkFrame(root)  # Stellen Sie sicher, dass Sie das Elternwidget korrekt ersetzen

        # Erstellen Sie das system_label im Frame
        self.system_label = CTkLabel(self.system_label_frame, text="")

        # Platzieren Sie das Frame mit pack oder grid, je nach Ihren Anforderungen
        self.system_label.grid(row=1, column=2)  # Beispiel für grid, passen Sie es an Ihre Bedürfnisse an

        self.system_label_frame.pack()

        self.credit_label.pack()

        # Other
        self.mouse_listener = mouse.Listener(on_click=self.on_click)
        self.mouse_listener.start()

        self.keyboard_listener = keyboard.Listener(on_release=self.on_key_release)
        self.keyboard_listener.start()

        self.update_mouse_position_label()
        
        self.config = config
        self.descmenu = desc
        
    # Save Files
    def save_settings(self):
        if not (self.config.alert_region_x_first.get() and self.config.alert_region_y_first.get()) or not (self.config.alert_region_x_second.get() and self.config.alert_region_y_second.get()):
            self.system_label.configure(text="System: ❎ Empty Fields. Minimum is Alert Region", text_color="red")
            return
        self.config.settings.save_settings({
            "logging": self.config.logging.get(),
            "alert_region_x_first": self.config.alert_region_x_first.get(),
            "alert_region_y_first": self.config.alert_region_y_first.get(),
            "alert_region_x_second": self.config.alert_region_x_second.get(),
            "alert_region_y_second": self.config.alert_region_y_second.get(),
            "faction_region_x_first": self.config.faction_region_x_first.get(),
            "faction_region_y_first": self.config.faction_region_y_first.get(),
            "faction_region_x_second": self.config.faction_region_x_second.get(),
            "faction_region_y_second": self.config.faction_region_y_second.get(),
            "detectionscale": self.config.detectionscale.get(),
            "mode_var": self.config.mode_var.get(),
            "cooldown_timer": self.config.cooldown_timer.get(),
        })
        self.alarm.set_settings()
    
    def is_configmode(self):
        return self.config_mode
    
    def toggle_configmode(self):
        if self.is_configmode():
            self.config_mode = False
            self.set_alert_region = False
            self.alert_region_mode = 0
            self.set_faction_region = False
            self.faction_region_mode = 0
            self.taking_screenshot = False
    
    def display_alert_region(self):
        selected_mode = self.config.mode_var.get()
        if selected_mode == "picture":
            self.root.after(0, self.alarm.set_vision)
        else:
            self.root.after(0, create_alert_region(self.root, self.system_label))

    def display_faction_region(self):
        selected_mode = self.config.mode_var.get()
        if selected_mode == "picture":
            self.root.after(0, self.alarm.set_vision_faction)
        else:
            self.root.after(0, create_faction_region(self.root, self.system_label))

    def display_screenshot_region(self, x, y, width, height):
        global screenshot_overlay
        screenshot_overlay = create_screenshot_region(x, y, width, height, self.root, self.system_label)
        self.root.after(0)

    # Mouse Functions
    def update_mouse_position_label(self):
        x, y = pyautogui.position()
        self.mouse_position_label.configure(text=f"Mausposition: X={x}, Y={y}")
        self.root.after(100, self.update_mouse_position_label)

    def on_click(self, x, y, button, pressed):
        if self.config_mode:
            if pressed and self.set_alert_region and not self.set_faction_region and not self.taking_screenshot and button == mouse.Button.middle:
                y, x = pyautogui.position()
                self.alert_region_mode = (self.alert_region_mode) % 2

                if self.alert_region_mode == 0:
                    print("First Region Set.")
                    self.config.alert_region_x_first.delete(0, tk.END)
                    self.config.alert_region_y_first.delete(0, tk.END)
                    self.config.alert_region_x_first.insert(0, str(y))
                    self.config.alert_region_y_first.insert(0, str(x))
                    self.alert_region_mode = (self.alert_region_mode + 1)
                else:
                    print("Second Region Set")
                    self.config.alert_region_x_second.delete(0, tk.END)
                    self.config.alert_region_y_second.delete(0, tk.END)
                    self.config.alert_region_x_second.insert(0, str(y))
                    self.config.alert_region_y_second.insert(0, str(x))
                    self.set_alert_region = False
                    self.alert_region_mode = 0
                    self.save_settings()
                    self.system_label.configure(text="✅ Positions Saved", text_color="green")
                pass

            if pressed and self.set_faction_region and not self.set_alert_region and not self.taking_screenshot and button == mouse.Button.middle:
                y, x = pyautogui.position()
                self.faction_region_mode = (self.faction_region_mode) % 2

                if self.faction_region_mode == 0:
                    print("First Region Set.")
                    self.config.faction_region_x_first.delete(0, tk.END)
                    self.config.faction_region_y_first.delete(0, tk.END)
                    self.config.faction_region_x_first.insert(0, str(y))
                    self.config.faction_region_y_first.insert(0, str(x))
                    self.faction_region_mode = (self.faction_region_mode + 1)
                else:
                    print("Second Region Set")
                    self.config.faction_region_x_second.delete(0, tk.END)
                    self.config.faction_region_y_second.delete(0, tk.END)
                    self.config.faction_region_x_second.insert(0, str(y))
                    self.config.faction_region_y_second.insert(0, str(x))
                    self.set_faction_region = False
                    self.faction_region_mode = 0
                    self.save_settings()
                    self.system_label.configure(text="✅ Positions Saved", text_color="green")
                pass

            global start_x, start_y, end_x, end_y

            if pressed and self.taking_screenshot and not self.set_faction_region and not self.set_alert_region and button == mouse.Button.middle:
                x, y = pyautogui.position()
                global screenshot_mode, screenshot_overlay
                screenshot_mode = (screenshot_mode) % 2

                if screenshot_mode == 0:
                    if screenshot_overlay:
                        screenshot_overlay.destroy()
                    start_x, start_y = x, y
                    print("Screenshot Position Set")
                    screenshot_mode = (screenshot_mode + 1)
                elif screenshot_mode == 1:
                    end_x, end_y = x, y
                    print("Screenshot Position 2 Set")
                    self.system_label.configure(text="Press F3 to confirm")
                    screenshot_mode = 0
                    try:
                        self.display_screenshot_region(start_x, start_y, abs(end_x - start_x), abs(end_y - start_y))
                    except Exception as e:
                        logger.error("Screenshot Error: %s", e)
                        self.system_label.configure(text="System: ❎ Draw Screenshot something Wrong.", text_color="red")

    # Keyboard Functions
    def on_key_release(self, key):
        global start_x, start_y, end_x, end_y
        if self.config_mode:
            if key == keyboard.Key.f1:
                if not self.set_alert_region:
                    self.taking_screenshot = False
                    self.set_faction_region = False
                    self.set_alert_region = True
                    self.system_label.configure(text="Alert Mode: ✅ Active.", text_color="yellow")
                else:
                    set_alert_region = False
            if key == keyboard.Key.f2:
                if not self.set_faction_region:
                    self.taking_screenshot = False
                    self.set_alert_region = False
                    self.set_faction_region = True
                    self.system_label.configure(text="Faction Mode: ✅ Active.", text_color="yellow")
                else:
                    set_faction_region = False
            if key == keyboard.Key.f3:
                if not self.taking_screenshot:
                    self.taking_screenshot = True
                    self.set_faction_region = False
                    self.set_alert_region = False
                    start_x, start_y = None, None
                    end_x, end_y = None, None
                    self.system_label.configure(text="Screenshot Mode: ✅ Active.", text_color="yellow")
                else:
                    self.taking_screenshot = False
                    if start_x is not None and start_y is not None and end_x is not None and end_y is not None:
                        try:
                            if screenshot_overlay:
                                screenshot_overlay.destroy()
                            screenshot = wincap.take_screenshot(start_x, start_y, end_x - start_x, end_y - start_y)
                            # screenshot = pyautogui.screenshot(region=(start_x, start_y, end_x - start_x, end_y - start_y))
                            if screenshot:
                                self.system_label.configure(text="✅ Screenshot Saved.", text_color="green")
                            else:
                                raise
                        except Exception as e:
                            print(e)
                            self.system_label.configure(text="Screenshot Mode: ❎ Positions wrong.", text_color="red")

    # Menu Button Section

    def save_button_clicked(self):
        self.system_label.configure(text="System: ✅ Settings Saved.", text_color="green")

        self.save_settings()

    def exit_button_clicked(self):
        if self.alarm.is_running:
            self.alarm.stop()
            self.system_label.configure(text="System: ❎ EVE Alert stopped.", text_color="red")
        else:
            self.system_label.configure(text="System: ❎ EVE Alert isn't running.", text_color="red")
        self.root.destroy()

    # Starten Sie den Alert-Thread, indem Sie die Alert-Funktion aus alert.py aufrufen
    def start_alert_script(self, system_label):
        if self.settings:
            if not self.alarm.is_running():
                self.alarm.set_system_label(system_label)
                alarm = self.alarm.start()
                if alarm:
                    self.system_label.configure(text="System: ✅ EVE Alert started", text_color="green")
                else:
                    self.system_label.configure(text="System: ❎ Wrong Alert settings.", text_color="red")
            else:
                self.system_label.configure(text="System: ❎ EVE Alert is already running.", text_color="green")
        else:
            self.system_label.configure(text="System: ❎ No Settings found.", text_color="red")

    def stop_alert_script(self):
        if self.alarm.is_running():
            self.alarm.set_system_label(self.system_label)
            self.alarm.stop()
            self.system_label.configure(text="System: ❎ EVE Alert stopped.", text_color="red")
            return
        self.system_label.configure(text="System: ❎ EVE Alert isn't running.", text_color="red")

    # Configuration Section

    def description_mode_toggle(self):
        self.descmenu.open_description_window()

    def config_mode_toggle(self):
        self.config.open_description_window()

# Menu Settings
root = customtkinter.CTk()
root.title(f"Alert - {__version__}")
root.iconbitmap(default=get_resource_path(icon_path))
desc = DescriptionMenu(root)
config = ConfigMenu(root)
app = AlertMenu(root)
root.mainloop()