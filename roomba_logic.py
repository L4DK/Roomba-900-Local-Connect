"""
FilePath: "/Roomba-900-Local-Connect/roomba_logic.py"
Project Title: Roomba-900-Local-Connect
File Description: MQTT Logic engine with Keep-alive and SSL Legacy support.
Author: "Michael Landbo"
Date created: 31/03/2026
Date Modified: 01/04/2026
Version: v.1.3.1
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
        self.ip = os.getenv("ROOMBA_IP")
        self.blid = os.getenv("ROOMBA_BLID")
        self.password = os.getenv("ROOMBA_PASSWORD")
        self.client = mqtt.Client(mqtt.CallbackAPIVersion.VERSION2, client_id=self.blid)
        self.full_state = {}
        self.is_connected = False

    def _create_ssl_context(self):
        context = ssl.create_default_context()
        context.check_hostname = False
        context.verify_mode = ssl.CERT_NONE
        context.options |= 0x4  # Enable Legacy Renegotiation
        context.set_ciphers("DEFAULT@SECLEVEL=1") # Allow 1024-bit DH keys
        return context

    def on_connect(self, client, userdata, flags, rc, properties):
        if rc == 0:
            self.is_connected = True
            print(f"ENGINE: Stable connection established to {self.ip}")
            self.client.subscribe("wss")
            self.client.subscribe("state")
        else:
            print(f"CONNECTION ERROR: Code {rc}")

    def on_message(self, client, userdata, msg):
        try:
            payload = json.loads(msg.payload.decode("utf-8"))
            if "state" in payload:
                reported = payload["state"].get("reported", {})
                self.full_state.update(reported)
        except: pass

    def _keep_alive(self):
        while True:
            if self.is_connected:
                try: self.client.publish("echo", "")
                except: pass
            time.sleep(15)

    def connect(self):
        self.client.username_pw_set(self.blid, self.password)
        self.client.tls_set_context(self._create_ssl_context())
        self.client.on_connect = self.on_connect
        self.client.on_message = self.on_message
        self.client.connect(self.ip, 8883, 60)
        self.client.loop_start()
        Thread(target=self._keep_alive, daemon=True).start()

    def send_command(self, command):
        payload = {"command": command, "time": int(time.time()), "initiator": "localApp"}
        self.client.publish("cmd", json.dumps(payload))
