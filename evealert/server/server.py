# server.py
import logging
import socket
import threading
import time
from datetime import datetime
from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from evealert.menu.main import MainMenu

logger = logging.getLogger("main")


class ServerAgent:
    def __init__(self, main: "MainMenu"):
        self.main = main
        self.server = None
        self.client = None
        self.running = False
        self.stop_event = threading.Event()

        # Default settings
        self.name = ""
        self.admin_password = "1234"

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
                self.main.write_message("Server stopped", "red")
                Server.log_message("Server stopped")
            if self.client:
                self.client.clean_up()
                self.client = None
            self.running = False
            # Close all active connections
            for connection in Server.connections:
                connection.close()
            Server.connections.clear()
        self._update_button()

    def _update_button(self):
        """Set the state of the server buttons."""
        if self.running:
            self.main.mainmenu_buttons.socket_server.configure(
                fg_color="#fa0202", hover_color="#bd291e", text="Stop Server"
            )
        else:
            if self.main.menu.setting.server_mode.get():
                self.main.mainmenu_buttons.socket_server.configure(
                    fg_color="#1f538d", hover_color="#14375e", text="Start Server"
                )
            else:
                self.main.mainmenu_buttons.socket_server.configure(
                    fg_color="#1f538d", hover_color="#14375e", text="Send to Server"
                )

    def start_server(self):
        """Start the server"""
        settings = self.main.menu.setting.load_settings()
        host = settings["server"]["host"]
        port = settings["server"]["port"]
        server = settings["server"]["server_mode"]

        # Set the server name and admin password
        self.admin_password = settings["server"]["admin_password"]
        self.name = settings["server"]["name"]

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
            threading.Thread(target=self.start_broadcaster_checker, daemon=True).start()

            self._update_button()
            self.main.write_message("Socket Server started successfully", "green")
        else:
            self.client = ClientAgent(self.main, settings)
            if self.client.connect():
                self.running = True
                login = self.client.login(self.admin_password)
                if login:
                    self._update_button()
                    self.main.write_message("Alerter successfully logged in!", "green")
                    Server.log_message("Alerter successfully logged in!")
                    return
                self.main.write_message("Wrong Password, Access not granted!", "red")
                Server.log_message("Wrong Password, Access not granted!")
            else:
                self.main.write_message("Client failed to connect", "red")
                Server.log_message("Client failed to connect")
            self.clean_up()

    def newconnections(self):
        while self.is_running:
            try:
                sock, address = self.server.accept()
                new_client = Server(
                    sock,
                    address,
                    Server.total_connections,
                    self.name,
                    True,
                    self.admin_password,
                    self.stop_event,
                )
                Server.add_connection(new_client)
                new_client.start()
            except OSError:
                break

    def start_broadcaster_checker(self):
        """Start the broadcaster checker."""
        if self.is_running:
            if self.server or self.client:
                threading.Thread(target=self._broadcaster, daemon=True).start()

    def _broadcaster(self):
        """Check if the broadcaster is still active."""
        while not self.stop_event.is_set():
            if Server.alerter_sent:
                time.sleep(5)
                Server.alerter_sent = False
            else:
                time.sleep(5)

    def recieve_alert(self, message: str):
        """Broadcast a message to all connected clients."""
        if self.server:
            msg = f"{self.name}: {message}"
            try:
                Server.broadcast_message(msg)
                Server.log_message(f"Server Send: {msg}")
            except OSError as e:
                if "WinError 10054" in str(e):
                    self.clean_up()
                    self.main.write_message("Connection to server lost", "red")
                    return
                Server.log_message(f"Server Send: Failed to broadcast message: {e}")
        elif self.client:
            try:
                self.client.broadcast_message(message)
            except OSError as e:
                if "WinError 10054" in str(e):
                    self.clean_up()
                    self.main.write_message("Connection to server lost", "red")
                    return
                Server.log_message(f"Server Send: Failed to broadcast message: {e}")


