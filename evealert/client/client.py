import socket
import threading
import time
from collections import deque

import sounddevice as sd
import soundfile as sf

from evealert.settings.helper import get_resource_path

ALARM_SOUND = get_resource_path("sound/alarm.wav")


class SocketClient:
    def __init__(self, host="127.0.0.1", port=27215):
        self.host = host
        self.port = port
        self.sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        self.is_admin = False
        self.running = False
        self.message_buffer = deque()

        # Alert Cooldown
        self.alert_cooldown = False
        self.alert_counter = 0

    def connect(self):
        try:
            self.sock.connect((self.host, self.port))
            self.running = True
            return True
        # pylint: disable=bare-except
        except Exception:
            print("Connection failed")
            return False

    def login(self):
        self.sock.send(b"")
        response = self.sock.recv(32).decode("utf-8")
        if response:
            print("Connected to server.. Receiving messages")
            self._start_receive_thread()
            self._start_process_thread()
        else:
            print("Something went wrong..")

    def _receive_messages(self):
        while self.running:
            try:
                data = self.sock.recv(32)
                if data:
                    message = data.decode("utf-8")
                    self.message_buffer.append(message)
            except Exception:
                print("Disconnected from server")
                break

    def _process_messages(self):
        last_message_time = time.time()
        while self.running:
            message_sent = False
            time.sleep(1)
            if self.message_buffer:
                messages = list(self.message_buffer)
                self.message_buffer.clear()
                if "Alert" in messages:
                    print("Enemy Detected")
                    self.play_alert_sound()
                elif "Normal" in messages:
                    print("No Enemy Detected")
                else:
                    for message in messages:
                        print(f"{message}")
                message_sent = True
            # Check if no messages are received
            if not message_sent and time.time() - last_message_time > 5:
                print("No Messages Received. Maybe no Alerter is active.")
                last_message_time = time.time()
            elif message_sent:
                last_message_time = time.time()

    def alert_cooldown_timer(self):
        while True:
            if self.alert_counter >= 5:
                print("Alert Cooldown Acctive (10s)")
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

    def _start_receive_thread(self):
        self.receive_thread = threading.Thread(target=self._receive_messages)
        self.receive_thread.daemon = True
        self.receive_thread.start()

    def _start_process_thread(self):
        self.process_thread = threading.Thread(target=self._process_messages)
        self.process_thread.daemon = True
        self.process_thread.start()

    def send_message(self, message):
        if self.running:
            try:
                self.sock.send(message.encode("utf-8"))
            # pylint: disable=bare-except
            except Exception:
                print("Failed to send message")

    def close(self):
        self.running = False
        self.sock.send(b"Disconnect")
        self.sock.close()


def main():
    client = SocketClient()
    if client.connect():
        client.login()
        try:
            while True:
                message = input("")
                if message.lower() == "quit":
                    break
                client.send_message(message)
        except KeyboardInterrupt:
            print("\nShutting down...")
        except Exception as e:
            print(f"Error: {e}")
        finally:
            client.close()


if __name__ == "__main__":
    main()
