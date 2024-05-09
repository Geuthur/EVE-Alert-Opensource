from pynput import mouse, keyboard
import pyautogui, sys, json, asyncio
from functions import *
from alert import Alert_Agent, wincap

# MENU SYSTEM
alarm_counter = 0

def main_menu():
    settings = open_settings()

    # Run Functon on Closing Menu
    def on_closing():
        alarm.stop()
        root.destroy()

    # Save Files
    def save_settings():
        if not (alert_region_x_first.get() and alert_region_y_first.get()) or not (alert_region_x_second.get() and alert_region_y_second.get()):
            system_label.configure(text="System: ❎ Empty Fields. Minimum is Alert Region", text_color="red")
            return
    
        settings = {
            "alert_region_1": {
                "x": alert_region_x_first.get(),
                "y": alert_region_y_first.get()
            },
            "alert_region_2": {
                "x": alert_region_x_second.get(),
                "y": alert_region_y_second.get()
            },
            "faction_region_1": {
                "x": faction_region_x_first.get(),
                "y": faction_region_y_first.get()
            },
            "faction_region_2": {
                "x": faction_region_x_second.get(),
                "y": faction_region_y_second.get()
            },
            "detectionscale": {
                "value": detectionscale.get()
            },
            "detection_mode": {
                "value": mode_var.get()
            }
        }
        with open(settings_file, 'w') as file:
            json.dump(settings, file, indent=4)
        alarm.set_settings()
    
    def display_alert_region():
        selected_mode = mode_var.get()
        if selected_mode == "picture":
            root.after(0, alarm.set_vision)
        else:
            root.after(0, create_alert_region(root, system_label))

    def display_faction_region():
        selected_mode = mode_var.get()
        if selected_mode == "picture":
            root.after(0, alarm.set_vision_faction)
        else:
            root.after(0, create_faction_region(root, system_label))

    def display_screenshot_region(x, y, width, height):
        global screenshot_overlay
        screenshot_overlay = create_screenshot_region(x, y, width, height, root, system_label)
        root.after(0)

    # Mouse Functions
    def update_mouse_position_label():
        x, y = pyautogui.position()
        mouse_position_label.configure(text=f"Mausposition: X={x}, Y={y}")
        root.after(100, update_mouse_position_label)

    def on_click(x, y, button, pressed):

        # Set Alert Region
        global set_alert_region
        # Set Faction Region
        global set_faction_region

        if pressed and set_alert_region and not set_faction_region and not taking_screenshot and button == mouse.Button.middle:
            y, x = pyautogui.position()
            global alert_region_mode
            alert_region_mode = (alert_region_mode) % 2

            if alert_region_mode == 0:
                print("First Region Set.")
                alert_region_x_first.delete(0, tk.END)
                alert_region_y_first.delete(0, tk.END)
                alert_region_x_first.insert(0, str(y))
                alert_region_y_first.insert(0, str(x))
                alert_region_mode = (alert_region_mode + 1)
            else:
                print("Second Region Set")
                alert_region_x_second.delete(0, tk.END)
                alert_region_y_second.delete(0, tk.END)
                alert_region_x_second.insert(0, str(y))
                alert_region_y_second.insert(0, str(x))
                set_alert_region = False
                alert_region_mode = 0
                save_settings()
                system_label.configure(text="✅ Positions Saved", text_color="green")
            pass

        if pressed and set_faction_region and not set_alert_region and not taking_screenshot and button == mouse.Button.middle:
            y, x = pyautogui.position()
            global faction_region_mode
            faction_region_mode = (faction_region_mode) % 2

            if faction_region_mode == 0:
                print("First Region Set.")
                faction_region_x_first.delete(0, tk.END)
                faction_region_y_first.delete(0, tk.END)
                faction_region_x_first.insert(0, str(y))
                faction_region_y_first.insert(0, str(x))
                faction_region_mode = (faction_region_mode + 1)
            else:
                print("Second Region Set")
                faction_region_x_second.delete(0, tk.END)
                faction_region_y_second.delete(0, tk.END)
                faction_region_x_second.insert(0, str(y))
                faction_region_y_second.insert(0, str(x))
                set_faction_region = False
                faction_region_mode = 0
                save_settings()
                system_label.configure(text="✅ Positions Saved", text_color="green")
            pass

        global start_x, start_y, end_x, end_y

        if pressed and taking_screenshot and not set_faction_region and not set_alert_region and button == mouse.Button.middle:
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
                system_label.configure(text="Press SHIFT to confirm")
                screenshot_mode = 0
                try:
                    display_screenshot_region(start_x, start_y, abs(end_x - start_x), abs(end_y - start_y))
                except:
                    system_label.configure(text="System: ❎ Draw Screenshot something Wrong.", text_color="red")

    # Keyboard Functions
    def on_key_release(key):
        global start_x, start_y, end_x, end_y, taking_screenshot, set_alert_region, set_faction_region
        if config_mode:
            if key == keyboard.Key.f1:
                if not set_alert_region:
                    taking_screenshot = False
                    set_faction_region = False
                    set_alert_region = True
                    system_label.configure(text="Alert Mode: ✅ Active.", text_color="yellow")
                else:
                    set_alert_region = False
            if key == keyboard.Key.f2:
                if not set_faction_region:
                    taking_screenshot = False
                    set_alert_region = False
                    set_faction_region = True
                    system_label.configure(text="Faction Mode: ✅ Active.", text_color="yellow")
                else:
                    set_faction_region = False
            if key == keyboard.Key.f3:
                if not taking_screenshot:
                    taking_screenshot = True
                    set_faction_region = False
                    set_alert_region = False
                    start_x, start_y = None, None
                    end_x, end_y = None, None
                    system_label.configure(text="Screenshot Mode: ✅ Active.", text_color="yellow")
                else:
                    taking_screenshot = False
                    if start_x is not None and start_y is not None and end_x is not None and end_y is not None:
                        try:
                            if screenshot_overlay:
                                screenshot_overlay.destroy()
                            screenshot = wincap.take_screenshot(start_x, start_y, end_x - start_x, end_y - start_y)
                            # screenshot = pyautogui.screenshot(region=(start_x, start_y, end_x - start_x, end_y - start_y))
                            if screenshot:
                                system_label.configure(text="✅ Screenshot Saved.", text_color="green")
                            else:
                                raise
                        except Exception as e:
                            print(e)
                            system_label.configure(text="Screenshot Mode: ❎ Positions wrong.", text_color="red")

    # Menu Button Section

    def save_button_clicked():
        system_label.configure(text="System: ✅ Settings Saved.", text_color="green")

        save_settings()

    def exit_button_clicked():
        if alarm.is_running:
            alarm.stop()
            system_label.configure(text="System: ❎ EVE Alert stopped.", text_color="red")
        else:
            system_label.configure(text="System: ❎ EVE Alert isn't running.", text_color="red")
        root.destroy()

    # Starten Sie den Alert-Thread, indem Sie die Alert-Funktion aus alert.py aufrufen
    def start_alert_script(system_label):
        settings = load_settings()
        if settings:
            if not alarm.is_running():
                alarm.set_system_label(system_label)
                alarm.start()

                system_label.configure(text="System: ✅ EVE Alert starting...", text_color="green")
                system_label.configure(text="System: ✅ EVE Alert has been started.", text_color="green")
            else:
                system_label.configure(text="System: ❎ EVE Alert is already running.", text_color="green")
        else:
            system_label.configure(text="System: ❎ No Settings found.", text_color="red")

    def stop_alert_script():
        if alarm.is_running():
            alarm.set_system_label(system_label)
            alarm.stop()
            system_label.configure(text="System: ❎ EVE Alert stopped.", text_color="red")
            return
        system_label.configure(text="System: ❎ EVE Alert isn't running.", text_color="red")

    # Configuration Section

    def config_mode_toggle():
        global config_mode, taking_screenshot, set_alert_region, set_faction_region
        config_mode = not config_mode
        if config_mode:
            open_description_window(root, config_mode)
            config_button.configure(fg_color="#fa0202", hover_color="#bd291e")
        else:
            open_description_window(root, config_mode)
            taking_screenshot = False
            set_alert_region = False
            set_faction_region = False
            config_button.configure(fg_color="#1f538d", hover_color="#14375e")

    def update_mode():
        selected_mode = mode_var.get()
        if selected_mode == "color" and alarm.get_vision() == True:
            alarm.set_vision()
            alarm.set_vision_faction()
        save_settings()
        empty_label_00.configure(text=selected_mode)

    def slider_event(slider_value):
        empty_label_1.configure(text=slider_value)

    customtkinter.set_appearance_mode("dark")
    customtkinter.set_default_color_theme("dark-blue")

    # Menu Settings
    root = customtkinter.CTk()
    root.title("Alert - 0.3.6")

    # Setzen Sie das Fenster-Icon
    icon_path = "img/eve.ico"  # Geben Sie den Pfad zu Ihrem Icon-Bild an
    root.iconbitmap(default=get_resource_path(icon_path))

    screensize = pyautogui.size()
    screen_width, screen_height = screensize

    if screen_width <= 1920 and screen_height <= 1080:
        # Die gewünschten Prozentsätze der Bildschirmbreite und -höhe
        window_width = 600
        window_height = 400
    elif screen_width > 2560 and screen_height > 1440:
        # Die gewünschten Prozentsätze der Bildschirmbreite und -höhe
        window_width = 600
        window_height = 400
    else:
        # Die gewünschten Prozentsätze der Bildschirmbreite und -höhe
        window_width = 800
        window_height = 600

    # Setze die Größe des Fensters
    root.geometry(f"{window_width}x{window_height}")

    #root.columnconfigure(3, weight=1)

    # 1 Row - Init
    mouse_position_label = customtkinter.CTkLabel(root, text="")
    label_x_axis = customtkinter.CTkLabel(root, text="X-Achse")
    label_y_axis = customtkinter.CTkLabel(root, text="Y-Achse")
    
    # 2 Row - Init
    # Alert Region Position 1
    alert_region_label_1 = customtkinter.CTkLabel(root, text="Alert Region Left Upper Corner:", justify='left')
    alert_region_x_first = customtkinter.CTkEntry(root)
    alert_region_y_first = customtkinter.CTkEntry(root)

    # 3 Row - Init
    # Alert Region Position 2
    alert_region_label_2 = customtkinter.CTkLabel(root, text="Alert Region Right Lower Corner:", justify='left')
    alert_region_x_second = customtkinter.CTkEntry(root)
    alert_region_y_second = customtkinter.CTkEntry(root)
    
    # 4 Row - Init
    # Alert Region Position 1
    faction_region_label_1 = customtkinter.CTkLabel(root, text="Faction Region Left Upper Corner:", justify='left')
    faction_region_x_first = customtkinter.CTkEntry(root)
    faction_region_y_first = customtkinter.CTkEntry(root)

    # 5 Row - Init
    # Alert Region Position 2
    faction_region_label_2 = customtkinter.CTkLabel(root, text="Faction Region Right Lower Corner:", justify='left')
    faction_region_x_second = customtkinter.CTkEntry(root)
    faction_region_y_second = customtkinter.CTkEntry(root)

    # Row 6 - Init
    # Slider
    slider_label = customtkinter.CTkLabel(root, text="Detection Threshold")
    detectionscale = tk.DoubleVar()
    detectionscale.set(70)  # Setzen Sie den Standardwert auf 70
    slider = customtkinter.CTkSlider(root, from_=0, to=100, orientation="horizontal", number_of_steps=100, variable=detectionscale, command=slider_event)
    mode_var = customtkinter.StringVar(value="color")

    # Row 7
    # Config / Detection Mode- Init
    config_button = customtkinter.CTkButton(root, text="Config Mode", command=config_mode_toggle)
    mode_checkbox = customtkinter.CTkCheckBox(root, text="Detection Mode", variable=mode_var, onvalue="color", offvalue="picture", command=update_mode)

    # Row 8
    # Buttons
    save_button = customtkinter.CTkButton(root, text="Save", command=save_button_clicked)
    show_alert_button = customtkinter.CTkButton(root, text="Show Alert Region", command=display_alert_region)
    exit_button = customtkinter.CTkButton(root, text="Exit", command=exit_button_clicked)

    # Row 12 
    # System Info
    system_label = customtkinter.CTkLabel(root, text="System: ")
    credit_label = customtkinter.CTkLabel(root, text="Powered by Geuthur")
    
    if settings:
        alert_region_x_first.insert(0, settings["alert_region_1"]["x"])
        alert_region_y_first.insert(0, settings["alert_region_1"]["y"])
        alert_region_x_second.insert(0, settings["alert_region_2"]["x"])
        alert_region_y_second.insert(0, settings["alert_region_2"]["y"])
        faction_region_x_first.insert(0, settings["faction_region_1"]["x"])
        faction_region_y_first.insert(0, settings["faction_region_1"]["y"])
        faction_region_x_second.insert(0, settings["faction_region_2"]["x"])
        faction_region_y_second.insert(0, settings["faction_region_2"]["y"])
        detectionscale.set(settings["detectionscale"]["value"])
        mode_var.set(settings["detection_mode"]["value"])

    empty_label_1 = customtkinter.CTkLabel(root, text=slider.get())
    empty_label_00 = customtkinter.CTkLabel(root, text=mode_var.get())

    label_x_axis.grid(row=0, column=1)
    label_y_axis.grid(row=0, column=2)

    mouse_position_label.grid(row=0, column=0)

    # Alert Region 1 Visual
    alert_region_label_1.grid(row=1, column=0, padx=20)
    alert_region_x_first.grid(row=1, column=1)
    alert_region_y_first.grid(row=1, column=2)

    # Alert Region 2 Visual
    alert_region_label_2.grid(row=2, column=0, padx=20)
    alert_region_x_second.grid(row=2, column=1)
    alert_region_y_second.grid(row=2, column=2)

    # Faction Region 1 Visual
    faction_region_label_1.grid(row=3, column=0, padx=20)
    faction_region_x_first.grid(row=3, column=1)
    faction_region_y_first.grid(row=3, column=2)

    # Faction Region 2 Visual
    faction_region_label_2.grid(row=4, column=0, padx=20)
    faction_region_x_second.grid(row=4, column=1)
    faction_region_y_second.grid(row=4, column=2)
    
    # Slider Visual
    empty_label_1.grid(row=6, column=2)

    # Slider Visual
    slider_label.grid(row=6, column=0)
    slider.grid(row=6, column=1)

    # Config Visual
    config_button.grid(row=7, column=0)
    # Erstellen Sie die Checkbox für den Moduswechsel
    mode_checkbox.grid(row=7, column=1)
    empty_label_00.grid(row=7, column=2)

    empty_label_2 = customtkinter.CTkLabel(root, text="")
    empty_label_2.grid(row=8, column=1)

    # Buttons Visual
    save_button.grid(row=9, column=0)
    show_alert_button.grid(row=9, column=1)
    exit_button.grid(row=9, column=2)

    empty_label_3 = customtkinter.CTkLabel(root, text="")
    empty_label_3.grid(row=10, column=1)

    start_button = customtkinter.CTkButton(root, text="Start Script", command=lambda: start_alert_script(system_label))
    show_faction_button = customtkinter.CTkButton(root, text="Show Faction Region", command=display_faction_region)
    stop_button = customtkinter.CTkButton(root, text="Stop Script", command=stop_alert_script)

    start_button.grid(row=11, column=0)
    show_faction_button.grid(row=11, column=1)
    stop_button.grid(row=11, column=2)

    empty_label_4 = customtkinter.CTkLabel(root, text="")
    empty_label_4.grid(row=12, column=1)

    # Platzieren Sie das system_label in der neuen Zeile, um es zu zentrieren
    system_label.grid(row=101, column=0, pady=(0, 10))  # Stellen Sie sicher, dass der Abstand nur unten (10) ist
    credit_label.grid(row=102, column=2, pady=(0, 10))  # Stellen Sie sicher, dass der Abstand nur unten (10) ist
    mouse_listener = mouse.Listener(on_click=on_click)
    mouse_listener.start()

    keyboard_listener = keyboard.Listener(on_release=on_key_release)
    keyboard_listener.start()

    update_mouse_position_label()
    
    #root.mainloop()
    root.protocol("WM_DELETE_WINDOW", on_closing)  # Registrieren Sie die on_closing-Funktion für das Schließen des Fensters
    root.mainloop()

if __name__ == '__main__':
    alarm = Alert_Agent()
        
    # Start the main_menu coroutine
    main_menu()