import os, time, random, asyncio, threading
import pyaudio
import wave
from config import *
from functions import load_settings, get_resource_path
from threading import Thread, Lock
from pycolorise.colors import *
from PIL import Image
from vision import Vision
from windowscapture import WindowCapture
# ALERT SYSTEM

alarm_counter_lock = threading.Lock()
faction_counter_lock = threading.Lock()

# Den Dateinamen des Alarmklangs angeben
alarm_sound = "sound/alarm.wav"
faction_sound = "sound/faction.wav"

alarm_sound = get_resource_path(alarm_sound)
faction_sound = get_resource_path(faction_sound)

img_folder = 'img'
image_filenames = [os.path.join(img_folder, filename) for filename in os.listdir(img_folder) if filename.startswith('image_')]
image_faction_filenames = [os.path.join(img_folder, filename) for filename in os.listdir(img_folder) if filename.startswith('faction_')]
vision = Vision(image_filenames)
vision_faction = Vision(image_faction_filenames)
wincap = WindowCapture()

class Alert_Agent:

    def __init__(self):
        # Settings
        self.stopped = True
        self.enemy = False
        self.faction = False
        self.image_detected = False
        self.change = True
            
        # create a thread lock object
        self.lock = Lock()
        self.timerlock = Lock()
        self.visionlock = Lock()
        self.factionlock = Lock()
        self.running = False
        self.threads = []  # Liste zur Verfolgung aller erstellten Threads

        # Alarm Settings
        # Faction
        self.faction_counter = 0
        self.faction_queue = 0
        self.faction_alarm_played = False
        self.faction_playing_alarm = False
        self.faction_playing = Lock()
        # Alarm
        self.alarm_counter = 0
        self.alarm_queue = 0
        # 
        self.alarm_times = []
        self.alarm_frequency = 3
        self.alarm_played = False
        self.playing = Lock()
        self.alarmlock = Lock()
        self.playing_alarm = False
        self.cooldown = False

        # PyAudio-Objekt erstellen
        self.p = pyaudio.PyAudio()

        # Timer
        self.timer = 0

        # Color Detection Settings
        # neut 117,117,117
        # red 128,12,12
        self.red_tolerance = 20
        self.green_blue_tolerance = 4
        self.rgb_group = [(128,12,12)]

        # system_label wird zuerst auf None gesetzt
        self.system_label = None

    def load_settings(self):
        # Settings Menu
        if self.change:
            settings = load_settings()
            if settings:
                self.x1 = int(settings.get("alert_region_1", {}).get("x", None))
                self.y1 = int(settings.get("alert_region_1", {}).get("y", None))
                self.x2 = int(settings.get("alert_region_2", {}).get("x", None))
                self.y2 = int(settings.get("alert_region_2", {}).get("y", None))
                self.x1_faction = int(settings.get("faction_region_1", {}).get("x", None))
                self.y1_faction = int(settings.get("faction_region_1", {}).get("y", None))
                self.x2_faction = int(settings.get("faction_region_2", {}).get("x", None))
                self.y2_faction = int(settings.get("faction_region_2", {}).get("y", None))
                self.detection = settings.get("detectionscale", {}).get("value", None)
                self.mode = settings.get("detection_mode", {}).get("value", "picture")
                self.cooldowntimer = int(settings.get("timer", {}).get("value", 60))
                self.detection = self.detection / 100
                self.change = False
            else:
                self.x1 = 0
                self.y1 = 0
                self.x2 = 0
                self.y2 = 0
                self.x1_faction = 0
                self.y1_faction = 0
                self.x2_faction = 0
                self.y2_faction = 0
                self.detection = 0
                self.mode = "picture"
                self.detection = 0
                self.change = False

    def start(self):
        self.stopped = False
        self.running = True

        t1 = Thread(target=self.alarm_timer_thread)
        t1.start()
        self.threads.append(t1)

        t2 = Thread(target=self.vision_thread)
        t2.start()
        self.threads.append(t2)

        t3 = Thread(target=self.vision_faction_thread)
        t3.start()
        self.threads.append(t3)

        t4 = Thread(target=self.alarm_thread)
        t4.start()
        self.threads.append(t4)

        # Start the self.run() coroutine in a new thread
        t5 = Thread(target=self.run)
        t5.start()
        self.threads.append(t5)
    
    # If async use this
    def run_in_thread(self):
        loop = asyncio.new_event_loop()
        asyncio.set_event_loop(loop)
        loop.run_until_complete(self.run())
        loop.close()

    def stop(self):
        self.stopped = True
        self.running = False
        self.alarm_counter = 0
        self.timer = 0
        self.alarm_queue = 0
        self.faction_queue = 0
        vision.debug_mode = False
        vision_faction.debug_mode_faction = False

    def is_running(self):
        return self.running
    
    def set_settings(self):
        self.change = True

    def set_system_label(self, system_label):
        # Set System Menu Label
        self.system_label = system_label

    def set_vision(self):
        if not vision.debug_mode:
            vision.debug_mode = True
        else:
            vision.debug_mode = False

    def set_vision_faction(self):
        if not vision_faction.debug_mode_faction:
            vision_faction.debug_mode_faction = True
        else:
            vision_faction.debug_mode_faction = False

    def get_vision(self):
        return vision.debug_mode
    
    def get_vision_faction(self):
        return vision_faction.debug_mode_faction

    def vision_thread(self):
        self.visionlock.acquire()
        while not self.stopped:
            self.load_settings()
            screenshot, screenshot_data = wincap.get_screenshot_value(self.y1, self.x1, self.x2, self.y2)
            if screenshot is not None:
                if self.mode == "color":
                    # Check if the target color is in the screenshot
                    enemy = self.is_color_in_screenshot(screenshot_data.pixels, self.rgb_group[0], tolerance=10)
                    if enemy:
                        self.enemy = True
                    else:
                        self.enemy = False
                else:
                    #screenshot, screenshot_data = wincap.get_screenshot()
                    enemy = vision.find(screenshot, self.detection)
                    if enemy:
                        self.enemy = True
                    else:
                        self.enemy = False
                time.sleep(0.1)
            else:
                self.stop()
                print(Red("Wrong Alert Settings."))
                self.system_label.configure(text="System: ❎ Wrong Alert settings.")
        self.visionlock.release()

    def vision_faction_thread(self):
        self.factionlock.acquire()
        while not self.stopped:
            self.load_settings()
            screenshot_faction, screenshot_faction_data = wincap.get_screenshot_value(self.y1_faction, self.x1_faction, self.x2_faction, self.y2_faction)
            if screenshot_faction is not None:
                faction = vision_faction.find(screenshot_faction, 0.7)
                if faction:
                    self.faction = True
                else:
                    self.faction = False
            else:
                pass
            time.sleep(0.1)
        self.factionlock.release()

    # Play Alarm Sound
    #@staticmethod
    def play_alarm_sound(self, sound):
        # Funktion, um den Alarm-Sound in einem separaten Thread abzuspielen
        def play_sound():
            chunk = 1024
            wf = wave.open(sound, 'rb')
            stream = self.p.open(format=self.p.get_format_from_width(wf.getsampwidth()),
                            channels=wf.getnchannels(),
                            rate=wf.getframerate(),
                            output=True)
            data = wf.readframes(chunk)
            while data:
                stream.write(data)
                data = wf.readframes(chunk)

            wf.close()

            if self.playing_alarm:
                self.alarm_queue -= 1
                self.playing_alarm = False


        # Überprüfen Sie, ob der Sound bereits abgespielt wird
        if not self.playing_alarm:
            self.playing_alarm = True
            # Starten Sie die Sound-Wiedergabe im Hintergrund
            threading.Thread(target=play_sound).start()

    # Play Alarm Sound
    #@staticmethod
    def play_faction_sound(self, sound):
        # Funktion, um den Alarm-Sound in einem separaten Thread abzuspielen
        def play_faction_sound():
            chunk = 1024
            wf = wave.open(sound, 'rb')
            stream = self.p.open(format=self.p.get_format_from_width(wf.getsampwidth()),
                            channels=wf.getnchannels(),
                            rate=wf.getframerate(),
                            output=True)
            data = wf.readframes(chunk)
            while data:
                stream.write(data)
                data = wf.readframes(chunk)

            wf.close()

            if self.faction_playing_alarm:
                self.faction_queue -= 1
                self.faction_playing_alarm = False

        if not self.faction_playing_alarm:
            self.faction_playing_alarm = True
            # Starten Sie die Sound-Wiedergabe im Hintergrund
            threading.Thread(target=play_faction_sound).start()

    # Alarm Cooldown - Run in Background
    def alarm_timer_thread(self):
        self.timerlock.acquire()
        while not self.stopped:
            #self.play_alarm_sound(alarm_sound)
            if self.alarm_counter >= self.alarm_frequency:
                self.cooldown = True
                print(Yellow("Play sound cooldown started"))
                self.timer = time.sleep(self.cooldowntimer)  # Warten Sie 1 Minute (60 Sekunden)
                self.alarm_counter = 0  # Setzen Sie den Zähler zurück
                self.cooldown = False
            time.sleep(3)  # Warten Sie 3 Sekunden zwischen den Alarmüberprüfungen
        self.timerlock.release()

    # Alarm Cooldown - Run in Background
    def alarm_thread(self):
        self.alarmlock.acquire()
        while not self.stopped:
            if self.alarm_queue > 0:
                self.play_alarm_sound(alarm_sound)
            if self.faction_queue > 0:
                self.play_faction_sound(faction_sound)
            time.sleep(1)
        self.alarmlock.release()

    def is_color_in_screenshot(self, pixels, target_color, tolerance):
        # Check if the target color is in the screenshot pixels with tolerance
        for pixel_row in pixels:
            for pixel in pixel_row:
                # Berechnen Sie die Differenzen für jeden Farbkanal separat
                channel_diffs = [abs(c1 - c2) for c1, c2 in zip(pixel, target_color)]

                # Überprüfen Sie, ob alle Differenzen innerhalb der Toleranz liegen
                if all(isinstance(diff, (int, float)) and diff <= tolerance for diff in channel_diffs):
                    return True

        return False

    # Run Alert Agent
    def run(self):
        self.lock.acquire()
        while not self.stopped:
            self.load_settings()
            # Setzen Sie das Flag `image_detected` auf False am Anfang jeder Schleife
            self.image_detected = False
            faction_detected = False
            self.alarm_played = False
            self.faction_alarm_played = False

            try:
                if self.faction:
                    faction_detected = True
                    if self.faction_counter < self.alarm_frequency:
                        if not self.faction_alarm_played:
                            self.faction_alarm_played = True
                            with faction_counter_lock:
                                self.faction_counter += 1
                                self.faction_queue += 1
                            print(Red(f"FACTION SPAWN!!- Play Sound ({self.faction_counter}/{self.alarm_frequency})"))
                if self.enemy:
                    self.image_detected = True
                    if self.alarm_counter < self.alarm_frequency:
                        if not self.alarm_played:
                            self.alarm_played = True
                            with alarm_counter_lock:
                                self.alarm_counter += 1
                                self.alarm_queue += 1
                            print(Red(f"Enemy Detected - Play Sound ({self.alarm_counter}/{self.alarm_frequency})"))
            except Exception as e:
                print(e)
                self.stop()
                self.system_label.configure(text="System: ❎ Something went wrong.")
                return
                
            # Überprüfen, ob Faction Spawn erkannt wurde
            if not faction_detected:
                self.faction_counter = 0

            # Überprüfen, ob eines der Bilder erkannt wurde
            if not self.image_detected and self.stopped == False:
                self.alarm_counter = 0
                print(Green("No Enemy detected..."))

            # Zufällige Schlafzeit zwischen 2 und 3 Sekunden
            if self.mode == "color" and self.stopped == False:
                sleep_time = random.uniform(2, 3)
                print(Yellow(f"Next check in {sleep_time:.2f} seconds..."))
                time.sleep(sleep_time)
            else:
                if self.stopped == False:
                    sleep_time = random.uniform(1, 2)
                    print(Yellow(f"Next check in {sleep_time:.2f} seconds..."))
                    time.sleep(sleep_time)
        self.lock.release()