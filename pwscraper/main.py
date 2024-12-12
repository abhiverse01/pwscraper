# PWscraper/main.py

import asyncio # `asyncio` is a library to write concurrent code using the async/await syntax.
from scraper import VideoScraper # Import the VideoScraper class from the scraper module.
from utils import setup_logging, validate_config # Import the setup_logging and validate_config functions from the utils module.
from storage import save_dataset # Import the save_dataset function from the storage module.
import logging # The `logging` module defines functions and classes which implement a flexible event logging system for applications and libraries.

logger = logging.getLogger(__name__) # Create a logger instance for the main module.


async def main(): # Define the main coroutine function.
    setup_logging() # Call the setup_logging function to configure logging.
    logger.info("Starting the scraping process.") # Log an informational message for the start of the scraping process.

    config_path = "config/platforms.json" # Path to the configuration file.

    try: 
        config = validate_config(config_path) # Load and validate the configuration file.
    except ValueError as e:
        logger.error(f"Invalid configuration: {e}")
    except Exception as e:
        logger.error(f'Configuration Validation failed: {e}')


    scraper = VideoScraper(platforms_config=config, output_dir="datasets/raw") # Create an instance of the VideoScraper class.

    try: 
        scraped_data = await scraper.run() # Scrape data from all platforms.
        if not scraped_data:
            logger.warning("No data scraped. Exiting without Scrape")
            return
        
        scraper = VideoScraper.deduplicate_data(scraped_data) # Deduplicate the scraped data.
        save_dataset(scraped_data, output_file="datasets/processed/videos_dataset.csv", format="csv") # Save the processed data to a CSV file.



    except Exception as e:
        logger.critical(f'An Unhandled error occurred during scraping, {e}', exc_info=True)
    finally:
        logger.info("Scraping process completed.") # Log an informational message for the completion of the scraping process.


if __name__ == "__main__":
    asyncio.run(main()) # Run the main coroutine function using asyncio.
