import pandas as pd
import re
from datetime import date
import numpy as np
from datetime import date, timedelta



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

    # unique id check and drop
    id_df = pd.read_csv("Data/unique_id.csv")
    df = df.loc[~df['id'].isin(id_df['id']), :]

    # add new unique id from df to id list
    new_id_df = pd.concat([id_df[['id']], df[['id']]])
    new_id_df.to_csv("Data/unique_id.csv", index=False)

    return df