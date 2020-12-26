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

#download file from web
url = 'https://d17h27t6h515a5.cloudfront.net/topher/2017/August/599fd2ad_image-predictions/image-predictions.tsv'

if not os.path.exists(url.split('/')[-1]):
    response = requests.get(url)

    with open(os.path.join(url.split('/')[-1]), mode = 'wb') as file: #add encoding
        file.write(response.content)

print(os.listdir())

#twitter api information
