# server.py
import socket
import threading
import time
from datetime import datetime

ADMIN_PASSWORD = "test123"


class Server(threading.Thread):
    connections = []
    total_connections = 0
    has_active_admin = False
    check_thread = None

    # pylint: disable=too-many-positional-arguments
    def __init__(self, st, address, sid, name, signal):
        threading.Thread.__init__(self)
        self.socket = st
        self.address = address
        self.id = sid
        self.name = name
        self.signal = signal

        # Alerter
        self.is_admin = False
        self.alerter_count = 0

        # Alert
        self.alert = False

    @staticmethod
    def log_message(message):
        timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        print(f"[{timestamp}] {message}")

    @classmethod
    def add_connection(cls, client):
        cls.connections.append(client)
        cls.total_connections += 1

    @classmethod
    def remove_connection(cls, client):
        if client in cls.connections:
            cls.connections.remove(client)
            Server.log_message(f"Client {client.address} disconnected")

    def handle_disconnect(self):
        self.signal = False
        Server.remove_connection(self)
        if self.is_admin:
            Server.has_active_admin = False
            self._check_admin_status()

    @classmethod
    def start_admin_check(cls):
        if cls.check_thread is None:
            cls.check_thread = threading.Thread(target=cls._check_admin_status)
            cls.check_thread.daemon = True
            cls.check_thread.start()

    @classmethod
    def _check_admin_status(cls):
        while True:
            if len(cls.connections) > 0:  # Only check if clients exist
                admin_count = sum(1 for client in cls.connections if client.is_admin)
                if admin_count == 0:
                    cls.has_active_admin = False
                    cls._broadcast_no_alerter_all()
            time.sleep(30)

    @classmethod
    def _broadcast_no_alerter_all(cls):
        cls.log_message("Broadcasting No Alerter Active to all clients")
        for client in cls.connections:
            if not client.is_admin:
                client.socket.sendall(b"No Alerter Active")

    def check_alerter_status(self):
        """Check if there's an active alerter and notify this client if not"""
        admin_count = sum(1 for client in self.connections if client.is_admin)
        if admin_count == 0 and not self.is_admin:
            self.socket.send(b"No Alerter Active")

    # pylint: disable=too-many-nested-blocks
    def run(self):
        try:
            initial_data = self.socket.recv(32).decode("utf-8")
            if initial_data.strip() == ADMIN_PASSWORD:
                self.is_admin = True
                Server.has_active_admin = True
                self.socket.send(b"Alerter access granted!")
                Server.log_message(f"Client {self.address} authenticated as Alerter")
            else:
                Server.log_message(f"Client {self.address} connected as listener user")
                Server.start_admin_check()
        # pylint: disable=bare-except
        except Exception:
            self.signal = False
            Server.remove_connection(self)
            return

        # Main message handling loop
        # pylint: disable=too-many-nested-blocks
        while self.signal:
            try:
                data = self.socket.recv(32)
                if not data:
                    break

                message = data.decode("utf-8")
                Server.log_message(f"Received from {self.address}: {message}")

                if self.is_admin:
                    if message == "Disconnect":
                        self.handle_disconnect()
                        break
                    if message in ["Alert", "Normal"]:
                        self.alert = message == "Alert"
                        # Forward message to all non-admin clients
                        for client in Server.connections:
                            if not client.is_admin:
                                client.socket.send(message.encode("utf-8"))
            # pylint: disable=bare-except
            except Exception:
                break

        # Cleanup on disconnect
        self.signal = False
        if self in self.connections:
            self.connections.remove(self)
            Server.log_message(
                f"ID:{self.id} - Client(Admin:{self.is_admin}) {self.address} disconnected"
            )


def newconnections(sc: socket.socket):
    while True:
        sock, address = sc.accept()
        new_client = Server(sock, address, Server.total_connections, "Name", True)
        Server.add_connection(new_client)
        if not new_client.is_admin:
            new_client.check_alerter_status()
        new_client.start()
        Server.log_message(f"New connection at ID {new_client.id}, {address}")


def main():
    host = "127.0.0.1"
    port = 27215
    sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    sock.bind((host, port))
    sock.listen(5)

    Server.log_message(f"Server started on {host}:{port}")
    Server.log_message("Waiting for connections...")

    newconnectionsthread = threading.Thread(target=newconnections, args=(sock,))
    newconnectionsthread.daemon = True
    newconnectionsthread.start()

    try:
        while True:
            command = input("")
            if command == "quit":
                break
    except KeyboardInterrupt:
        Server.log_message("\nServer shutting down...")
    finally:
        sock.close()


if __name__ == "__main__":
    main()
