#test lines have been commented to provide a clean script output

# load packages
import pandas as pd 
import numpy as np
import matplotlib.pyplot as plt
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

f=open('twitter_api_information.txt',"r")
lines=f.readlines()
consumer_key = lines[0]
consumer_secret = lines[1]
access_token = lines[2]
access_secret = lines[3]
f.close()

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

#create a copy of the df to work on
twitter_archive_new = twitter_archive.copy()
image_predictions_new = image_predictions.copy()
tweet_json_new = tweet_json.copy()


#data cleaning
# combine tables into a new one df where we perform cleaning operations
master_clean = twitter_archive_new.merge(image_predictions_new, on='tweet_id', how='inner').merge(tweet_json_new, on='tweet_id', how='inner')
#test
print(master_clean.head())
#print(master_clean.info())

#


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

#save master clean to csv file
master_clean.to_csv('twitter_archive_master.csv')

#data exploration
# correlation matrix
numeric_vars = ['rating_numerator', 'p1_conf', 'p2_conf', 'p3_conf', 'retweet_count', 'favorite_count']

sb.heatmap(master_clean[numeric_vars].corr(), annot = True, fmt = '.2f',
           cmap = 'vlag_r', linewidths=.5 )
plt.title('Correlation matrix')
plt.xticks(fontsize=7, rotation=0)
plt.yticks(fontsize=7)
plt.show()

#rating univariate exploration
plt.hist(data = master_clean, x ='rating_numerator')
plt.title('Ratings histogram')
plt.xlabel('Rating')
plt.ylabel('Count')
plt.show()

#favorite counts univariate exploration
plt.hist(data = master_clean, x ='favorite_count')
plt.title('Favorites histogram')
plt.xlabel('Favorites')
plt.ylabel('Count')
plt.show()

#retweet counts univariate exploration
plt.hist(data = master_clean, x ='retweet_count')
plt.title('Retweets histogram')
plt.xlabel('Retweets')
plt.ylabel('Count')
plt.show()

#ratings, retweets and favorites scatterplot
scatter_vars = ['rating_numerator', 'favorite_count', 'retweet_count']

g = sb.PairGrid(data = master_clean, vars = scatter_vars, height = 1.5, aspect = 1.5)
g = g.map_diag(plt.hist);
g.map_offdiag(sb.regplot, scatter_kws={'alpha':0.15})
plt.subplots_adjust(top=0.9)
plt.suptitle("Scatterplot grid")
plt.show()

#ratings by dog breed
breeds = master_clean.groupby('p1').agg(count=('rating_numerator', 'size'), mean_rating=('rating_numerator', 'mean')).reset_index()
breeds = breeds.sort_values('count', ascending=False)

#plot top ten count breeds
breeds_top_ten = breeds.iloc[0:10,:]

base_color = sb.color_palette()[0]
sb.barplot(y='mean_rating', x='p1', data=breeds_top_ten, color = base_color)
plt.xticks(rotation=30, size=8)  # Set text labels.
plt.ylim(0, 15)
plt.title('Breeds mean rating')
plt.xlabel('Breed')
plt.ylabel('Mean rating')
plt.show()

#ratings, favorites and retweets
#three variable heatmap
master_clean['favorites_bin'] = pd.qcut(master_clean['favorite_count'], 10)
master_clean['retweets_bin'] = pd.qcut(master_clean['retweet_count'], 10)

master_clean.drop_duplicates(['favorites_bin','retweets_bin'], inplace=True)
data_pivoted = master_clean.pivot('favorites_bin', 'retweets_bin', 'rating_numerator')
ax = sb.heatmap(data_pivoted, cmap="Blues", linewidths=.5)
plt.title('Ratings by favorites and retweets')
ax.invert_yaxis()
plt.yticks(size=6)
plt.xticks(np.arange(10), ['0-0.4', '0.4-0.9', '0.9-1.8', '1.8-2.6', '2.6-3.4', '3.4-4.8', '4.8-7.4', '7.4-12.5', '12.5-20', '20-150'])  # Set text labels.
plt.xticks(rotation=30, size=6)
plt.yticks(np.arange(10), ['0-0.2', '0.2-0.4', '0.4-0.6', '0.6-0.8', '0.8-1.1', '1.1-1.6', '1.6-2.2', '2.2-3.3', '3.3-5.5', '5.5-7.6'])  # Set text labels.
plt.xlabel('Favorites (x1000)', size = 10)
plt.ylabel('Retweets( x1000)', size = 10)
plt.show()