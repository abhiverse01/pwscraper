import asyncio
from scraper import VideoScraper
from utils import setup_logging, validate_config
from storage import save_dataset

async def main():
    setup_logging()
    
    # Load and validate configuration
    config_path = "config/platforms.json"
    config = validate_config(config_path)

    # Initialize the scraper with the platform details
    scraper = VideoScraper(platforms_config=config, output_dir="datasets/raw")

    try:
        # Start the scraping process
        scraped_data = await scraper.run()

        # Deduplicate data (use VideoScraper class to call the static method)
        scraped_data = VideoScraper.deduplicate_data(scraped_data)

        # Save the data into a structured dataset
        save_dataset(scraped_data, output_file="datasets/processed/videos_dataset.csv", format="csv")
    except Exception as e:
        print(f"An error occurred: {e}")

if __name__ == "__main__":
    asyncio.run(main())
