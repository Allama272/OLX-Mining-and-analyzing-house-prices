from bs4 import BeautifulSoup
import requests
import pandas as pd
import numpy as np
import re
from datetime import date, timedelta
from cleaner_script import dfCleaner
import logging
import os
from urllib.request import Request, urlopen


logging.basicConfig(
    format="%(asctime)s %(message)s",
    datefmt="%Y-%m-%dT%H:%M:%S%z",level=logging.DEBUG
)

logger = logging.getLogger(__name__)
logger.setLevel(logging.INFO)

formatter = logging.Formatter("%(levelname)s:%(asctime)s:%(name)s:%(message)s",datefmt="%Y-%m-%dT%H:%M:%S%z")

file_handler = logging.FileHandler('weeklyLogger.log')
file_handler.setLevel(logging.INFO)
file_handler.setFormatter(formatter)

logger.addHandler(file_handler)


def days_ago_finder(str_ago):
    split = re.search(r"(\d+) (\w+)", str_ago).groups()
    days = split[0]
    days = int(days)
    date_type = split[1]
    if date_type == "days" or date_type == "day":
        days *= 1
    elif date_type == "weeks" or date_type == "week":
        days *= 7
    elif date_type == "months" or date_type == "month":
        days *= 30
    elif date_type == "years" or date_type == "year":
        # hopefully never
        days *= 365

    else:
        # in case of seconds, minutes, or hours
        days *= 0
    return days


def date_converter(ago):
    n = days_ago_finder(ago)
    new_date = date.today() - timedelta(days=n)
    return new_date


def main():
    # There is 199 page you can access, almost all of them are posted from 1 day ago to 5 months ago "10/18/2022"
    list_price = []
    list_bedroom = []
    list_bathroom = []
    list_area = []
    list_location = []
    list_id = []
    list_date_posted_string = []
    # Only apartments in alexandria
    url = 'https://www.dubizzle.com.eg/en/properties/apartments-duplex-for-sale/alexandria/?page={}'
    for i in range(1, 200):
        page_url = requests.get(url.format(i))
        soup = BeautifulSoup(page_url.content, "html.parser")
        content = soup.find_all(class_="a52608cc")
        # just to keep track of the proggress
        print(i, ' out of 199')
        for j in range(len(content)):
            href_tag = content[j].find('a', href=True)
            href_tag = str(href_tag)
            id = re.search("ID(\d+).html", href_tag)
            id = id.group(1)
            price = content[j].find(class_="_95eae7db").text
            bedrooms = content[j].find("span", class_="e05e3d9c")
            # Bedroom, bathroom, and area have the same class name so we just find the next sibling
            bath_area = bedrooms.find_next_siblings("span", class_="e05e3d9c")
            # the next sibling contains 2 classes one for the bathroom and one for the area
            bathrooms = bath_area[0].text
            area = bath_area[1].text
            # area got a lot of weird text, I just split it and took only the number part
            # area=area.split("area")[1]
            bedrooms = bedrooms.text
            location = content[j].find("span", class_="_2fc90438").text
            date_posted_string = content[0].find("span", class_="c4ad15ab").text

            list_id.append(id)
            list_price.append(price)
            list_bedroom.append(bedrooms)
            list_bathroom.append(bathrooms)
            list_area.append(area)
            list_location.append(location)
            list_date_posted_string.append(date_posted_string)

    logger.info("Successfully Scraped")

    list_date_posted_converted = []
    for i in list_date_posted_string:
        list_date_posted_converted.append(date_converter(i))

    logger.info("Converted date_posted to date_time format")

    df = pd.DataFrame(np.column_stack(
        [list_price, list_bedroom, list_bathroom, list_area, list_location, list_date_posted_converted, list_id]),
        columns=['Price', 'Bedrooms', 'Bathrooms', 'Area', 'Location', 'date', 'id'])

    today = date.today()
    current_date = today.strftime("%m-%d-%y")
    initial_csv_name = "initial_Data({})".format(current_date)
    initial_data_path = "Data/initial Data/" + initial_csv_name + ".csv"
    df.to_csv(initial_data_path, index=False)
    logger.info("{}.csv Saved".format(initial_csv_name))

    try:
        df_cleaned = dfCleaner(initial_data_path)
    except:
        logger.error('CLeaning FAILED !!')

    clean_csv_name = "clean_Data({})".format(current_date)
    clean_data_path = "Data/clean Data/" + clean_csv_name + ".csv"
    df_cleaned.to_csv(clean_data_path, index=False)
    logger.info("{}.csv Saved".format(clean_csv_name))


if __name__ == "__main__":
    try:
        main()
    except:
        logger.critical('MAIN ERROR FALIED')
