f = open("hindi_stopwords.txt")
text = f.read()
words = text.split("\n")
for w in words:
    print("Orignal: "+w+" - "+w.lower())