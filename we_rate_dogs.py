# load packages
import pandas as pd 
import numpy as np
import matplotlib as plt
import seaborn as sb 
import requests
import os
import json
import tweepy

#read csv
twitter_archive = pd.read_csv('twitter-archive-enhanced.csv')


#download file from web
url = 'https://d17h27t6h515a5.cloudfront.net/topher/2017/August/599fd2ad_image-predictions/image-predictions.tsv'

if not os.path.exists(url.split('/')[-1]):
    response = requests.get(url)

    with open(os.path.join(url.split('/')[-1]), mode = 'wb') as file: #add encoding
        file.write(response.content)

image_predictions = pd.read_csv('image-predictions.tsv', sep='\t')

#twitter api information

consumer_key = '0Bfm4ndyhQn7KySsuh51Vnukm'
consumer_secret = 'gqTSd4AMo69HT1AnaXjhz1IXgF5BFRCOtYWnYUyufRChtMhRof'
access_token = '524802061-TeSt8iwdGD32eUZX0AfMKGmce6mVM7NERYnQE7KM'
access_secret = '0V5dTYz0dvY8aoFbylbQGj8lxPmY1T5lJPayRpVdBQTxr'

auth = tweepy.OAuthHandler(consumer_key, consumer_secret)
auth.set_access_token(access_token, access_secret)

api = tweepy.API(auth, wait_on_rate_limit = True, wait_on_rate_limit_notify = True)
#api = tweepy.API(auth)

#read retweet and favorite from api by id
if not os.path.exists('tweet_json.txt'):
#create dictionary to build file
    tweet_json = []
    count = 0
    for id in twitter_archive['tweet_id']:
        try:
            tweet = api.get_status(id, tweet_mode='extended')
            retweet_count = tweet.retweet_count
            favorite_count = tweet.favorite_count

            # Append to list of dictionaries
            tweet_json.append({'retweet_count': retweet_count,
                                'favorite_count': favorite_count,
                                'tweet_id': id})
        except tweepy.error.TweepError:
            count += 1
            print(str(count) + ' ' + 'Missing id:' + ' ' + str(id))

    #write twitter_df to a json file
    with open('tweet_json.txt', 'w') as outfile:
        json.dump(tweet_json, outfile)

with open('tweet_json.txt') as json_file:
    tweet_json = json.load(json_file)

tweet_json = pd.DataFrame(tweet_json, columns = ['tweet_id', 'retweet_count', 'favorite_count'])

#Assess data
print(twitter_archive.head())
print(twitter_archive.info())
#print(twitter_archive.sample(10))
#print(twitter_archive.describe())

#print(image_predictions.head())
#print(image_predictions.info())
#print(image_predictions.sample(10))
#print(image_predictions.describe())

#print(tweet_json.head())
#print(tweet_json.info())
#print(tweet_json.sample(10))
#print(tweet_json.describe())