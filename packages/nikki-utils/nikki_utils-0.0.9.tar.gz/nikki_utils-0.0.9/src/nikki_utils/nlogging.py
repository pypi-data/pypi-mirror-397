#!/usr/bin/env python3

"""
Timestamping utils, including a beautiful datetime string function and timestamp print
"""

# built-in
from datetime import datetime
from pathlib import Path

LOG_FILE = Path("program.log")
LOG_FILE.open("w", encoding="utf-8").close()

DO_LOGGING = False

def tsprint(message: str):
    """
    Prints with datetime (e.g. "[9/18/2025 15:16:25] message here")

    Args:
    - `message` (str): the message to print
    - `log` (bool): whether to log to the log file. on by default
    """

    now = datetime.now()
    now = now.strftime("%x %X")
    output = f"[{now}] {message}"
    print(output)

    if DO_LOGGING:
        try:
            with LOG_FILE.open("a", encoding="utf-8") as file:
                file.write(output + "\n")
        except Exception as e:
            print(f"[{now}] Failed to write to log file: {e}")
