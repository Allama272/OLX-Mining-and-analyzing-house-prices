import pandas as pd
import re
from datetime import date
import numpy as np
from datetime import date, timedelta
import logging

logger = logging.getLogger(__name__)
logger.setLevel(logging.INFO)

formatter = logging.Formatter("%(levelname)s:%(asctime)s:%(name)s:%(message)s",datefmt="%Y-%m-%dT%H:%M:%S%z")

file_handler = logging.FileHandler('weeklyLogger.log')
file_handler.setFormatter(formatter)

logger.addHandler(file_handler)

def dfCleaner(path):
    df = pd.read_csv(path)

    # Remove strings from price, area, and bathrooms
    df['Price'] = df["Price"].str.replace(r"[\D]", '', regex=True)
    df['Price'] = df['Price'].astype(int)

    df['Area'] = df["Area"].str.replace(r"[\D]", '', regex=True)
    df['Area'] = df['Area'].astype(int)

    df['Bathrooms'] = df['Bathrooms'].astype(str)
    df['Bathrooms'] = df["Bathrooms"].str.replace(r"[\D]", '', regex=True)
    df['Bathrooms'] = df['Bathrooms'].astype(int)

    # Remove "Alexandria" and only keep the location
    df["Location"] = df["Location"].str.split(',').str[0]

    # replace "Laurent" with "Louran
    df["Location"] = df["Location"].str.replace('Laurent', "Louran")

    # drop duplicates according to id
    df = df.drop_duplicates(subset='id')
    all_id_num = df.shape[0]

    # unique id check
    id_df = pd.read_csv("Data/unique_id.csv")
    new_id=df.loc[~df['id'].isin(id_df['id']), :]
    unique_id_num= new_id.shape[0]

    logger.info("{0}:unique id found out of:{1}".format(unique_id_num,all_id_num))
    # add new unique id from df to id list
    new_id_df = pd.concat([id_df[['id']], new_id[['id']]])
    new_id_df.to_csv("Data/unique_id.csv", index=False)
    logger.info("Saved new id list with new:{0} ids now total:{1}".format(unique_id_num,new_id_df.shape[0]))

    return df
