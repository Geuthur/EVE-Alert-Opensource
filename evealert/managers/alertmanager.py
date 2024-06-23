import asyncio
import logging
import os
import random
import wave

import numpy as np
import pyaudio

from evealert.managers.settingsmanager import SettingsManager
from evealert.settings.functions import get_resource_path
from evealert.tools.vision import Vision

# Den Dateinamen des Alarmklangs angeben
ALERT_SOUND = "sound/alarm.wav"
FACTION_SOUND = "sound/faction.wav"
IMG_FOLDER = "evealert/img"

alarm_sound = get_resource_path(ALERT_SOUND)
faction_sound = get_resource_path(FACTION_SOUND)

image_filenames = [
    os.path.join(IMG_FOLDER, filename)
    for filename in os.listdir(IMG_FOLDER)
    if filename.startswith("image_")
]
image_faction_filenames = [
    os.path.join(IMG_FOLDER, filename)
    for filename in os.listdir(IMG_FOLDER)
    if filename.startswith("faction_")
]

# vision = Vision(image_filenames)
# vision_faction = Vision(image_faction_filenames)

logger = logging.getLogger("alert")


class AlertAgent:
    """Alert Agent Class"""

    def __init__(self, main):
        self.main = main
        self.loop = asyncio.get_event_loop()
        # Main Settings
        self.running = False
        self.check = False
        self.wincap = self.main.wincap
        self.settings = SettingsManager(self.main)

        # Locks to prevent overstacking
        self.lock = asyncio.Lock()
        self.timerlock = {}
        self.visionlock = asyncio.Lock()
        self.factionlock = asyncio.Lock()

        # Vison Settings
        self.enemy = False
        self.faction = False
        self.vision_settings = {}

        # Alarm Settings
        self.alarm_detected = False
        self.alarm_counter = {"Enemy": 0, "Faction": 0}
        self.alarm_frequency = 3

        # PyAudio-Objekt erstellen
        self.p = pyaudio.PyAudio()

        # Color Detection Settings
        # neut 117,117,117
        # red 128,12,12
        self.red_tolerance = 20
        self.green_blue_tolerance = 4
        self.rgb_group = [(128, 12, 12)]

    def create_vision(self, image, name):
        vision = Vision(image, name)
        return vision

    def load_settings(self):
        settings = self.settings.load_settings()
        if settings:
            self.alert_regions = settings.get("alarm_locations", [])
            self.x1 = self.alert_regions[0].get("vision_1", {}).get("x1")
            self.y1 = self.alert_regions[0].get("vision_1", {}).get("y1")
            self.x2 = self.alert_regions[0].get("vision_1", {}).get("x2")
            self.y2 = self.alert_regions[0].get("vision_1", {}).get("y2")
            self.x1_faction = settings.get("faction_region_1", {}).get("x")
            self.y1_faction = settings.get("faction_region_1", {}).get("y")
            self.x2_faction = settings.get("faction_region_2", {}).get("x")
            self.y2_faction = settings.get("faction_region_2", {}).get("y")
            self.detection = settings.get("detectionscale", {}).get("value")
            self.mode = settings.get("detection_mode", {}).get("value")
            self.cooldowntimer = settings.get("cooldown_timer", {}).get("value")

    def start(self):
        self.loop.run_until_complete(self.vision_check())
        if self.check is True:

            self.vison_t = self.loop.create_task(self.vision_thread())
            self.alarm_timer_t = self.loop.create_task(self.init_alarm_cooldowns())
            self.vision_faction_t = self.loop.create_task(self.vision_faction_thread())

            # Start the Alarm
            self.alert_t = self.loop.create_task(self.run())

            self.running = True
            self.main.write_message("System: EVE Alert started.", "green")
            self.loop.run_forever()
            logger.info("Alle Tasks wurden gestartet")
            return True
        return False

    def stop(self):
        self.loop.stop()
        self.running = False
        self.alarm_counter = {"Enemy": 0, "Faction": 0}
        self.vision_settings = {}

    def is_running(self):
        return self.running

    def set_settings(self):
        self.load_settings()

    def get_vision(self, vision_name):
        return self.vision_settings.get(vision_name, False)

    def set_vision(self, vision_name):
        current_value = self.vision_settings.get(vision_name, False)
        self.vision_settings[vision_name] = not current_value

    def check_vision(self, instance, screenshot, detection, name):
        # Check if the "enemy" vision setting is enabled
        vision_check = self.vision_settings.get(name)

        enemy = instance.find(screenshot, vision_check, detection)
        return enemy

    async def vision_check(self):
        self.load_settings()
        screenshot, _ = self.wincap.get_screenshot_value(
            self.y1, self.x1, self.x2, self.y2
        )
        if screenshot is not None:
            self.check = True
        else:
            self.main.write_message("Wrong Alert Settings.", "red")
            self.check = False

    async def vision_thread(self):
        self.alarm_vision = self.create_vision(image_filenames, "Alert")
        async with self.visionlock:
            while True:
                screenshot, screenshot_data = self.wincap.get_screenshot_value(
                    self.y1, self.x1, self.x2, self.y2
                )
                if screenshot is not None:
                    if self.mode == "color":
                        # Check if the target color is in the screenshot
                        enemy = await self.is_color_in_screenshot(
                            screenshot_data.pixels, self.rgb_group[0], tolerance=10
                        )
                        if enemy:
                            self.enemy = True
                        else:
                            self.enemy = False
                        await asyncio.sleep(1)  # Add a small delay
                    else:
                        enemy = self.check_vision(
                            self.alarm_vision, screenshot, self.detection, "Alert"
                        )
                        # enemy = self.alarm_vision.find(screenshot, vision_check, self.detection)
                        if enemy == "Error":
                            break
                        if enemy:
                            self.enemy = True
                        else:
                            self.enemy = False
                else:
                    self.main.write_message("Wrong Alert Settings.", "red")
                    break
                await asyncio.sleep(0.1)  # Add a small delay

    async def vision_faction_thread(self):
        self.faction_vision = self.create_vision(image_faction_filenames, "Faction")
        async with self.factionlock:
            while True:
                screenshot_faction, _ = self.wincap.get_screenshot_value(
                    self.y1_faction, self.x1_faction, self.x2_faction, self.y2_faction
                )
                if screenshot_faction is not None:
                    faction = self.check_vision(
                        self.faction_vision, screenshot_faction, 0.7, "Faction"
                    )
                    # faction = self.faction_vision.find(screenshot_faction, 0.7)
                    if faction == "Error":
                        break
                    if faction:
                        self.faction = True
                    else:
                        self.faction = False
                await asyncio.sleep(
                    0.1
                )  # Warten Sie 3 Sekunden zwischen den Alarmüberprüfungen

    # Alarm Cooldown - Run in Background
    async def alarm_timer_check(self, alarm_type):
        async with self.timerlock[alarm_type]:
            while True:
                if self.alarm_counter[alarm_type] >= self.alarm_frequency:
                    self.main.write_message(f"{alarm_type} cooldown started.")
                    await asyncio.sleep(int(self.cooldowntimer))
                    self.alarm_counter[alarm_type] = 0
                    self.main.write_message(f"{alarm_type} cooldown stopped.")
                await asyncio.sleep(0.1)

    async def init_alarm_cooldowns(self):
        for alarm_type in self.alarm_counter:
            self.timerlock[alarm_type] = asyncio.Lock()
            asyncio.ensure_future(self.alarm_timer_check(alarm_type))

    async def reset_alarm(self, alarm_type):
        if self.alarm_counter.get(alarm_type, 0) > 0:
            self.main.write_message(f"No {alarm_type} found, cooldown reseted.")
        self.alarm_counter[alarm_type] = 0
        if alarm_type in self.timerlock and self.timerlock[alarm_type].locked():
            self.timerlock[alarm_type].release()

    async def is_color_in_screenshot(self, pixels, target_color, tolerance):
        # Konvertieren Sie pixels in ein NumPy-Array für effiziente Berechnungen
        pixels_array = np.array(pixels)

        # Berechnen Sie die absolute Differenz zwischen den Pixeln und der Ziel-Farbe
        diffs = np.abs(pixels_array - target_color)

        # Überprüfen Sie, ob die maximale Differenz in jedem Pixel innerhalb der Toleranz liegt
        matches = np.all(diffs <= tolerance, axis=-1)

        # Überprüfen Sie, ob irgendein Pixel die Bedingung erfüllt
        return np.any(matches)

    async def alarm_detection(self, alarm_text, sound=alarm_sound, alarm_type="Enemy"):
        if self.alarm_counter.get(alarm_type, 0) >= self.alarm_frequency:
            return
        self.alarm_counter[alarm_type] = self.alarm_counter.get(alarm_type, 0) + 1

        self.main.write_message(
            f"{alarm_text} - Play Sound ({self.alarm_counter[alarm_type]}/{self.alarm_frequency}).",
            "red",
        )
        await self.play_sound(sound, alarm_type)

    async def play_sound(self, sound, alarm_type="enemy"):
        if self.alarm_counter.get(alarm_type, 0) <= 3:
            asyncio.ensure_future(self._play_sound(sound))

    async def _play_sound(self, sound):
        chunk = 1024
        wf = wave.open(sound, "rb")
        try:
            stream = self.p.open(
                format=self.p.get_format_from_width(wf.getsampwidth()),
                channels=wf.getnchannels(),
                rate=wf.getframerate(),
                output=True,
            )
        except OSError as e:
            logger.error("Error opening audio stream: %s", e)
            self.stop()
            self.main.write_message("Something went wrong.", "red")
            wf.close()
            return

        data = wf.readframes(chunk)
        while data:
            stream.write(data)
            data = wf.readframes(chunk)

        wf.close()

    # Run Alert Agent
    async def run(self):
        async with self.lock:
            while True:
                # Reset Alarm Status
                self.alarm_detected = False

                try:
                    if self.faction:
                        self.alarm_detected = True
                        await self.alarm_detection(
                            "Faction Spawn!", faction_sound, "Faction"
                        )
                    if self.enemy:
                        self.alarm_detected = True
                        await self.alarm_detection(
                            "Enemy Appears!", alarm_sound, "Enemy"
                        )
                except ValueError as e:
                    logger.error("Alert System Error: %s", e)
                    self.stop()
                    self.main.write_message("Something went wrong.", "red")
                    return

                # Überprüfen, ob eines der Bilder erkannt wurde
                if not self.faction:
                    await self.reset_alarm("Faction")
                if not self.enemy:
                    await self.reset_alarm("Enemy")

                sleep_time = random.uniform(2, 3)
                self.main.write_message(
                    f"Next check in {sleep_time:.2f} seconds...",
                )
                await asyncio.sleep(sleep_time)
