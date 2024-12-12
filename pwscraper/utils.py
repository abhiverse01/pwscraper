# utils.py : Utility functions (utils.py) to handle file I/O and logging.
# pwscraper/utils.py

import logging
import os
import json

def setup_logging():
    if not os.path.exists("logs"):
        os.makedirs("logs")

    logging.basicConfig(
        filename="logs/activity.log",
        level=logging.INFO,
        format="%(asctime)s - %(levelname)s - %(message)s"
    )
    logging.getLogger().addHandler(logging.StreamHandler())

def validate_config(config_path):
    if not os.path.exists(config_path):
        raise FileNotFoundError(
            f"Configuration file not found: {config_path}. "
            "Ensure the file exists and contains valid platform configurations."
        )
    with open(config_path, "r") as file:
        try:
            config = json.load(file)
            if "platforms" not in config or not isinstance(config["platforms"], list):
                raise ValueError("Invalid configuration: 'platforms' key missing or not a list.")
            return config
        except json.JSONDecodeError as e:
            raise ValueError(f"Failed to parse JSON configuration: {e}")
