import asyncio
import logging
import os
import random
import time
from typing import TYPE_CHECKING

import sounddevice as sd
import soundfile as sf

from evealert.settings.helper import get_resource_path
from evealert.tools.vision import Vision
from evealert.tools.windowscapture import WindowCapture

if TYPE_CHECKING:
    from evealert.menu.main import MainMenu

# Den Dateinamen des Alarmklangs angeben
IMG_FOLDER = "evealert/img"

ALARM_SOUND = get_resource_path("sound/alarm.wav")
FACTION_SOUND = get_resource_path("sound/faction.wav")

ALERT_FILES = [
    os.path.join(IMG_FOLDER, filename)
    for filename in os.listdir(IMG_FOLDER)
    if filename.startswith("image_")
]
FACTION_FILES = [
    os.path.join(IMG_FOLDER, filename)
    for filename in os.listdir(IMG_FOLDER)
    if filename.startswith("faction_")
]

logger = logging.getLogger("alert")


class AlertAgent:
    """Alert Agent Class"""

    def __init__(self, main: "MainMenu"):
        self.main = main
        self.loop = asyncio.get_event_loop()
        self.wincap = WindowCapture(self.main)
        self.alert_vision = Vision(ALERT_FILES)
        self.alert_vision_faction = Vision(FACTION_FILES)

        # Main Settings
        self.running = False
        self.check = False

        # Locks to prevent overstacking
        self.lock = asyncio.Lock()
        self.visionlock = asyncio.Lock()
        self.factionlock = asyncio.Lock()

        # Vison Settings
        self.enemy = False
        self.faction = False

        # Alarm Settings
        self.cooldown_timers = {}
        self.cooldowntimer = 60
        self.alarm_detected = False
        self.mute = False

        # Webhook Settings
        self.webhook_cooldown_timer = 0
        self.webhook_sent = False

        # Sound Settings
        self.p = sd
        self.alarm_trigger_counts = {}
        self.max_sound_triggers = 3
        self.currently_playing_sounds = {}

        self.load_settings()

    @property
    def is_running(self):
        return self.running

    @property
    def is_alarm(self):
        return self.alarm_detected

    @property
    def is_enemy(self):
        return self.enemy

    @property
    def is_faction(self):
        return self.faction

    def clean_up(self):
        self.stop()
        self.main.write_message("System: EVE Alert stopped.", "green")

    def start(self):
        self.loop.run_until_complete(self.vision_check())
        if self.check is True:

            self.vison_t = self.loop.create_task(self.vision_thread())
            self.vision_faction_t = self.loop.create_task(self.vision_faction_thread())

            # Start the Alarm
            self.alert_t = self.loop.create_task(self.run())

            self.running = True
            self.main.write_message("System: EVE Alert started.", "green")
            self.loop.run_forever()
            logger.debug("Alle Tasks wurden gestartet")
            return True
        return False

    def stop(self):
        self.loop.stop()
        self.running = False
        self.currently_playing_sounds = {}
        self.alarm_trigger_counts = {}
        self.cooldown_timers = {}
        self.alert_vision.debug_mode = False
        self.alert_vision_faction.debug_mode_faction = False
        self.main.update_alert_button()
        self.main.update_faction_button()

    def load_settings(self):
        settings = self.main.menu.setting.load_settings()

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
            self.mute = settings["server"]["mute"]
            if self.main.menu.setting.is_changed:
                vision_opened = False
                factiom_vision_opened = False
                if self.alert_vision.is_vision_open:
                    vision_opened = True
                if self.alert_vision_faction.is_faction_vision_open:
                    factiom_vision_opened = True
                # Reload the Vision
                self.alert_vision = Vision(ALERT_FILES)
                self.alert_vision_faction = Vision(FACTION_FILES)
                if vision_opened:
                    self.set_vision()
                if factiom_vision_opened:
                    self.set_vision_faction()
                self.main.write_message("Settings: Loaded.", "green")

    def set_vision(self):
        if self.is_running:
            self.alert_vision.debug_mode = not self.alert_vision.debug_mode
            self.main.update_alert_button()

    def set_vision_faction(self):
        if self.is_running:
            self.alert_vision_faction.debug_mode_faction = (
                not self.alert_vision_faction.debug_mode_faction
            )
            self.main.update_faction_button()

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
        async with self.visionlock:
            while True:
                screenshot, _ = self.wincap.get_screenshot_value(
                    self.y1, self.x1, self.x2, self.y2
                )
                if screenshot is not None:
                    enemy = self.alert_vision.find(screenshot, self.detection)
                    if enemy == "Error":
                        self.clean_up()
                    if enemy:
                        self.enemy = True
                    else:
                        self.enemy = False
                else:
                    self.main.write_message("Wrong Alert Settings.", "red")
                    self.clean_up()
                await asyncio.sleep(
                    0.1
                )  # Add a small delay to prevent overstacking the CPU

    async def vision_faction_thread(self):
        async with self.factionlock:
            self.faction_state = True
            while True:
                screenshot_faction, _ = self.wincap.get_screenshot_value(
                    self.y1_faction, self.x1_faction, self.x2_faction, self.y2_faction
                )
                if screenshot_faction is not None:
                    faction = self.alert_vision_faction.find_faction(
                        screenshot_faction, self.detection_faction
                    )

                    if faction:
                        self.faction = True
                    else:
                        self.faction = False
                await asyncio.sleep(
                    0.1
                )  # Add a small delay to prevent overstacking the CPU

    async def reset_alarm(self, alarm_type):
        if alarm_type in self.alarm_trigger_counts:
            self.alarm_trigger_counts[alarm_type] = 0
            self.cooldown_timers[alarm_type] = 0

        if self.main.webhook and alarm_type == "Enemy":
            self.webhook_sent = False
            self.main.webhook.execute(
                f"Alarm Reset: {alarm_type} alarm reset in {self.main.menu.setting.system_name.get()}!"
            )

    async def alarm_detection(self, alarm_text, sound=ALARM_SOUND, alarm_type="Enemy"):
        self.main.write_message(
            f"{alarm_text}",
            "red",
        )
        await self.play_sound(sound, alarm_type)
        await self.send_webhook_message(alarm_type)

    async def send_webhook_message(self, alarm_type):
        current_time = time.time()
        # Ensure to limit the webhook sending to once every 5 seconds
        if current_time < self.webhook_cooldown_timer:
            logger.info("Webhook is in cooldown period. Message not sent.")
            return

        if self.main.webhook and alarm_type == "Enemy" and self.webhook_sent is False:
            # Send the webhook message
            try:
                msg = f"Enemy Appears in {self.main.menu.setting.system_name.get()}!"
                self.main.webhook.execute(msg)
                self.webhook_cooldown_timer = current_time + 5
                self.webhook_sent = True

            except Exception as e:
                logger.error("Error sending webhook: %s", e)

    async def play_sound(self, sound, alarm_type):
        if self.mute:
            return

        # Initialize counter and cooldown timer if not present
        if alarm_type not in self.alarm_trigger_counts:
            self.alarm_trigger_counts[alarm_type] = 0
        if alarm_type not in self.cooldown_timers:
            self.cooldown_timers[alarm_type] = 0

        # Check cooldown timer
        current_time = time.time()
        if current_time < self.cooldown_timers[alarm_type]:
            self.main.write_message(
                f"{alarm_type} Sound is in cooldown period.", "yellow"
            )
            return

        # Increment the counter
        self.alarm_trigger_counts[alarm_type] += 1

        # Check if the alarm has been triggered three times
        if self.alarm_trigger_counts[alarm_type] > self.max_sound_triggers:
            self.cooldown_timers[alarm_type] = current_time + self.cooldowntimer
            self.alarm_trigger_counts[alarm_type] = 0
            self.main.write_message(
                f"{alarm_type} Sound is now in cooldown for {self.cooldowntimer} seconds.",
                "yellow",
            )
            return

        if alarm_type not in self.currently_playing_sounds:
            self.currently_playing_sounds[alarm_type] = True
            try:
                # Lese die Audiodaten mit soundfile
                data, samplerate = sf.read(sound, dtype="int16")

                # Spiele die Audiodaten ab
                sd.play(data, samplerate)
                await asyncio.sleep(
                    len(data) / samplerate
                )  # Wait for the sound to finish
            except Exception as e:
                if self.alarm_trigger_counts[alarm_type] <= 1:
                    self.main.open_error_window(
                        "Error Playing Sound. Check Logs for more information."
                    )
                logger.exception("Error Playing Sound: %s", e)
            finally:
                self.currently_playing_sounds.pop(alarm_type, None)

    # Run Alert Agent
    async def run(self):
        async with self.lock:
            while True:
                # Reload Settings if changed
                if self.main.menu.setting.is_changed:
                    self.load_settings()
                    self.main.menu.setting.changed = False

                # Reset Alarm Status
                self.alarm_detected = False

                try:
                    if self.faction:
                        self.alarm_detected = True
                        await self.alarm_detection(
                            "Faction Spawn!", FACTION_SOUND, "Faction"
                        )
                    if self.enemy:
                        self.alarm_detected = True
                        await self.alarm_detection(
                            "Enemy Appears!", ALARM_SOUND, "Enemy"
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
