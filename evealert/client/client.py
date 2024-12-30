import socket
import threading
import time
from collections import deque
from typing import TYPE_CHECKING

import sounddevice as sd
import soundfile as sf

from evealert.client.logger import setup_logger
from evealert.settings.helper import get_resource_path

ALARM_SOUND = get_resource_path("sound/alarm.wav")

if TYPE_CHECKING:
    from evealert.client.listener import MainMenu

log_main = setup_logger("main")


class SocketClient:
    def __init__(self, main: "MainMenu", host="127.0.0.1", port=27215):
        self.main = main
        self.host = host
        self.port = port
        self.sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        self.is_admin = False
        self.running = False
        self.message_buffer = deque()

        # Threads
        self.receive_thread = None
        self.process_thread = None

        # Alert Cooldown
        self.alert_cooldown = False
        self.alert_counter = 0

    @property
    def is_running(self):
        return self.running

    def clean_up(self):
        if self.sock:
            self.sock.close()
            self.sock = None
        self.running = False
        self.message_buffer.clear()
        self.alert_cooldown = False
        self.alert_counter = 0
        self.switch_state()

    def connect(self):
        try:
            self.sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
            self.sock.connect((self.host, self.port))
            self.running = True
            return True
        # pylint: disable=bare-except
        except Exception:
            self.main.write_message("Connection failed", "red")
            log_main.debug("Connection failed")
            return False

    def heartbeat(self):
        try:
            self.sock.send(b"Send Heartbeat")
            self._start_receive_thread()
            self._start_process_thread()
        except Exception as e:
            self.main.write_message("Failed to send heartbeat. Read Logs", "red")
            log_main.info("Failed to send heartbeat: %s", e)

    def send_message(self, message):
        if self.running:
            try:
                self.sock.send(message.encode("utf-8"))
            # pylint: disable=bare-except
            except Exception as e:
                self.main.write_message("Failed to send message", "red")
                log_main.info("Failed to send message: %s", e)

    def switch_state(self):
        if not self.running:
            self.main.connect_button.configure(
                state="normal", fg_color="#1f538d", hover_color="#14375e"
            )
            self.main.disconnect_button.configure(
                state="disabled", fg_color="#fa0202", hover_color="#bd291e"
            )
        else:
            self.main.connect_button.configure(
                state="disabled", fg_color="#fa0202", hover_color="#bd291e"
            )
            self.main.disconnect_button.configure(
                state="normal", fg_color="#1f538d", hover_color="#14375e"
            )

    def _start_receive_thread(self):
        self.receive_thread = threading.Thread(target=self._receive_messages)
        self.receive_thread.daemon = True
        self.receive_thread.start()

    def _start_process_thread(self):
        self.process_thread = threading.Thread(target=self._process_messages)
        self.process_thread.daemon = True
        self.process_thread.start()

    def _receive_messages(self):

        while self.running:
            try:
                if self.sock:
                    data = self.sock.recv(32)
                    if data:
                        message = data.decode("utf-8")
                        self.message_buffer.append(message)
                else:
                    print("Socket is not valid")
                    break
            except ConnectionResetError:
                log_main.debug("Connection was reset by server")
                self.main.write_message("Connection was reset by server", "red")
                self.clean_up()
                self._retry_connection()
                break
            except ConnectionAbortedError:
                log_main.debug("Connection was aborted by Client")
                self.main.write_message("Connection was aborted by Client", "red")
                self.clean_up()
                break
            except Exception as e:
                log_main.info("An unexpected error occurred: %s", e)
                self.main.write_message(
                    "An unexpected error occurred. Read Logs", "red"
                )
                self.clean_up()
                break

    def _retry_connection(self):
        for attempt in range(3):
            self.main.write_message(
                f"Attempting to reconnect... ({attempt + 1}/3)", "normal"
            )
            if self.connect():
                self.heartbeat()
                self.switch_state()
                self.main.write_message("Reconnected successfully", "green")
                return
            time.sleep(5)
        self.main.write_message("Failed to reconnect after 3 attempts", "red")

    def _process_messages(self):
        last_message_time = time.time()
        while self.running:
            message_sent = False
            time.sleep(1)
            if self.message_buffer:
                messages = list(self.message_buffer)
                self.message_buffer.clear()
                if "Alert" in messages:
                    self.main.write_message("Enemy Detected", "red")
                    self.play_alert_sound()
                elif "Normal" in messages:
                    self.main.write_message("No Enemy Detected", "green")
                else:
                    for message in messages:
                        self.main.write_message(f"{message}")
                message_sent = True
            # Check if no messages are received
            if not message_sent and time.time() - last_message_time > 5:
                self.main.write_message(
                    "No Messages Received. Maybe no Alerter is active.", "red"
                )
                last_message_time = time.time()
            elif message_sent:
                last_message_time = time.time()

    def alert_cooldown_timer(self):
        while True:
            if self.alert_counter >= 5:
                self.main.write_message("Alert Cooldown Acctive (10s)", "normal")
                self.alert_cooldown = True
                time.sleep(10)
                self.alert_cooldown = False
                self.alert_counter = 0
                break

    def play_alert_sound(self):
        """Play alert sound."""
        try:
            if self.alert_cooldown:
                return
            if self.alert_counter >= 5:
                threading.Thread(target=self.alert_cooldown_timer).start()
                return
            # Lese die Audiodaten mit soundfile
            data, samplerate = sf.read(ALARM_SOUND, dtype="int16")

            # Spiele die Audiodaten ab
            sd.play(data, samplerate)
            self.alert_counter += 1
        except Exception as e:
            print(f"Error: {e}")
