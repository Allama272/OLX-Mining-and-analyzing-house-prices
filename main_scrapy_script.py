from bs4 import BeautifulSoup
import requests
import pandas as pd
import numpy as np
import re
from datetime import date, timedelta
from cleaner_script import dfCleaner
import logging
import os
from typing import List, Dict, Union
from dataclasses import dataclass


# Configure logging
def setup_logger(log_file: str = 'weeklyLogger.log') -> logging.Logger:
    """Configure and return a logger with both file and console handlers."""
    logger = logging.getLogger(__name__)
    logger.setLevel(logging.INFO)

    # Create formatters and handlers
    formatter = logging.Formatter(
        "%(levelname)s:%(asctime)s:%(name)s:%(message)s",
        datefmt="%Y-%m-%dT%H:%M:%S%z"
    )

    # File handler
    file_handler = logging.FileHandler(log_file)
    file_handler.setLevel(logging.INFO)
    file_handler.setFormatter(formatter)

    # Console handler
    console_handler = logging.StreamHandler()
    console_handler.setLevel(logging.INFO)
    console_handler.setFormatter(formatter)

    # Add handlers
    logger.addHandler(file_handler)
    logger.addHandler(console_handler)

    return logger


@dataclass
class PropertyListing:
    """Data class to store property listing information."""
    id: str
    price: str
    bedrooms: str
    bathrooms: str
    area: str
    location: str
    date_posted: str


def convert_time_to_days(time_str: str) -> int:
    """Convert time string (e.g., '2 days', '1 week') to number of days."""
    match = re.search(r"(\d+) (\w+)", time_str)
    if not match:
        return 0

    amount, unit = match.groups()
    amount = int(amount)

    time_units = {
        'day': 1,
        'days': 1,
        'week': 7,
        'weeks': 7,
        'month': 30,
        'months': 30,
        'year': 365,
        'years': 365
    }

    return amount * time_units.get(unit, 0)


def get_date_from_ago(ago: str) -> date:
    """Convert 'X time ago' string to actual date."""
    days = convert_time_to_days(ago)
    return date.today() - timedelta(days=days)


def scrape_property_listing(content) -> PropertyListing:
    """Extract property information from a single listing."""
    try:
        href_tag = str(content.find('a', href=True))
        id_match = re.search(r"ID(\d+).html", href_tag)
        if not id_match:
            raise ValueError("Could not find property ID")
        property_data = PropertyListing(
            id=id_match.group(1),
            price=content.find('div', attrs={'aria-label': 'Price'}).find('span').text,
            bedrooms=content.find('span', attrs={'aria-label': 'Beds'}).find('span', class_='').text,
            bathrooms=content.find('span', attrs={'aria-label': 'Bathrooms'}).find('span', class_='').text,
            area=content.find('span', attrs={'aria-label': 'Area'}).find('span', class_='').text,
            location=content.find('span', attrs={'aria-label': 'Location'}).text,
            date_posted=content.find('span', attrs={'aria-label': 'Creation date'}).text
        )
        return property_data
    except Exception as e:
        logger.error(f"Error scraping listing: {str(e)}")
        print(e)
        return None


def scrape_properties(base_url: str, max_pages: int = 199) -> List[PropertyListing]:
    """Scrape property listings from multiple pages."""
    properties = []
    session = requests.Session()

    for page in range(1, max_pages + 1):
        try:
            print(f"Scraping page {page} of {max_pages}")
            response = session.get(base_url.format(page))
            response.raise_for_status()

            soup = BeautifulSoup(response.content, "html.parser")
            listings = soup.find_all('li', attrs={'aria-label': 'Listing'})
            for listing in listings:
                property_data = scrape_property_listing(listing)
                if property_data:
                    properties.append(property_data)

        except requests.RequestException as e:
            logger.error(f"Error fetching page {page}: {str(e)}")
            continue

    return properties


def create_dataframe(properties: List[PropertyListing]) -> pd.DataFrame:
    """Convert property listings to a pandas DataFrame."""
    data = {
        'Price': [],
        'Bedrooms': [],
        'Bathrooms': [],
        'Area': [],
        'Location': [],
        'date': [],
        'id': []
    }

    for prop in properties:
        data['Price'].append(prop.price)
        data['Bedrooms'].append(prop.bedrooms)
        data['Bathrooms'].append(prop.bathrooms)
        data['Area'].append(prop.area)
        data['Location'].append(prop.location)
        data['date'].append(get_date_from_ago(prop.date_posted))
        data['id'].append(prop.id)

    return pd.DataFrame(data)


def save_dataframe(df: pd.DataFrame, category: str) -> str:
    """Save DataFrame to CSV file."""
    current_date = date.today().strftime("%m-%d-%y")
    filename = f"{category}_Data({current_date})"
    filepath = f"Data/{category} Data/{filename}.csv"

    os.makedirs(os.path.dirname(filepath), exist_ok=True)
    df.to_csv(filepath, index=False)
    logger.info(f"Saved {filename}.csv")

    return filepath


def main():
    """Main function to orchestrate the scraping process."""
    base_url = 'https://www.dubizzle.com.eg/en/properties/apartments-duplex-for-sale/alexandria/?page={}'

    try:
        # Scrape properties
        properties = scrape_properties(base_url)
        if not properties:
            raise ValueError("No properties were scraped")

        # Create and save initial DataFrame
        df = create_dataframe(properties)
        initial_filepath = save_dataframe(df, "initial")

        # Clean and save cleaned DataFrame
        df_cleaned = dfCleaner(initial_filepath)
        #save_dataframe(df_cleaned, "clean")
        print(df_cleaned.head())
        logger.info("Scraping process completed successfully")

    except Exception as e:
        logger.critical(f"Critical error in main process: {str(e)}", exc_info=True)
        raise


if __name__ == "__main__":
    logger = setup_logger()
    main()