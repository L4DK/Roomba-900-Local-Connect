"""
FilePath: "/Roomba-900-Local-Connect/roomba_unified_extractor.py"
Project Title: Roomba-900-Local-Connect
File Description: Unified tool to extract BLID and Password via pairing, 
                 derive BLID from password, and use UDP fallback.
Author: "Michael Landbo"
Date created: 31/03/2026
Date Modified: 01/04/2026
Version: v.2.1.0
"""

import argparse
import json
import re
import socket
import sys
from typing import Any, Optional
from roombapy import RoombaPassword  # type: ignore

class Style:
    RESET = "\033[0m"
    BOLD = "\033[1m"
    RED = "\033[31m"
    GREEN = "\033[32m"
    YELLOW = "\033[33m"
    CYAN = "\033[36m"
    MAGENTA = "\033[35m"

def info(msg: str) -> None:
    print(f"{Style.CYAN}[INFO]{Style.RESET} {msg}")

def success(msg: str) -> None:
    print(f"{Style.GREEN}[OK]{Style.RESET}   {msg}")

def warn(msg: str) -> None:
    print(f"{Style.YELLOW}[WARN]{Style.RESET} {msg}")

def error(msg: str) -> None:
    print(f"{Style.RED}[ERROR]{Style.RESET} {msg}")

def header(title: str) -> None:
    line = "=" * 60
    print(f"\n{Style.MAGENTA}{line}{Style.RESET}")
    print(f"{Style.BOLD}{title.center(60)}{Style.RESET}")
    print(f"{Style.MAGENTA}{line}{Style.RESET}")

def extract_blid_unified(data: Any, robot_ip: str) -> Optional[str]:
    # 1) Direct attributes
    blid = getattr(data, "blid", None) or getattr(data, "username", None)
    if blid: return str(blid).strip()

    # 2) Derive from password structure (:1:BLID:PW)
    raw_pw = getattr(data, "password", None)
    if raw_pw:
        pw_str = raw_pw.decode("utf-8") if isinstance(raw_pw, (bytes, bytearray)) else str(raw_pw)
        match = re.match(r"^:1:(\d+):", pw_str)
        if match: return match.group(1)

    # 3) UDP fallback
    return udp_discovery_fallback(robot_ip)

def udp_discovery_fallback(ip: str) -> Optional[str]:
    sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
    sock.settimeout(3.0)
    try:
        sock.sendto(b'irobot_discovery', (ip, 5678))
        data, _ = sock.recvfrom(2048)
        return json.loads(data.decode()).get("hostname", "").replace("Roomba-", "").replace("bb-", "").strip()
    except: return None
    finally: sock.close()

def run_unified_extractor(roomba_ip: str) -> int:
    header("L4DK Unified Extractor – BLID & Password")
    info(f"Connecting to Roomba at IP: {roomba_ip}")
    print("\n1. Hold the HOME button until the melody plays...")
    input("2. When it starts blinking: press ENTER to continue...")

    try:
        rp = RoombaPassword(roomba_ip)
        data = rp.get_password()
        if not data:
            error("No data received. Check IP, network, and pairing mode.")
            return 1

        raw_password = str(getattr(data, "password", data))
        clean_password = raw_password.split(":")[-1] if ":" in raw_password else raw_password
        blid = extract_blid_unified(data, roomba_ip)

        header("EXTRACTION RESULT")
        print(f"{Style.BOLD}BLID:           {Style.RESET}{blid or 'NOT FOUND'}")
        print(f"{Style.BOLD}RAW PASSWORD:   {Style.RESET}{raw_password}")
        print(f"{Style.BOLD}CLEAN PASSWORD: {Style.RESET}{clean_password}")

        print("\n" + "-" * 60)
        success("Extraction successful.")
        print("Update your .env file with these values:\n")
        print(f'  ROOMBA_BLID="{blid}"')
        print(f'  ROOMBA_PASSWORD="{clean_password}"')
        print("-" * 60)
        return 0
    except Exception as e:
        error(f"Critical error: {e}")
        return 1

if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument("--ip", "-i", default="192.168.1.17")
    args = parser.parse_args()
    sys.exit(run_unified_extractor(args.ip))
