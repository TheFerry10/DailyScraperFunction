import datetime
import logging
from tagesschauscraper import helper, tagesschau, __version__
import azure.functions as func
import json
from azure.storage.blob import ContainerClient
import os

def main(mytimer: func.TimerRequest) -> None:
    utc_timestamp = datetime.datetime.utcnow().replace(
        tzinfo=datetime.timezone.utc).isoformat()

    if mytimer.past_due:
        logging.info('The timer is past due!')
    
    # Storage settings
    connection_string = os.environ["OUTPUTSTORAGE_CONNECTIONSTRING"]
    container_name = "tagesschau-teaser"

    # Scraping parameters
    date_ = datetime.date.today() - datetime.timedelta(days=1)
    category = 'all'
    
    # Scraping
    logging.info(f"TagesschauScraper version: {__version__}")
    logging.info(f"Initialize scraping for date {date_} and category {category}")
    tagesschauScraper = tagesschau.TagesschauScraper()
    url = tagesschau.create_url_for_news_archive(date_, category=category)
    logging.info(f"Scraping teaser from URL {url}")
    teaser = tagesschauScraper.scrape_teaser(url)
    
    # Create hierarchical file path
    dateDirectoryTreeCreator = helper.DateDirectoryTreeCreator(date_, root_dir="")
    file_path = dateDirectoryTreeCreator.create_file_path_from_date()
    file_name_and_path = os.path.join(
        file_path,
        helper.create_file_name_from_date(
            date_, extension=".json"
        ),
    )
    
    # Upload blob
    container_client = ContainerClient.from_connection_string(connection_string, container_name)
    container_client.upload_blob(file_name_and_path, json.dumps(teaser, indent=4), overwrite=True)
    
    logging.info("Scraping terminated.")
    logging.info('Python timer trigger function ran at %s', utc_timestamp)
