import asyncio
import logging
import os
import random

import cv2 as cv
import sounddevice as sd
import soundfile as sf

from evealert.managers.settingsmanager import SettingsManager
from evealert.settings.functions import get_resource_path
from evealert.tools.vision import Vision
from evealert.tools.windowscapture import WindowCapture

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
vision = Vision(image_filenames)
vision_faction = Vision(image_faction_filenames)
wincap = WindowCapture()

logger = logging.getLogger("alert")


class AlertAgent:
    """Alert Agent Class"""

    def __init__(self, main):
        self.main = main
        self.loop = asyncio.get_event_loop()
        # Main Settings
        self.running = False
        self.check = False
        self.settings = SettingsManager()

        # Locks to prevent overstacking
        self.lock = asyncio.Lock()
        self.timerlock = {}
        self.visionlock = asyncio.Lock()
        self.factionlock = asyncio.Lock()

        # Vison Settings
        self.enemy = False
        self.faction = False

        # Alarm Settings
        self.alarm_detected = False
        self.alarm_counter = {"Enemy": 0, "Faction": 0}
        self.alarm_frequency = 3

        # PyAudio-Objekt erstellen
        self.p = sd

        self.load_settings()

    def load_settings(self):
        settings = self.settings.open_settings()

        if settings:
            self.x1 = int(settings["alert_region_1"]["x"])
            self.y1 = int(settings["alert_region_1"]["y"])
            self.x2 = int(settings["alert_region_2"]["x"])
            self.y2 = int(settings["alert_region_2"]["y"])
            self.x1_faction = int(settings["faction_region_1"]["x"])
            self.y1_faction = int(settings["faction_region_1"]["y"])
            self.x2_faction = int(settings["faction_region_2"]["x"])
            self.y2_faction = int(settings["faction_region_2"]["y"])
            self.detection = int(settings["detectionscale"]["value"])
            self.detection_faction = int(settings["faction_scale"]["value"])
            self.cooldowntimer = int(settings["cooldown_timer"]["value"])

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
        vision.debug_mode = False
        vision_faction.debug_mode_faction = False

    def is_running(self):
        return self.running

    def get_vision(self):
        return vision.debug_mode

    def get_vision_faction(self):
        return vision_faction.debug_mode_faction

    def set_vision(self):
        vision.debug_mode = not vision.debug_mode

    def set_vision_faction(self):
        vision_faction.debug_mode_faction = not vision_faction.debug_mode_faction

    async def vision_check(self):
        self.load_settings()
        screenshot, _ = wincap.get_screenshot_value(self.y1, self.x1, self.x2, self.y2)
        if screenshot is not None:
            self.check = True
        else:
            self.main.write_message("Wrong Alert Settings.", "red")
            self.check = False

    async def vision_thread(self):
        async with self.visionlock:
            while True:
                screenshot, _ = wincap.get_screenshot_value(
                    self.y1, self.x1, self.x2, self.y2
                )
                if screenshot is not None:
                    enemy = vision.find(screenshot, self.detection)
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
        async with self.factionlock:
            self.faction_state = True
            while True:
                screenshot_faction, _ = wincap.get_screenshot_value(
                    self.y1_faction, self.x1_faction, self.x2_faction, self.y2_faction
                )
                if screenshot_faction is not None:
                    try:
                        faction = vision_faction.find_faction(
                            screenshot_faction, self.detection_faction
                        )
                    except Exception as e:
                        faction = None
                        logger.error(e)
                        self.main.write_message(e, "red")
                        if vision_faction.faction:
                            cv.destroyWindow("Faction Vision")
                            vision_faction.faction = False
                        await asyncio.sleep(10)

                    if faction:
                        self.faction = True
                    else:
                        self.faction = False
                await asyncio.sleep(
                    0.1
                )  # Add a small delay to prevent overstacking the CPU

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
        try:
            # Lese die Audiodaten mit soundfile
            data, samplerate = sf.read(sound, dtype="int16")

            # Spiele die Audiodaten ab
            sd.play(data, samplerate)
        except Exception as e:
            logger.error("Error playing audio: %s", e)
            self.stop()
            self.main.write_message("Something went wrong.", "red")

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
