# read all files from the data folder and add fields like so in the output-

#• poi_name : Screen name of one of the 9 persons of interest. Null if the tweet is from general public.
#• poi_id : User Id of one of the 9 persons of interest. Null if the tweet is from general public.
#• country : One of the 3 countries
#• tweet_text : Default field
#• tweet_lang : Language of the tweet from Twitter as a two letter code.
#• text_xx : For language specific fields where xx is at least one amongst en(English), hi (Hindi) and it (Italian)
#• hashtags : if there are any hashtags within the tweet text
#• mentions : if there are any mentions within the tweet text
#• tweet_urls : if there are any urls within the tweet text
#• tweet_emoticons : if there are any emoticons within the tweet text
#• tweet_date : Tweet creation date rounded to nearest hour and in GMT

from os import listdir
from os.path import isfile, join
import json
import re
import nltk
import datetime
from functools import reduce
from itertools import chain
import demoji

def getHindiStopWords():
    hindiStopWordsFile = open("hindi_stopwords.txt")
    hindiStopWordsTxt = hindiStopWordsFile.read()
    return hindiStopWordsTxt.split("\n")

def hour_rounder(t):
    # Rounds to nearest hour by adding a timedelta hour if minute >= 30
    return (t.replace(second=0, microsecond=0, minute=0, hour=t.hour)
               +datetime.timedelta(hours=t.minute//30))

def getProcessedTweet(tweet, country):
    tweet_text = None
    if "retweeted_status" in tweet:
        tweet_text = tweet['retweeted_status']['full_text']
    else:
        tweet_text = tweet['full_text']

    stop_words = None
    if tweet["lang"] == 'en':
        stop_words = stop_words_en
    elif tweet["lang"] == 'und':
        stop_words = stop_words_en
    elif tweet["lang"] == "it":
        stop_words = stop_words_it
    elif tweet["lang"] == "hi":
        stop_words = stop_words_hi
    else:
        #raise Exception("Language unsupported: "+tweet["lang"]+", Tweet: "+text+", ScreenName: "+tweet['poi_name'])
        print("Language unsupported: "+tweet["lang"]+", Tweet: "+tweet_text+", ScreenName: "+tweet["user"]["screen_name"])
        return None
    
    if tweet["user"]["screen_name"] in poi_map:
        tweet['poi_name'] = tweet["user"]["screen_name"]
    else:
        tweet['poi_name'] = None
    tweet['poi_id'] = tweet["user"]["id"]
    tweet['country'] = country
    tweet['tweet_text'] = tweet_text

    tweet['tweet_lang'] = tweet["lang"]
    # the tweet_xx field contains the stop words removed, no hashtags, no profile mentions,
    # no urls, no emoticons

    # get rid of emoticons first
    
    noEmpticonText = tweet_text
    result = demoji.findall(tweet_text)
    symbols = []
    if result == None or len(result) == 0:
        pass
    else:
        for emoji in result:
            #print(emoji)
            symbols.append(emoji)
    
    # collect all the user mentions, hashtags, and urls from given json
    entities = tweet["entities"]
    urls = [e["url"] for e in entities["urls"]]
    users = ["@"+e["screen_name"] for e in entities["user_mentions"]]
    media_urls = []
    if "media" in entities:
        media_urls = [e["url"] for e in entities["media"]]
    
    hashtags = ["#"+e["text"] for e in entities["hashtags"]]

    tweet_text = reduce(lambda t, s: t.replace(s, ""), chain(urls, media_urls, users, hashtags, symbols), noEmpticonText)

    word_tokens = nltk.word_tokenize(tweet_text.lower())
    filtered_sentence_arr = [w for w in word_tokens if not w in stop_words]
    
    filtered_sentence = ""
    for word in filtered_sentence_arr:
        filtered_sentence += word + " "
    
    if tweet["lang"] == "en" or tweet["lang"] == "und":
        tweet["text_en"] = filtered_sentence
    elif tweet["lang"] == "it":
        tweet["text_it"] = filtered_sentence
    else:
        # hindi
        tweet["text_hi"] = filtered_sentence

    tweet["hashtags"] = [hashtag[1:] for hashtag in hashtags]
    tweet['mentions'] =  [mention[1:] for mention in users]
    tweet['tweet_urls'] = urls
    tweet['tweet_emoticons'] = symbols

    date_time_obj = datetime.datetime.strptime(tweet["created_at"], '%a %b %d %H:%M:%S %z %Y')

    rounded_hour = hour_rounder(date_time_obj)
    rounded_hour_str = rounded_hour.strftime("%Y-%m-%dT%H:%M:%S.%f%Z")
    tweet["tweet_date"] = rounded_hour_str
    return tweet
    
poi_map_file = open("pois_map.json")
poi_map_contents = poi_map_file.read()
poi_map_file.close()
poi_map = json.loads(poi_map_contents)

emoji_pattern = re.compile("["
        u"\U0001F600-\U0001F64F"  # emoticons
        u"\U0001F300-\U0001F5FF"  # symbols & pictographs
        u"\U0001F680-\U0001F6FF"  # transport & map symbols
        u"\U0001F1E0-\U0001F1FF"  # flags (iOS)
                           "]+", flags=re.UNICODE)

stop_words_en = set(nltk.corpus.stopwords.words('english'))
stop_words_it = set(nltk.corpus.stopwords.words('italian'))
stop_words_hi = getHindiStopWords()

allTweetsFormatted = {}
dataPath = "./data/"
files = [f for f in listdir(dataPath) if isfile(join(dataPath, f))]
finalTweetString = ""
peopleSeen = 0
totalTweets = 0
for fileName in files:
    fil = open(dataPath+fileName)
    fileContents = fil.read()
    fil.close()

    country = None
    if "India" in fileName:
        country = "India"
    elif "Italy" in fileName:
        country = "Italy"
    elif "USA" in fileName:
        country = "USA"
    else:
        country = None

    poiCount = 0
    poiHindi = 0
    poiEnglish = 0
    poiItalian = 0
    poiUnd = 0
    
    tweetsAsJson = json.loads(fileContents)
    for tweetId in tweetsAsJson:
        tweet = tweetsAsJson[tweetId]
        processed_tweet = getProcessedTweet(tweet, country)
        if processed_tweet == None:
            poiUnd += 1
            continue
        poiCount += 1
        if tweet["lang"] == 'en':
            poiEnglish += 1
        elif tweet["lang"] == "it":
            poiItalian += 1
        elif tweet["lang"] == "hi":
            poiHindi += 1

        tweetString = json.dumps(processed_tweet)
        tweetString = tweetString.replace('color": "', 'color": "#')
        finalTweetString += tweetString
        totalTweets += 1
        allTweetsFormatted[tweetId] = processed_tweet
    
    print("For POI: "+fileName)
    print("Total Tweets: "+str(poiCount))
    print("English Tweets: "+str(poiEnglish))
    print("POI Undef: "+str(poiUnd))
    print("POI Hindi: "+str(poiHindi))
    print("POI Italian: "+str(poiItalian))
    print("\n\n")

print("Total tweets indexed yet: "+str(totalTweets))
outputFile = open("output/output.json", "w")
outputFile.write(finalTweetString)
outputFile.close()

allTweetsFormattedJson = json.dumps(allTweetsFormatted)
outputFile = open("output/proper_output.json", "w")
outputFile.write(allTweetsFormattedJson)
outputFile.close()