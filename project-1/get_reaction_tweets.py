from tweepy import OAuthHandler
from tweepy import Stream
from tweepy import Cursor
import json
from tweepy import API
import sys
from datetime import datetime
from datetime import timedelta
import os
import time

def hour_rounder(t):
    # Rounds to nearest hour by adding a timedelta hour if minute >= 30
    return (t.replace(second=0, microsecond=0, minute=0, hour=t.hour)
               +timedelta(hours=t.minute//30))

def getDateString(date):
    return str(end.year)+"-"+str(end.month)+"-"+str(end.day)

def dumpInfo(countryName, date, retweets, allTweetDictionary, minTweetId):
    storeFile = open("data_general"+"/"+countryName+"_"+date+".json", "w")
    allTweetIds = list(allTweetDictionary.keys())
    allTweetIds = [int(id) for id in allTweetIds]
    storageInfo = {
        "retweets" : list(retweets),
        "allTweets" : allTweetDictionary,
        "tweetIds": allTweetIds,
        "minTweetId" : minTweetId
    }
    storageInfoAsJson = json.dumps(storageInfo)
    storeFile.write(storageInfoAsJson)
    storeFile.close()

    print("Written a toal of: "+str(len(allTweetIds))+", Retweets: "+str(len(list(retweets))))
    print("Min of all tweet ids: "+str(minTweetId))

CREDENTIALS_FILE = "credentials.json"

cred_file = open(CREDENTIALS_FILE)
cred_json_Contents = cred_file.read()
cred_file.close()
credentials = json.loads(cred_json_Contents)
credentialInstance = credentials[5]

auth = OAuthHandler(credentialInstance['CONSUMER_KEY'], credentialInstance['CONSUMER_SECRET'])
auth.set_access_token(credentialInstance['ACCESS_TOKEN'], credentialInstance['ACCESS_TOKEN_SECRET'])

apiInst = API(auth_handler=auth)

batchCount = 10000
minTweetId = sys.maxsize
tweetCount = 1
retweets = 0
dates = {}
retweetsByDate = {}
end = datetime.today() - timedelta(days = 3)
endStr = getDateString(end)
print(endStr)
dayCount = 0
country = "India"
print("Fetching tweets for: "+country)
tweetsById = {}
query = "(covid OR pandemic OR lockdown OR coronavirus OR mask OR covid-19) AND (measures OR action OR governor OR policy OR government) AND (USA OR america OR trump OR cdc OR fauci OR Redfield OR california OR new york OR washington)"
query2 = "(anti-virus) AND (USA OR america)"
query2 = "(covid pandemic OR lockdown OR coronavirus OR mask OR covid-19) AND (india OR delhi OR maharashtra)"
query = "(covid OR corona OR pandemia OR coronavirus OR confinamento) AND (governo OR risposta OR politica)"
query2 = "(corona morta ) AND (italy OR italians OR bologna OR caserta OR Naples OR Agrigento OR codogno)"
query2 = "(covid OR pandemic OR lockdown OR coronavirus OR mask OR covid-19) AND (measures OR action OR governor OR policy OR government) AND (italy OR italians OR bologna OR caserta OR Naples OR Agrigento)"
query = "(covid OR pandemic OR lockdown OR coronavirus OR mask OR covid-19) AND (USA OR america OR trump OR cdc OR fauci OR Redfield OR california OR new york OR washington)"
query = "(कोविड OR कोरोना OR लॉकडाउन OR मौत) AND (सरकार OR मोदी OR केजरीवाल OR नीति OR दिल्ली)"
#AND (Italia OR italiani OR italiane OR conte OR Roberto Speranza)
stopOperation = False
#1306380895436320770
fileForDumpPath = "data_general" + "/" + country+"_"+endStr+".json"
if os.path.exists(fileForDumpPath):
    # read the file
    filePtr = open(fileForDumpPath)
    fileContents = filePtr.read()
    filePtr.close()
    existingInfo = json.loads(fileContents)
    tweetsById = existingInfo["allTweets"]
    listOfExistingIds = [int(id) for id in existingInfo["tweetIds"]]
    dates[endStr] = set(listOfExistingIds)
    retweetsByDate[endStr] = set(existingInfo["retweets"])
    totalTweetCount = len(existingInfo["tweetIds"])
    retweetCount = len(existingInfo["retweets"])
    # get the max of all the tweetids
    #minTweetId = min(listOfExistingIds)
    #minTweetId = existingInfo["minTweetId"]
    #minTweetId = 1305494011302391809
    print("Partial info exists: Total Tweets: "+str(totalTweetCount)+", Retweets: "+str(retweetCount))
    print("Min tweet id: "+str(minTweetId))
else:
    print("Partial info does not exist!")

try:
    for batchI in range(batchCount):
        if stopOperation:
            break
        try:
            if batchI == 0:
                tweets = apiInst.search(q = query, count = 500, max_id = minTweetId, tweet_mode = "extended", until = endStr)
            else:
                tweets = apiInst.search(q = query, count = 500, max_id = minTweetId, tweet_mode = "extended", until = endStr)

        except Exception as exc:
            # dump all the information, and break
            print(type(exc))
            print(exc)
            print("Exception occured: Dumping everythin..")
            endDateStr = getDateString(end)
            dumpInfo(country, endDateStr, retweetsByDate[endDateStr], tweetsById, minTweetId)
            break

        print("Another try")
        if len(tweets) == 0:
            print("Nothing returned")
            break
        else:
            print(str(len(tweets))+" Returned")
        for tweet in tweets:
            #print(str(tweetCount)+") "+tweet.full_text)
            minTweetId = tweet.id
            tweetDate = hour_rounder(tweet.created_at)
            date = getDateString(tweetDate)
            if date in dates:
                if len(dates[date]) > 4500:
                    print("Old Query Date: "+endStr+" "+str(len(dates[date])))

                    # save the tweets for the old date
                    print("More than 3150 tweets have been collected, dumping and closing")
                    dumpInfo(country, date, retweetsByDate[date], tweetsById, minTweetId)
                    stopOperation = True

                    if tweetDate.day < end.day:
                        end = tweetDate - timedelta(days = 1)
                    else:
                        end = end - timedelta(days = 1)
                    endStr = str(end.year)+"-"+str(end.month)+"-"+str(end.day)
                    print("Changing dates until: "+endStr)
                    break

                if tweet.id in dates[date]:
                    #print("Duplicate: "+str(tweet.id))
                    pass
                else:
                    if hasattr(tweet, 'retweeted_status'):
                        if len(retweetsByDate[date]) > 250:
                            #print("Dropping RT")
                            continue
                        else:
                            retweetsByDate[date].add(tweet.id)
                    dates[date].add(tweet.id)
                    tweetsById[tweet.id] = tweet._json
                    print("Date: "+date+": "+str(len(dates[date])))
            else:
                print("__________________________________________________")
                print("New date: "+date)
                endDateStr = getDateString(end)
                if endDateStr != date:
                    # save the tweets for the old date, and stop
                    print("Date has changed, dumping everything, and exiting..")
                    dumpInfo(country, endDateStr, retweetsByDate[endDateStr], tweetsById, minTweetId)
                    stopOperation = True
                    break
                    
                dates[date] = set()
                dates[date].add(tweet.id)
                retweetsByDate[date] = set()
                if hasattr(tweet, 'retweeted_status'):
                    retweetsByDate[date].add(tweet.id)
                tweetsById[tweet.id] = tweet._json

except KeyboardInterrupt:
    print("Exception occured. Dumping everything and leaving")
    endDateStr = getDateString(end)
    dumpInfo(country, endDateStr, retweetsByDate[endDateStr], tweetsById, minTweetId)

print("Tweet count: "+str(tweetCount))