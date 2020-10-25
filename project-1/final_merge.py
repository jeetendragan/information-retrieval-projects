import json

# read window tweets, and the POI tweets
# merge them
# make sure that all stats are fulfilled

windowFilePath = "./output/window_output.json"
poiFilePath = "./output/proper_output.json"

finalTweets = {}
finalTweetSolrStr = ""

poiFileHandl = open(poiFilePath)
poiContents = poiFileHandl.read()
poiFileHandl.close()
poiContentsJson = json.loads(poiContents)
for twitterId in poiContentsJson:
    tweet = poiContentsJson[twitterId]
    finalTweets[twitterId] = tweet
    tweetStr = json.dumps(tweet)
    tweetStr = tweetStr.replace('color": "', 'color": "#')
    finalTweetSolrStr += tweetStr


windowFileHandl = open(windowFilePath)
windowContents = windowFileHandl.read()
windowFileHandl.close()
windowContentsJson = json.loads(windowContents)
duplicateCount = 0
for twitterId in windowContentsJson:
    if twitterId in finalTweets:
        duplicateCount += 1
    else:
        tweet =  windowContentsJson[twitterId]
        finalTweets[twitterId] = tweet
        tweetStr = json.dumps(tweet)
        tweetStr = tweetStr.replace('color": "', 'color": "#')
        finalTweetSolrStr += tweetStr

totalTweetCount = len(list(finalTweets.keys()))
print("Final Tweet count: "+str(totalTweetCount))
print("Duplicates removed: "+str(duplicateCount))

finalFileHandlr = open("./output/final.json", "w")
finalFileHandlr.write(finalTweetSolrStr)
finalFileHandlr.close()

finalFileHandlr = open("./output/final_real_json.json", "w")
finalFileHandlr.write(json.dumps(finalTweets))
finalFileHandlr.close()