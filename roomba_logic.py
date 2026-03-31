"""
FilePath: "/Roomba-900-Local-Connect/roomba_logic.py"
Project Title: Roomba-900-Local-Connect
File Description: MQTT Logic engine. Fixed .env loading with absolute paths.
Author: "Michael Landbo"
Date Modified: 01/04/2026
Version: v.1.3.6
"""

import json
import os
import ssl
import time
from pathlib import Path
from threading import Thread
import paho.mqtt.client as mqtt
from dotenv import load_dotenv

# Absolute path fix: Ensures .env is found regardless of where main.py is run from
env_path = Path(__file__).resolve().parent / ".env"
load_dotenv(env_path)

class RoombaController:
    def __init__(self):
        # Load variables after load_dotenv has pointed to the correct path
        self.ip = os.getenv("ROOMBA_IP")
        self.blid = os.getenv("ROOMBA_BLID")
        self.password = os.getenv("ROOMBA_PASSWORD")
        self.full_state = {}
        self.is_connected = False
        
        # Always initialize the MQTT client
        self.client = mqtt.Client(
            mqtt.CallbackAPIVersion.VERSION2, 
            client_id=self.blid or ""
        )

    def _create_ssl_context(self):
        """Prepares the SSL context for legacy Roomba hardware."""
        context = ssl.create_default_context()
        context.check_hostname = False
        context.verify_mode = ssl.CERT_NONE
        context.options |= 0x4  # OP_LEGACY_SERVER_CONNECT
        context.set_ciphers("DEFAULT@SECLEVEL=1")
        return context

    def on_connect(self, client, userdata, flags, rc, properties):
        if rc == 0:
            self.is_connected = True
            print(f"SUCCESS: Connected to Roomba at {self.ip}")
            self.client.subscribe("wss")
            self.client.subscribe("state")
        else:
            print(f"CONNECTION ERROR: Unauthorized or invalid credentials (Code {rc})")

    def on_message(self, client, userdata, msg):
        try:
            payload = json.loads(msg.payload.decode("utf-8"))
            if "state" in payload:
                reported = payload["state"].get("reported", {})
                self.full_state.update(reported)
        except Exception:
            pass

    def _keep_alive(self):
        """Maintains the MQTT connection."""
        while True:
            if self.is_connected:
                try:
                    self.client.publish("echo", "")
                except Exception:
                    pass
            time.sleep(15)

    def connect(self):
        if not all([self.ip, self.blid, self.password]):
            print(f"ERROR: .env variables missing. IP: {self.ip}, BLID: {self.blid}")
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
            print(f"CRITICAL: Connection failed: {e}")

    def send_command(self, command):
        if not self.is_connected:
            return
        payload = {"command": command, "time": int(time.time()), "initiator": "localApp"}
        self.client.publish("cmd", json.dumps(payload))
