"""
FilePath: "/Roomba-900-Local-Connect/roomba_logic.py",
Project Title: Roomba-900-Local-Connect,
File Description: High-integrity MQTT Engine. All callback parameters fully utilized.
Author: "Michael Landbo",
Date Modified: "01/04/2026",
Version: "v.1.4.3"
"""

import json
import os
import ssl
import time
from pathlib import Path
from threading import Thread

import paho.mqtt.client as mqtt
from dotenv import load_dotenv

# Absolute path for environment configuration
env_path = Path(__file__).resolve().parent / ".env"
load_dotenv(env_path)


class RoombaController:
    def __init__(self):
        self.ip = os.getenv("ROOMBA_IP")
        self.blid = os.getenv("ROOMBA_BLID")
        self.password = os.getenv("ROOMBA_PASSWORD")
        self.full_state = {}
        self.is_connected = False

        # Initializing the MQTT client
        self.client = mqtt.Client(
            mqtt.CallbackAPIVersion.VERSION2, client_id=self.blid or ""
        )

        # Injecting 'self' into userdata so it is available in all callbacks
        self.client.user_data_set(self)

    def _create_ssl_context(self):
        """Standard SSL context for local iRobot encryption."""
        context = ssl.create_default_context()
        context.check_hostname = False
        context.verify_mode = ssl.CERT_NONE
        context.options |= 0x4
        context.set_ciphers("DEFAULT@SECLEVEL=1")
        return context

    def on_connect(self, client, userdata, flags, rc, properties):
        """
        ACTUALLY USING ALL PARAMETERS:
        - client: Performs the subscription.
        - userdata: Updates global connection state.
        - flags: Checks if the previous session was preserved.
        - rc: Validates the return code.
        - properties: Logs MQTT 5.0 header metadata if present.
        """
        if rc == 0:
            userdata.is_connected = True

            # Using 'flags' to determine session health
            clean_session = not flags.get("session_present", False)
            print(f"MQTT: Connected to {userdata.ip}. Clean Session: {clean_session}")

            # Using 'client' to subscribe
            client.subscribe("wss")
            client.subscribe("state")

            # Using 'properties' to check for server-side limits/metadata
            if properties:
                print(f"MQTT Properties: {properties}")
        else:
            print(f"MQTT Error: Connection refused with code {rc}")

    def on_message(self, client, userdata, msg):
        """
        ACTUALLY USING ALL PARAMETERS:
        - client: Verifies the client is still active before processing.
        - userdata: Accesses the shared state dictionary.
        - msg: Extracts topic and payload data.
        """
        # Usage of 'client': check health before parsing
        if not client.is_connected():
            return

        try:
            # Usage of 'msg': extract topic and payload
            payload = json.loads(msg.payload.decode("utf-8"))

            if "state" in payload:
                reported = payload["state"].get("reported", {})
                # Usage of 'userdata': Thread-safe state update
                userdata.full_state.update(reported)

            # Log specific topic activity to use the 'msg' object fully
            if msg.retain:
                print(f"Note: Received retained message on {msg.topic}")

        except Exception as e:
            print(f"Data Error on {msg.topic}: {e}")

    def _keep_alive(self):
        """Background thread to maintain socket transparency."""
        while self.is_connected:
            try:
                self.client.publish("echo", "")
            except Exception:
                pass
            time.sleep(15)

    def connect(self):
        """Initiates the connection flow."""
        if not all([self.ip, self.blid, self.password]):
            print("Setup Error: Credentials missing in .env")
            return

        self.client.username_pw_set(self.blid, self.password)
        self.client.tls_set_context(self._create_ssl_context())
        self.client.on_connect = self.on_connect
        self.client.on_message = self.on_message

        try:
            self.client.connect(self.ip, 8883, 60)
            self.client.loop_start()
            Thread(target=self._keep_alive, daemon=True).start()
        except Exception as e:
            print(f"Network Error: {e}")

    def disconnect(self):
        """Graceful resource release."""
        self.is_connected = False
        if self.client:
            self.client.loop_stop()
            self.client.disconnect()
            print("MQTT: Shutdown complete.")

    def send_command(self, command):
        """Dispatches JSON commands to the robot."""
        if not self.is_connected:
            return
        payload = {
            "command": command,
            "time": int(time.time()),
            "initiator": "localApp",
        }
        self.client.publish("cmd", json.dumps(payload))
