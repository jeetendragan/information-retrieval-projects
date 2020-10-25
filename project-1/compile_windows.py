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

def getProcessedTweet(tweet, country):
    tweet_text = None
    if "retweeted_status" in tweet:
        tweet_text = tweet['retweeted_status']['full_text']
    else:
        tweet_text = tweet['full_text']

    stop_words = None
    if country == "USA":
        tweet["lang"] = "en"
        stop_words = stop_words_en
    elif country == "Italy":
        if tweet["lang"] == 'en' or tweet["lang"] == 'und':
            stop_words = stop_words_en
            tweet["lang"] = "en"
        else:
            stop_words = stop_words_it
            tweet["lang"] = "it"
    else:
        if tweet["lang"] == 'en' or tweet["lang"] == 'und':
            stop_words = stop_words_en
            tweet["lang"] = "en"
        elif tweet["lang"] == "it":
            stop_words = stop_words_it
            tweet["lang"] = "it"
        else:
            stop_words = stop_words_hi
            tweet["lang"] = "hi"
    
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

if __name__ == "__main__":
    allTweets = {}
    dataPath = "./data_general/"
    files = [f for f in listdir(dataPath) if isfile(join(dataPath, f))]
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
        
        tweetsInFile = 0
        hindiInFile = 0
        italianInFile = 0
        englishInFile = 0
        undefInFile = 0
        langCount = {}

        tweetsAsJson = json.loads(fileContents)["allTweets"]
        for tweetId in tweetsAsJson:
            if tweetId in allTweets:
                continue

            tweet = tweetsAsJson[tweetId]
            processed_tweet = getProcessedTweet(tweet, country)
            if processed_tweet == None:
                undefInFile += 1
                continue
            tweetsInFile += 1            
            if processed_tweet["lang"] == 'en':
                englishInFile += 1
            elif processed_tweet["lang"] == "it":
                italianInFile += 1
            elif processed_tweet["lang"] == "hi":
                hindiInFile += 1
            else:
                if processed_tweet["lang"] in langCount:
                    langCount[processed_tweet['lang']] += 1
                else:
                    langCount[processed_tweet['lang']] = 1

            allTweets[tweetId] = processed_tweet

        print("For POI: "+fileName)
        print("Total Tweets: "+str(tweetsInFile))
        print("English Tweets: "+str(englishInFile))
        print("Hindi: "+str(hindiInFile))
        print("Italian: "+str(italianInFile))
        print("Undefined: "+str(undefInFile))
        for lang in langCount:
            print(lang+": "+str(langCount[lang]))
        print("\n\n")

    allTweetsFormattedJson = json.dumps(allTweets)
    outputFile = open("./output/window_output.json", "w")
    outputFile.write(allTweetsFormattedJson)
    outputFile.close()