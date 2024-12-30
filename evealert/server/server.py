# server.py
import socket
import threading
from datetime import datetime
from typing import TYPE_CHECKING

ADMIN_PASSWORD = "test123"

if TYPE_CHECKING:
    from evealert.menu.main import MainMenu


class ServerAgent:
    def __init__(self, main: "MainMenu"):
        self.main = main
        self.server = None
        self.client = None
        self.running = False
        self.stop_event = threading.Event()

    @property
    def is_running(self):
        """Check if the server is running."""
        return self.running

    def clean_up(self):
        """Clean up the server."""
        if self.is_running:
            self.stop_event.set()
            if self.server:
                self.server.close()
                self.server = None
            if self.client:
                self.client.close()
                self.client = None
            self.running = False
            # Close all active connections
            for connection in Server.connections:
                connection.close()
            self.main.write_message("Server stopped", "red")
            Server.log_message("Server stopped")
            Server.connections.clear()
        self.main.mainmenu_buttons.socket_server.configure(
            fg_color="#1f538d", hover_color="#14375e"
        )

    def start_server(self):
        """Start the server"""
        settings = self.main.menu.setting.load_settings()
        host = settings["server"]["host"]
        port = settings["server"]["port"]
        admin_password = settings["server"]["admin_password"]
        server = settings["server"]["server_mode"]

        if server:
            self.server = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
            self.server.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
            self.server.bind((host, port))
            self.server.listen(5)
            self.stop_event.clear()
            self.running = True

            self.main.write_message("Socket Server started", "green")
            Server.log_message("Server started")

            # Starte den Thread, der Verbindungen akzeptiert
            threading.Thread(target=self.newconnections, daemon=True).start()

            self.main.write_message("Socket Server started successfully", "green")
        else:
            self.client = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
            try:
                self.client.connect((host, port))
                self.client.sendall(admin_password.encode("utf-8"))
                response = self.client.recv(1024).decode("utf-8")
                if response == "Alerter access granted!":
                    self.running = True
                    # Server.log_message("Connected to server as alerter.")
                    self.main.write_message("Connected to server as alerter", "green")
                    return
                # Server.log_message("Failed to authenticate with server.")
                self.main.write_message("Failed to authenticate with server", "red")
            except OSError as e:
                if "WinError 10061" in str(e):
                    # Server.log_message("Failed to connect to server: Connection refused")
                    self.main.write_message(
                        "Failed to connect to server: Connection refused", "red"
                    )
                else:
                    # Server.log_message(f"Connection error: {e}")
                    self.main.write_message(f"Connection error: {e}", "red")
            self.clean_up()

    def newconnections(self):
        while self.is_running:
            try:
                sock, address = self.server.accept()
                new_client = Server(
                    sock,
                    address,
                    Server.total_connections,
                    "Name",
                    True,
                    self.stop_event,
                )
                Server.add_connection(new_client)
                new_client.start()
            except OSError:
                break

    def broadcast_message(self, message: str):
        """Broadcast a message to all connected clients."""
        if self.server:
            try:
                for connection in Server.connections:
                    connection.send_message(message)
                Server.log_message(f"Server Broadcast: {message}")
            except OSError as e:
                Server.log_message(
                    f"Server Broadcast: Failed to broadcast message: {e}"
                )
        elif self.client:
            try:
                self.send_message_to_server(message)
            except OSError as e:
                if "WinError 10054" in str(e):
                    self.clean_up()
                    self.main.write_message("Connection to server lost", "red")
                    return
                Server.log_message(f"Server Send: Failed to broadcast message: {e}")

    def send_message_to_server(self, message: str):
        """Send a message to the server."""
        self.client.sendall(message.encode("utf-8"))


class Server(threading.Thread):
    connections = []
    total_connections = 0

    # pylint: disable=too-many-positional-arguments
    def __init__(self, st: socket.socket, address, sid, name, signal, stop_event):
        threading.Thread.__init__(self)
        self.socket = st
        self.address = address
        self.id = sid
        self.name = name
        self.signal = signal
        self.stop_event = stop_event

        # Alerter
        self.is_admin = False
        self.alerter_count = 0

        # Alert
        self.alert = False

    @classmethod
    def add_connection(cls, client):
        cls.connections.append(client)
        cls.total_connections += 1
        Server.log_message(
            f"New connection at ID {client.id}, {client.address} - Admin: {client.is_admin} - Total: {client.total_connections}"
        )

    @classmethod
    def remove_connection(cls, client):
        if client in cls.connections:
            cls.connections.remove(client)
            cls.total_connections -= 1
            Server.log_message(f"Client {client.address} disconnected")

    @staticmethod
    def log_message(message):
        timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        print(f"[{timestamp}] {message}")

    @classmethod
    def broadcast_message(cls, message):
        for client in cls.connections:
            try:
                client.socket.sendall(message.encode("utf-8"))
            except OSError as e:
                Server.log_message(f"Failed to send to {client.address}: {e}")
                client.close()

    def handle_disconnect(self):
        self.signal = False
        Server.remove_connection(self)

    def send_message(self, message):
        """Send a message to the client."""
        try:
            self.socket.sendall(message.encode("utf-8"))
        except OSError:
            self.close()

    def close(self):
        """Close the client connection."""
        self.signal = False
        self.socket.close()

    def run(self):
        while self.signal and not self.stop_event.is_set():
            try:
                data = self.socket.recv(32)
                if data:
                    self.handle_message(data.decode("utf-8"))
            except OSError:
                self.handle_disconnect()
            except Exception as e:
                # self.handle_disconnect()
                print(f"An unexpected error occurred: {e}")
        self.close()

    def handle_message(self, message: str):
        """Handle the message received from the client."""
        try:
            Server.log_message(f"Received from {self.address}: {message}")
            if message == ADMIN_PASSWORD:
                self.socket.sendall(b"Alerter access granted!")
                self.is_admin = True
                Server.broadcast_message("Alerter has loged in!")
            elif message == "Alert":
                Server.broadcast_message("Alert")
                Server.log_message(f"Alert broadcasted by {self.address}")
            elif message == "Normal":
                Server.broadcast_message("Normal")
                Server.log_message(f"Normal broadcasted by {self.address}")
        except OSError as e:
            print(f"Error: {e}")
