import socket
import threading
import time


class SocketClient:
    def __init__(self, host="127.0.0.1", port=27215):
        self.host = host
        self.port = port
        self.sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        self.is_admin = False
        self.running = False
        self.signal_thread = None
        self.receive_thread = None

    def connect(self):
        try:
            self.sock.connect((self.host, self.port))
            self.running = True
            return True
        # pylint: disable=bare-except
        except Exception:
            print("Connection failed")
            return False

    def login(self, is_admin=False):
        self.is_admin = is_admin
        if self.is_admin:
            self.sock.send(b"test123")
            self._start_signal_thread()
        else:
            self.sock.send(b"")

        response = self.sock.recv(32).decode("utf-8")
        if response:
            print("Connected to server.. Recieving messages")
            self._start_receive_thread()
        else:
            print("Something went wrong..")

    def _send_periodic_signal(self):
        while self.running and self.is_admin:
            try:
                self.sock.send(b"Alert")
                time.sleep(5)
                self.sock.send(b"Normal")
                time.sleep(5)
            # pylint: disable=bare-except
            except Exception:
                break

    def _receive_messages(self):
        while self.running:
            try:
                data = self.sock.recv(32)
                if data:
                    message = data.decode("utf-8")
                    if message == "Normal":
                        print("No Enemy Detected")
                    elif message == "Alert":
                        print("Enemy Detected")
                    else:
                        print(f"{message}")
            # pylint: disable=bare-except
            except Exception:
                print("Disconnected from server")
                break

    def _start_signal_thread(self):
        self.signal_thread = threading.Thread(target=self._send_periodic_signal)
        self.signal_thread.daemon = True
        self.signal_thread.start()

    def _start_receive_thread(self):
        self.receive_thread = threading.Thread(target=self._receive_messages)
        self.receive_thread.daemon = True
        self.receive_thread.start()

    def send_message(self, message):
        if self.running:
            try:
                self.sock.send(message.encode("utf-8"))
            # pylint: disable=bare-except
            except Exception:
                print("Failed to send message")

    def close(self):
        # First stop the running flag
        self.running = False

        # Send disconnect message
        self.sock.send(b"Disconnect")

        # Finally close socket
        self.sock.close()


def main():
    client = SocketClient()
    if client.connect():
        is_admin = input("Connect as admin? (y/n): ").lower() == "y"
        client.login(is_admin)

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
