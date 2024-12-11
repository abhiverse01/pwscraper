# storage.py : Storage module (storage.py) to save the scraped data.
# pwscraper/storage.py

import pandas as pd
import os

def save_dataset(data, output_file):
    if not os.path.exists(os.path.dirname(output_file)):
        os.makedirs(os.path.dirname(output_file))

    if not isinstance(data, list) or not all(isinstance(item, dict) for item in data):
        raise ValueError("Invalid data format. Expected a list of dictionaries.")

    df = pd.DataFrame(data)
    df.to_csv(output_file, index=False)
    print(f"Dataset saved to {output_file}")