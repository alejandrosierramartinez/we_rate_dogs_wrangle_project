f=open('twitter_api_information.txt',"r")
lines=f.readlines()
consumer_key = lines[0]
consumer_secret = lines[1]
access_token = lines[2]
access_secret = lines[3]
f.close()

print(consumer_key)
print(consumer_secret)
print(access_token)
print(access_secret)