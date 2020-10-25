import json
import datetime

def getDateString(date):
    return str(date.year)+"-"+str(date.month)+"-"+str(date.day)

windowStart = "2020-9-14"
windowEnd = "2020-9-23"

# read the final file
finalHandlr = open("output/final_real_json.json")
contents = finalHandlr.read()
finalHandlr.close()
tweets = json.loads(contents)
statsByDay = {}
cnt = 0
for tweetId in tweets:
    tweet = tweets[tweetId]
    country = tweet["country"]
    if country == None:
        country = "Undef"
    poi_name = tweet["poi_name"]
    date = datetime.datetime.strptime(tweet["tweet_date"], '%Y-%m-%dT%H:%M:%S.%f%Z')
    dateStr = getDateString(date)
    if dateStr < windowStart or dateStr > windowEnd:
        continue
    cnt += 1
    if dateStr in statsByDay:
        if country in statsByDay[dateStr]:
            statsByDay[dateStr][country] += 1
        else:
            statsByDay[dateStr][country] = 1
        
        if poi_name in statsByDay[dateStr]:
            statsByDay[dateStr][poi_name] += 1
        else:
            statsByDay[dateStr][poi_name] = 1
    else:
        statsByDay[dateStr] = {}
        statsByDay[dateStr][country] = 1
        statsByDay[dateStr][poi_name] = 1

repHand = open("output/report.json", "w")
repHand.write(json.dumps(statsByDay))
repHand.close()

print("Written items: "+str(cnt))