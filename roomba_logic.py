"""
FilePath: "/Roomba-900-Local-Connect/roomba_logic.py"
Project Title: Roomba-900-Local-Connect
File Description: MQTT Logic engine. All configuration is loaded from environment variables.
Author: "Michael Landbo"
Date created: 31/03/2026
Date Modified: 01/04/2026
Version: v.1.3.2
"""

import json
import os
import ssl
import time
from threading import Thread
import paho.mqtt.client as mqtt
from dotenv import load_dotenv

load_dotenv()

class RoombaController:
    def __init__(self):
        # All parameters are now pulled from the .env file
        self.ip = os.getenv("ROOMBA_IP")
        self.blid = os.getenv("ROOMBA_BLID")
        self.password = os.getenv("ROOMBA_PASSWORD")
        self.full_state = {}
        self.is_connected = False
        
        # Initialize MQTT client only if BLID is available
        if self.blid:
            self.client = mqtt.Client(mqtt.CallbackAPIVersion.VERSION2, client_id=self.blid)

    def _create_ssl_context(self):
        context = ssl.create_default_context()
        context.check_hostname = False
        context.verify_mode = ssl.CERT_NONE
        context.options |= 0x4  # Legacy Renegotiation fix
        context.set_ciphers("DEFAULT@SECLEVEL=1") # 1024-bit key fix
        return context

    def on_connect(self, client, userdata, flags, rc, properties):
        if rc == 0:
            self.is_connected = True
            print(f"SUCCESS: Connected to Roomba at {self.ip}")
            self.client.subscribe("wss")
            self.client.subscribe("state")
        else:
            print(f"CONNECTION FAILED: Unauthorized or network error (Code {rc})")

    def on_message(self, client, userdata, msg):
        try:
            payload = json.loads(msg.payload.decode("utf-8"))
            if "state" in payload:
                self.full_state.update(payload["state"].get("reported", {}))
        except: pass

    def connect(self):
        if not all([self.ip, self.blid, self.password]):
            print("ERROR: Missing configuration in .env file (IP, BLID, or PASSWORD).")
            return

        self.client.username_pw_set(self.blid, self.password)
        self.client.tls_set_context(self._create_ssl_context())
        self.client.on_connect = self.on_connect
        self.client.on_message = self.on_message
        
        try:
            self.client.connect(self.ip, 8883, 60)
            self.client.loop_start()
            # Heartbeat thread to keep connection alive
            Thread(target=self._keep_alive, daemon=True).start()
        except Exception as e:
            print(f"CRITICAL ERROR: Could not initiate connection: {e}")

    def _keep_alive(self):
        while True:
            if self.is_connected:
                try: self.client.publish("echo", "")
                except: pass
            time.sleep(15)

    def send_command(self, command):
        if not self.is_connected: return
        payload = {"command": command, "time": int(time.time()), "initiator": "localApp"}
        self.client.publish("cmd", json.dumps(payload))
