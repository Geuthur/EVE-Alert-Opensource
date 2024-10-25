import asyncio
import logging
import os
import random

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

        # Color Detection Settings
        # neut 117,117,117
        # red 128,12,12
        self.red_tolerance = 20
        self.green_blue_tolerance = 4
        self.rgb_group = [(128, 12, 12)]

    def load_settings(self):
        settings = self.settings.load_settings()
        if settings:
            self.x1 = settings["x1"]
            self.y1 = settings["y1"]
            self.x2 = settings["x2"]
            self.y2 = settings["y2"]
            self.x1_faction = settings["x1_faction"]
            self.y1_faction = settings["y1_faction"]
            self.x2_faction = settings["x2_faction"]
            self.y2_faction = settings["y2_faction"]
            self.detection = settings["detection"]
            self.mode = settings["mode"]
            self.cooldowntimer = settings["cooldowntimer"]

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

    def set_settings(self):
        self.load_settings()

    def get_vision(self):
        return vision.debug_mode

    def get_vision_faction(self):
        return vision_faction.debug_mode_faction

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
                screenshot, screenshot_data = wincap.get_screenshot_value(
                    self.y1, self.x1, self.x2, self.y2
                )
                if screenshot is not None:
                    if self.mode == "color":
                        # Check if the target color is in the screenshot
                        enemy = self.is_color_in_screenshot(
                            screenshot_data.pixels, self.rgb_group[0], tolerance=10
                        )
                        if enemy:
                            self.enemy = True
                        else:
                            self.enemy = False
                    else:
                        # screenshot, screenshot_data = wincap.get_screenshot()
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
            while True:
                screenshot_faction, _ = wincap.get_screenshot_value(
                    self.y1_faction, self.x1_faction, self.x2_faction, self.y2_faction
                )
                if screenshot_faction is not None:
                    faction = vision_faction.find(screenshot_faction, 0.7)
                    if faction == "Error":
                        break
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

    def is_color_in_screenshot(self, pixels, target_color, tolerance):
        # Check if the target color is in the screenshot pixels with tolerance
        for pixel_row in pixels:
            for pixel in pixel_row:
                # Berechnen Sie die Differenzen für jeden Farbkanal separat
                channel_diffs = [abs(c1 - c2) for c1, c2 in zip(pixel, target_color)]

                # Überprüfen Sie, ob alle Differenzen innerhalb der Toleranz liegen
                if all(
                    isinstance(diff, (int, float)) and diff <= tolerance
                    for diff in channel_diffs
                ):
                    return True

        return False

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
            sd.wait()
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
