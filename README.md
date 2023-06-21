# OLX-Mining-and-analyzing-house-prices

## The main Aim of this project is to collect apartment sale ads information from OLX Alexandria -for now- and analyze it



## The Scrapper automatically collects data every 15 days and commits them 

## The collected data consists of [price (EGP), Bedrooms, Bathrooms, area (sqm), location, date posted and id]

#### The id is the unique id olx gives to each ad in order to keep track of any redundant data in the future
If upon scrapping in the new month there was an apartment that existed in the last month and was still not sold, it will still be counted in the data
The reason for doing so is that those apartments are still a part of the market and should not be removed

NOTE: Due to OLX rebranding as dubizzle some of the website code has been changed, and thus the data between 04/16/2023 up to 06/20/2023 has been lost
