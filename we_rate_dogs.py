#test lines have been commented to provide a clean script output

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
#print(twitter_archive.info())
#print(twitter_archive.describe())
#print(twitter_archive.sample(20))

#print(image_predictions.info())
#print(image_predictions.describe())
#print(image_predictions.sample(20))

#print(tweet_json.info())
#print(tweet_json.describe())
#print(tweet_json.sample(20))

#data cleaning
# combine tables into a new one df where we perform cleaning operations
master_clean = twitter_archive.merge(image_predictions, on='tweet_id', how='inner').merge(tweet_json, on='tweet_id', how='inner')
#test
#print(master_clean.head())
#print(master_clean.info())

#convert timestamp to date type
master_clean['timestamp'] = pd.to_datetime(master_clean.timestamp)
#test
#print(master_clean.info())

#numerator ratings min value
zero_ratings = master_clean.query('rating_numerator == 0')
print(zero_ratings)

#denominator different than 10
non_standard_denominator = master_clean.query('rating_denominator != 10')
print(non_standard_denominator['rating_denominator'].count())

#standard denominator 10
master_clean ['rating_numerator']= master_clean['rating_numerator']*10/master_clean['rating_denominator']
master_clean ['rating_denominator']= master_clean['rating_denominator']*10/master_clean['rating_denominator']

#test
#non_standard_denominator = master_clean.query('rating_denominator != 10')
#print(non_standard_denominator['rating_denominator'].count())

#numerator ratings max value
high_ratings = master_clean.query('rating_numerator > 15')
print(high_ratings[['tweet_id', 'expanded_urls', 'rating_numerator', 'rating_denominator', 'name', 'retweet_count', 'favorite_count']])

master_clean = master_clean.query('rating_numerator < 15')
#test
#print(master_clean.rating_numerator.max())
#print(master_clean.describe()[['rating_numerator', 'rating_denominator']])

#extract source from link in source column
source = []
for s in master_clean.source:
    source_split = s.split('>')[-2].split('<')[-2]
    source.append(source_split)

master_clean['source'] = source
print(master_clean.source.value_counts())

#test
#print(master_clean.source.head())

#dog stage column
master_clean['dog_stage'] = master_clean.doggo

master_clean.loc[master_clean['doggo']=='doggo', 'dog_stage'] = 'doggo'
master_clean.loc[master_clean['puppo']=='puppo', 'dog_stage'] = 'puppo'
master_clean.loc[master_clean['floofer']=='floofer', 'dog_stage'] = 'floofer'
master_clean.loc[master_clean['pupper']=='pupper', 'dog_stage'] = 'pupper'

#test
#print(master_clean.dog_stage.value_counts())

#extended urls column with duplicated information
#check for duplicated fields
count = 0
for url in master_clean.expanded_urls:
    if len(url.split(',')) > 1:
        if url.split(',')[1] != url.split(',') [-1]:
            count += 1
            print(count)
            print(False)
            print(url)

#split into one entry
urls = []
for url in master_clean.expanded_urls:
    if len(url.split(',')) > 1:
        urls.append(url.split(',')[-1])
    else:
        urls.append(url)

#test
#print(urls[0:5])


#dog names duplicated values
#print(master_clean.name.value_counts().head())
#print(master_clean[master_clean.name == "a"]['text'])

#identify text with "We only rate dogs." comment
#only_dogs = master_clean[master_clean['text'].str.contains('We only rate dogs.')]
#print(only_dogs[['rating_numerator', 'name', 'retweet_count', 'favorite_count', 'text']])

#drop rows without dogs
master_clean = master_clean[~master_clean.text.str.contains('We only rate dogs.')]

#test
#only_dogs = master_clean[master_clean['text'].str.contains('We only rate dogs.')]
#print(only_dogs[['rating_numerator', 'name', 'retweet_count', 'favorite_count', 'text']])

#zero favorites fields
zero_fav = master_clean.query('favorite_count == 0')
#for i in zero_fav.text:
#    print(i)

zero_rt = master_clean.query('retweet_count == 0')
print(zero_rt)