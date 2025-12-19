#!/usr/bin/env python3

"""
Timestamping utils, including a beautiful datetime string function and timestamp print
"""

# built-in
from datetime import datetime
from pathlib import Path

LOG_FILE = Path("program.log")
LOG_FILE.open("w", encoding="utf-8").close()

def tsprint(message: str, log: bool = True):
    """
    Prints to terminal and logfile with datetime (e.g. "[9/18/2025 15:16:25] message here")

    Args:
    :param message: the message to print
    :type message: str
    :param log: whether to log to the log file. off by default
    :type log: bool
    """

    now = datetime.now()
    now = now.strftime("%x %X")
    output = f"[{now}] {message}"
    print(output)

    if log:
        try:
            with LOG_FILE.open("a", encoding="utf-8") as file:
                file.write(output + "\n")
        except Exception as e:
            print(f"[{now}] Failed to write to log file: {e}")