class Server(threading.Thread):
    connections = []
    total_connections = 0
    alerter_sent = False
    alerter_count = 0

    # pylint: disable=too-many-positional-arguments
    def __init__(
        self, st: socket.socket, address, sid, name, signal, password, stop_event
    ):
        threading.Thread.__init__(self)
        self.socket = st
        self.address = address
        self.id = sid
        self.name = name
        self.signal = signal
        self.password = password
        self.stop_event = stop_event

        # Alert
        self.alert = False

    @classmethod
    def add_alerter(cls):
        """Set alerter_sent to False every 5 seconds."""
        cls.alerter_count += 1
        Server.log_message(f"Alerter count: {cls.alerter_count}")

    @classmethod
    def add_connection(cls, client):
        """Add a connection to the list."""
        cls.connections.append(client)
        cls.total_connections += 1
        Server.log_message(
            f"New connection at ID {client.id}, {client.address} - Total: {client.total_connections}"
        )
        client.send_message(f"Connetected to {client.name} Server")

    @classmethod
    def remove_connection(cls, client):
        """Remove a connection from the list."""
        if client in cls.connections:
            cls.connections.remove(client)
            cls.total_connections -= 1
            Server.log_message(f"Client {client.address} disconnected")

    @staticmethod
    def log_message(message):
        """Log a message to the console."""
        timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        print(f"[{timestamp}] {message}")

    @classmethod
    def broadcast_message(cls, message):
        """Broadcast a message to all connected clients."""
        for client in cls.connections:
            try:
                client.socket.sendall(message.encode("utf-8"))
            except OSError as e:
                Server.log_message(f"Failed to send to {client.address}: {e}")
                client.close()
        if "Alert" in message or "Normal" in message:
            cls.alerter_sent = True

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
                data = self.socket.recv(32).decode("utf-8")
                if data:
                    self.handle_message(data)
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
            if self.password in message:
                self.socket.sendall(b"Alerter access granted!")
                self.socket.sendto(b"Alerter access granted!", self.address)
                Server.broadcast_message("Local Broadcaster has loged in!")
            elif "Alert" in message:
                Server.alerter_sent = True
                Server.broadcast_message(message)
                Server.log_message(f"Alert broadcasted by {self.address}")
            elif "Normal" in message:
                Server.alerter_sent = True
                Server.broadcast_message(message)
                Server.log_message(f"Normal broadcasted by {self.address}")
            elif "Heartbeat" in message:
                data = f"Heartbeat received from {self.address}"
                data += f"\nServer Name: {self.name}"
                data += f"\nTotal Connections: {self.total_connections}"
                data += f"\nLocal Active: {self.alerter_sent}"
                self.socket.sendto(data.encode("utf-8"), self.address)
            else:
                self.socket.sendall(b"Invalid Command")
                self.handle_disconnect()
        except OSError as e:
            print(f"Error: {e}")


class ClientAgent:
    def __init__(self, main: "MainMenu", settings):
        self.main = main

        self.port = settings.get("server", {}).get("port", 27215)
        self.host = settings.get("server", {}).get("host", "127.0.0.1")
        self.password = settings.get("server", {}).get("admin_password", "1234")
        self.server_name = settings.get("server", {}).get("name", "No Name")

        self.sock = None
        self.running = False
        self.stop_event = threading.Event()

    @property
    def is_running(self):
        """Check if the client is running."""
        return self.running

    def clean_up(self):
        """Clean up the client."""
        if self.running:
            self.stop_event.set()
            if self.sock:
                self.sock.close()
                self.sock = None
            self.running = False
            self.main.write_message("Alerter stopped", "red")
            Server.log_message("Alerter stopped")

    def connect(self):
        """Connect to the server."""
        self.sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        try:
            self.sock.connect((self.host, self.port))
            response = self.sock.recv(1024).decode("utf-8")
            if "Connetected" in response:
                self.main.write_message(response, "green")
                Server.log_message(response)
                self.running = True
                return True
            return False
        except OSError as e:
            if "WinError 10061" in str(e):
                self.main.write_message(
                    "Failed to connect to server: Connection refused", "red"
                )
            elif "WinError 10053" in str(e):
                pass
            else:
                logger.debug("Connection error: %s", e)
                self.main.write_message("Failed to connect to server, Read Logs", "red")
        except Exception as e:
            logger.exception("An unexpected error occurred: %s", e)
            self.main.write_message("An unexpected error occurred, Read Logs", "red")
        self.clean_up()
        return False

    def login(self, password):
        """Send login message to the server."""
        if self.running:
            try:
                self.sock.sendall(password.encode("utf-8"))
                response = self.sock.recv(1024).decode("utf-8")
                if "Alerter access granted!" in response:
                    return True
                return False
            except OSError as e:
                self.main.write_message(f"Failed to login: {e}", "red")
                self.clean_up()
                return False
            except Exception as e:
                print(f"An unexpected error occurred: {e}")
                self.clean_up()
                return False
        return False

    def broadcast_message(self, message):
        """Broadcast a message to the server."""
        msg = f"{self.server_name}: {message}"
        if self.running:
            try:
                self.sock.sendall(msg.encode("utf-8"))
            except OSError as e:
                self.main.write_message(f"Failed to broadcast message: {e}", "red")
                logger.exception("Failed to broadcast message: %s", e)
                self.clean_up()
            except Exception as e:
                print(f"An unexpected error occurred: {e}")
                self.clean_up()
        else:
            self.main.write_message("Alerter not running", "red")
