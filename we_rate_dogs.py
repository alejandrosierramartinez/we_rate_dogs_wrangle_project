# load packages
import pandas as pd 
import numpy as np
import matplotlib as plt
import seaborn as sb 
import requests
import os
import json
#import tweepy

#read csv
twitter_archive = pd.read_csv('twitter-archive-enhanced.csv')
print(twitter_archive.head())

#download file from web
url = 'https://d17h27t6h515a5.cloudfront.net/topher/2017/August/599fd2ad_image-predictions/image-predictions.tsv'

if not os.path.exists(url.split('/')[-1]):
    response = requests.get(url)

    with open(os.path.join(url.split('/')[-1]), mode = 'wb') as file: #add encoding
        file.write(response.content)

image_predictions = pd.read_csv('image-predictions.tsv', sep='\t')
print(image_predictions.head())

#twitter api information
import tweepy

consumer_key = '0Bfm4ndyhQn7KySsuh51Vnukm'
consumer_secret = 'gqTSd4AMo69HT1AnaXjhz1IXgF5BFRCOtYWnYUyufRChtMhRof'
access_token = '524802061-TeSt8iwdGD32eUZX0AfMKGmce6mVM7NERYnQE7KM'
access_secret = '0V5dTYz0dvY8aoFbylbQGj8lxPmY1T5lJPayRpVdBQTxr'

auth = tweepy.OAuthHandler(consumer_key, consumer_secret)
auth.set_access_token(access_token, access_secret)

api = tweepy.API(auth)
