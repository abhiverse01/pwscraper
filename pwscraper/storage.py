# storage.py : Storage module (storage.py) to save the scraped data.
# pwscraper/storage.py

import pandas as pd
import os
import logging

logger = logging.getLogger(__name__)

def save_dataset(data, output_file: str, format: str = "csv"):
    if not os.path.exists(os.path.dirname(output_file)):
        os.makedirs(os.path.dirname(output_file))

    if not isinstance(data, list) or not all(isinstance(item, dict) for item in data):
        logger.error("Invalid data format. Expected a list of dictionaries.")
        raise ValueError("Invalid data format.")

    df = pd.DataFrame(data)

    try:
        if format == "csv":
            df.to_csv(output_file, index=False)
        elif format == "json":
            df.to_json(output_file, orient="records", indent=4)
        elif format == "parquet":
            df.to_parquet(output_file, index=False)
        else:
            raise ValueError(f"Unsupported format: {format}")

        logger.info(f"Dataset saved to {output_file}")
    except Exception as e:
        logger.error(f"Failed to save dataset: {e}")
        raise
