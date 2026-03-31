"""
FilePath: "/Roomba-900-Local-Connect/roomba_unified_extractor.py"
Project Title: Roomba-900-Local-Connect
File Description: Unified tool to extract BLID and Password. Now pulls default IP from .env.
Author: "Michael Landbo"
Date created: 31/03/2026
Date Modified: 01/04/2026
Version: v.2.2.0
"""

import argparse
import json
import re
import socket
import sys
import os
from typing import Any, Optional
from roombapy import RoombaPassword  # type: ignore
from dotenv import load_dotenv

# Load existing .env if it exists
load_dotenv()

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

def error(msg: str) -> None:
    print(f"{Style.RED}[ERROR]{Style.RESET} {msg}")

def header(title: str) -> None:
    line = "=" * 60
    print(f"\n{Style.MAGENTA}{line}{Style.RESET}")
    print(f"{Style.BOLD}{title.center(60)}{Style.RESET}")
    print(f"{Style.MAGENTA}{line}{Style.RESET}")

def run_unified_extractor(roomba_ip: str) -> int:
    header("Roomba Unified Extractor – BLID & Password")
    info(f"Targeting Roomba at IP: {roomba_ip}")
    print("\n1. Put Roomba in the dock.")
    print("2. Hold the HOME button until the melody plays.")
    input("3. When it starts blinking: press ENTER to continue...")

    try:
        rp = RoombaPassword(roomba_ip)
        data = rp.get_password()
        if not data:
            error("No data received. Ensure the robot is in pairing mode.")
            return 1

        raw_password = str(getattr(data, "password", data))
        # Extract the clean 16-char password from format :1:BLID:PASSWORD
        clean_password = raw_password.split(":")[-1] if ":" in raw_password else raw_password
        
        # Extract BLID from data object or derive from password string
        blid = getattr(data, "blid", None) or getattr(data, "username", None)
        if not blid and ":" in raw_password:
            match = re.match(r"^:1:(\d+):", raw_password)
            if match: blid = match.group(1)

        header("EXTRACTION RESULT")
        print(f"{Style.BOLD}BLID:           {Style.RESET}{blid or 'NOT FOUND'}")
        print(f"{Style.BOLD}CLEAN PASSWORD: {Style.RESET}{clean_password}")

        print("\n" + "-" * 60)
        success("Credentials retrieved successfully.")
        print("Add these to your .env file:\n")
        print(f'ROOMBA_IP={roomba_ip}')
        print(f'ROOMBA_BLID={blid}')
        print(f'ROOMBA_PASSWORD={clean_password}')
        print("-" * 60)
        return 0
    except Exception as e:
        error(f"Critical error during extraction: {e}")
        return 1

if __name__ == "__main__":
    # Pull default IP from environment if available
    default_ip = os.getenv("ROOMBA_IP")
    
    parser = argparse.ArgumentParser(description="Extract Roomba credentials.")
    parser.add_argument(
        "--ip", "-i", 
        default=default_ip,
        help="Roomba IP address (defaults to ROOMBA_IP from .env if set)"
    )
    args = parser.parse_args()

    if not args.ip:
        error("IP address not found in .env and not provided via --ip argument.")
        sys.exit(1)
        
    sys.exit(run_unified_extractor(args.ip))
