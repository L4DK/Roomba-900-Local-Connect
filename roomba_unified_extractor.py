"""
FilePath: "/Roomba-900-Local-Connect/roomba_unified_extractor.py",
Project Title: Roomba-900-Local-Connect,
File Description: High-integrity extraction tool with UDP fallback and regex parsing.
Author: "Michael Landbo",
Date Modified: "01/04/2026",
Version: "v.2.2.5"
"""

import argparse
import json
import os
import re
import socket
import sys
from pathlib import Path
from typing import Any, Optional

from dotenv import load_dotenv
from roombapy import RoombaPassword  # type: ignore

# Use absolute path to ensure the tool can read/write to the correct .env location
env_path = Path(__file__).resolve().parent / ".env"
load_dotenv(env_path)


class Style:
    """Terminal styling for professional CLI feedback."""

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


def udp_discovery_fallback(robot_ip: str) -> Optional[str]:
    """
    ACTUAL USAGE of 'socket' and 'json':
    Attempts to find the BLID via UDP discovery if the pairing payload is incomplete.
    """
    discovery_msg = b"irobot_discovery"
    # Create a UDP socket
    sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
    sock.settimeout(3.0)

    try:
        sock.sendto(discovery_msg, (robot_ip, 5678))
        data, _ = sock.recvfrom(2048)
        # Parse the UDP response using json
        decoded_data = json.loads(data.decode("utf-8"))
        hostname = decoded_data.get("hostname", "")
        # Clean hostname to get the BLID (e.g., 'Roomba-12345' -> '12345')
        return hostname.replace("Roomba-", "").replace("bb-", "").strip()
    except Exception:
        return None
    finally:
        sock.close()


def extract_credentials(data: Any, robot_ip: str) -> tuple[Optional[str], str]:
    """
    ACTUAL USAGE of 're':
    Parses the raw pairing data to extract the 16-char password and the BLID.
    """
    raw_pw = str(getattr(data, "password", data))

    # Extract the clean password (the part after the last colon)
    clean_pw = raw_pw.split(":")[-1] if ":" in raw_pw else raw_pw

    # Extract BLID from attributes or use regex on the raw password string
    blid = getattr(data, "blid", None) or getattr(data, "username", None)

    if not blid:
        # Regex usage: Find the digits between the first two colons in :1:BLID:PW
        match = re.search(r":1:(\d+):", raw_pw)
        blid = match.group(1) if match else udp_discovery_fallback(robot_ip)

    return str(blid) if blid else None, clean_pw


def run_unified_extractor(target_ip: str) -> int:
    """The main execution logic for the extraction process."""
    header("Roomba Unified Extractor – Local Credentials")
    info(f"Targeting Roomba at: {target_ip}")

    print("\n1. Place your Roomba in the charging dock.")
    print("2. Hold the HOME button until it plays a specific melody.")
    input("3. Once the Wi-Fi light is blinking, press ENTER here...")

    try:
        # Use roombapy to initiate the pairing handshake
        rp = RoombaPassword(target_ip)
        pairing_data = rp.get_password()

        if not pairing_data:
            error("No data received. Please check pairing mode and IP address.")
            return 1

        blid, password = extract_credentials(pairing_data, target_ip)

        header("EXTRACTION SUCCESSFUL")
        print(f"{Style.BOLD}ROOMBA_IP={Style.RESET}{target_ip}")
        print(f"{Style.BOLD}ROOMBA_BLID={Style.RESET}{blid or 'NOT_FOUND'}")
        print(f"{Style.BOLD}ROOMBA_PASSWORD={Style.RESET}{password}")

        print("\n" + "-" * 60)
        success("Process complete. Update your .env file with the values above.")
        print("-" * 60)
        return 0

    except Exception as e:
        error(f"Critical error during extraction: {e}")
        return 1


def main(argv: list[str]) -> None:
    """
    ACTUAL USAGE of 'argparse', 'os', and 'sys':
    Configures CLI and handles the process exit.
    """
    # Use os.getenv to pull default from .env if it exists
    default_ip = os.getenv("ROOMBA_IP", "192.168.1.17")

    parser = argparse.ArgumentParser(description="Extract Roomba Local Credentials.")
    parser.add_argument(
        "--ip",
        "-i",
        default=default_ip,
        help=f"IP address of the Roomba (Default: {default_ip})",
    )

    # Parse the arguments from the provided argv list
    args = parser.parse_args(argv)

    # Execute and exit with the correct status code
    exit_status = run_unified_extractor(args.ip)
    sys.exit(exit_status)


if __name__ == "__main__":
    # Pass sys.argv[1:] to the main function to utilize the sys module fully
    main(sys.argv[1:])
