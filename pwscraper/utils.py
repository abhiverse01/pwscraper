# utils.py : Utility functions (utils.py) to handle file I/O and logging.
# pwscraper/utils.py

import logging
import os

def setup_logging():
    if not os.path.exists("logs"):
        os.makedirs("logs")

    logging.basicConfig(
        filename="logs/activity.log",
        level=logging.INFO,
        format="%(asctime)s - %(levelname)s - %(message)s"
    )
    logging.getLogger().addHandler(logging.StreamHandler())
