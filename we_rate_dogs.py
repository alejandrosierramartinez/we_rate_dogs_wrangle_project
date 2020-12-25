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