from tweepy import OAuthHandler
from tweepy import Stream
import json
from tweepy import API
import sys
from datetime import datetime
from datetime import timedelta

CREDENTIALS_FILE = "credentials.json"

cred_file = open(CREDENTIALS_FILE)
cred_json_Contents = cred_file.read()
cred_file.close()
credentials = json.loads(cred_json_Contents)
print("Printing the credentials:")
print(credentials['CONSUMER_KEY'])

auth = OAuthHandler(credentials['CONSUMER_KEY'], credentials['CONSUMER_SECRET'])
auth.set_access_token(credentials['ACCESS_TOKEN'], credentials['ACCESS_TOKEN_SECRET'])

apiInst = API(auth_handler=auth)

tweetCount = 1
batchCount = 10000
minTweetId = sys.maxsize
allTweets = {}
country = "USA"
handle = "realDonaldTrump"
retweets = 0
hindiTweets = 0
italianTweets = 0
englishTweets = 0
tweetsOnDates = {}
minDate = None
rawTweetCount = 0
retweetsCounted = 0
otherLanguages = set()
otherLanguagesCount = 0

for batchI in range(batchCount):
    if batchI == 0:
        tweetsStr = apiInst.user_timeline(screen_name = handle, count = 20, tweet_mode = "extended")
    else:
        tweetsStr = apiInst.user_timeline(screen_name = handle, count = 20, max_id = minTweetId, tweet_mode = "extended")

    if rawTweetCount > 850:
        break

    for tweet in tweetsStr:
        tweetId = tweet.id
        rawTweetCount += 1
        if tweetId in allTweets:
            print("Tweet seen before: Raw Count: "+str(rawTweetCount))
            continue

        if tweet.lang == "hi":
            hindiTweets += 1
        elif tweet.lang == "it":
            italianTweets += 1
        elif tweet.lang == "en":
            englishTweets += 1
        else:
            otherLanguages.add(tweet.lang)
            otherLanguagesCount += 1
            print(str(tweetCount)+") "+" id: "+str(tweet.id)+" : "+tweet.full_text+"\n")
            continue


        if hasattr(tweet, 'retweeted_status'):
            retweets += 1
            if retweets > 200:
                print("Dropping this retweet")
                continue
            else:
                retweetsCounted += 1

        tweetCount += 1
        allTweets[tweet.id] = tweet._json
        #Thu Sep 17 19:01:37 +0000 2020
        #date_time_obj = datetime.strptime(tweet.created_at, '%a %b %d %H:%M:%S %z %Y')
        date = str(tweet.created_at.day)+":"+str(tweet.created_at.month)+":"+str(tweet.created_at.year)
        tweetDate = tweet.created_at.replace(hour = 0, minute = 0, second = 0, microsecond = 0)
        minDate = tweetDate
        #print("Raw: "+str(rawTweetCount))
        #print(str(tweetCount)+") "+" id: "+str(tweet.id)+" : "+date+" : "+tweet.full_text+"\n")

        tweetsOnDates[date] = True
    
        if tweetId < minTweetId:
            minTweetId = tweetId

    if tweetCount >= 1400:
        print(str(tweetCount)+" tweets retrived for user. Stoping.")
        break

tweetsJsonString = json.dumps(allTweets)
f = open("data/POI_"+country+"_"+handle+".json", "w")
f.write(tweetsJsonString)
f.close()

today = datetime.today()
today = today.replace(hour=0, minute=0, second=0, microsecond=0)
print("Today!::")
print(today)
dayDiff = (today - minDate).days

print("Tweets missing dates: ")
for i in range(1, dayDiff+1):
    dateStr = str(today.day)+":"+str(today.month)+":"+str(today.year)
    if dateStr in tweetsOnDates:
        print(dateStr+": Tweet True")
    else:
        print(dateStr+": Tweet False")
    today = today - timedelta(days=1)

print("Retweets seen: "+str(retweets))
print("Retweets counted: "+str(retweetsCounted))
print("Total tweets: "+str(tweetCount))
print("English tweets: "+str(englishTweets))
print("Hindi tweets: "+str(hindiTweets))
print("Itlaian tweets: "+str(italianTweets))
print("Other languages count: "+str(otherLanguagesCount))
outOtherLang = ""
for lang in otherLanguages:
    outOtherLang += lang+" "
print("Other languages used: "+outOtherLang)
