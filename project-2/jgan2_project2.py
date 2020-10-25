import sys
import re
from nltk.corpus import stopwords
from nltk.stem import PorterStemmer
import json

## classes
class Node:
    def __init__(self, docId = None, next = None):
        self.docId = docId
        self.next = next
        self.freq = 1
    
    def incFrequency(self):
        self.freq += 1

class LinkedList:

    def __init__(self, token):
        self.start_node = None # Head pointer
        self.end_node = None # Tail pointer
        self.token = token

    # Method to traverse a created linked list
    def traverse_list(self):
        traversal = []
        if self.start_node is None:
            print("List has no element")
            return None
        else:
            n = self.start_node
            # Start traversal from head, and go on till you reach None
            while n is not None:
                traversal.append("DocID: "+str(n.docId)+", Freq: "+str(n.freq))
                n = n.next
            return traversal

    def getDocIds(self):
        docIds = []
        if self.start_node is not None:
            n = self.start_node
            # Start traversal from head, and go on till you reach None
            while n is not None:
                docIds.append(n.docId)
                n = n.next
        return docIds

    def print(self):
        traversal = self.traverse_list()
        if traversal == None:
            print("______________")
            print(self.token+ ": Empty")
            print("______________")
        else:
            print("______________")
            print(self.token+": ")
            print(traversal, ',')
            print("______________")

    # Method to insert elements in the linked list
    def insert(self, docId):

        # Initialze a linked list element of type "Node" 
        new_node = Node(docId)
        currentHead = self.start_node # Head pointer

        # If linked list is empty, insert element at head
        if self.start_node is None:
            new_node = Node(docId)
            self.start_node = new_node
            self.end_node = new_node
            return "Inserted"
        else:
            if self.start_node.docId > docId:
                # If element to be inserted has lower docId than head, insert new element at head
                new_node = Node(docId)
                self.start_node = new_node
                self.start_node.next = currentHead
                return "Inserted"
            elif self.start_node.docId == docId:
                # if the head's docId and the new docid match, increment the frequency at the head node
                self.start_node.incFrequency()
            elif self.end_node.docId < docId:
                # If element to be inserted has higher docId than tail, insert new element at tail
                new_node = Node(docId)
                self.end_node.next = new_node
                self.end_node = new_node
                return "Inserted"
            elif self.end_node.docId == docId:
                # docId to be inserted exists at the tail, so just increment the frequency
                self.end_node.incFrequency()
            else:
                # If element to be inserted lies between head & tail, find the appropriate position to insert it
                ptr = self.start_node
                while True:
                    if ptr.docId == docId:
                        ptr.incFrequency()
                        return "Inserted"
                    else:
                        if ptr.next.docId > docId:
                            # it is 100% sure that ptr.docId < docId, and ptr.next != None
                            new_node = Node(docId)
                            nextTemp = ptr.next
                            ptr.next = new_node
                            new_node.next = nextTemp
                            return "Inserted"
                        else:
                            ptr = ptr.next
                return "Inserted"
## classes end here

def wordCount(tokens):
    tokenDict = {}
    for token in tokens:
        if token in tokenDict:
            tokenDict[token] += 1
        else:
            tokenDict[token] = 1
    return tokenDict

def tokenizeDocument(docContents):
    docContents = docContents.lower() # req a
    words = docContents.split(" ") # tokenize d
    filteredWords = []
    ps = PorterStemmer()
    for word in words:
        repWord = re.sub('[^a-z0-9]+', ' ', word) # b
        repWord = repWord.strip() # c
        if repWord == '' or repWord == ' ':
            continue
        wordsDelimitedBySpecChars = repWord.split(' ')
        for wordDelBySpecChar in wordsDelimitedBySpecChars:
            wordDelBySpecChar = wordDelBySpecChar.strip()
            if wordDelBySpecChar in stopwords.words('english') or wordDelBySpecChar == '':
                continue
            wordDelBySpecChar = ps.stem(wordDelBySpecChar) # f
            filteredWords.append(wordDelBySpecChar)
    return filteredWords

def buildPostingsList(docIdToTokens):
    postingsList = {} # key is token and value is LinkedList object
    for docId in docIdToTokens:
        tokenList = docIdToTokens[docId]
        for token in tokenList:
            if token in postingsList:
                linkedList = postingsList[token]
            else:
                linkedList = LinkedList(token)
                postingsList[token] = linkedList
            linkedList.insert(docId)
    return postingsList

def getQueryToTokens(queryFilePath):
    queryFileHand = open(queryFilePath)
    queries = queryFileHand.readlines()
    queryToTokens = {}
    for line in queries:
        if line == None:
            break
        tokens = tokenizeDocument(line)
        queryToTokens[line.strip()] = tokens
    return queryToTokens

def getPostingsListForQueries(queryToTokens, postingsList):
    queryPostingsList = {}
    
    for queryId in queryToTokens:
        queryTokens = queryToTokens[queryId]
        for queryToken in queryTokens:
            if queryToken not in queryPostingsList:
                queryPostingsList[queryToken] = postingsList[queryToken].getDocIds()
    
    return queryPostingsList

def generateOutputJson(outputFilePath, queryPostingsList, daatAnd):
    outputJson = {}
    outputJson['postingsList'] = queryPostingsList
    outputJson['daatAnd'] = daatAnd
    outputStr = json.dumps(outputJson)
    fileHandl = open(outputFilePath, "w")
    fileHandl.write(outputStr)
    fileHandl.close()

def getDaatAnd(queryToTokens, queryPostingsList):
    queryToResults = {}
    for query in queryToTokens:
        tokensInQuery = queryToTokens[query]
        docIntersectnForQuery = []
        if len(tokensInQuery) == 1:
            results = queryPostingsList[tokensInQuery[0]]
            num_comparisons = 0
            num_docs = len(tokensInQuery[0])
        else:
            num_comparisons = 0

            # make a dictionary with key as the token, and value as the len of postings list
            tokenToPostingsListLen = {}
            for token in tokensInQuery:
                tokenToPostingsListLen[token] = len(queryPostingsList[token])

            # sort the tokenToPostingsListLen by increasing order of length
            tokenToPostingsListLen = {k: v for k, v in sorted(tokenToPostingsListLen.items(), key=lambda item: item[1])}
            orderedTokens = list(tokenToPostingsListLen.keys())
            
            docIntersectnForQuery = queryPostingsList[orderedTokens[0]]
            for tokenIdx in range(1, len(orderedTokens)):
                token = orderedTokens[tokenIdx]
                tokenDocList2 = queryPostingsList[token]
                (intersectDoc, operations) = mergeLists(docIntersectnForQuery, tokenDocList2)
                docIntersectnForQuery = intersectDoc
                num_comparisons += operations

        queryToResults[query] = {
            'results' : docIntersectnForQuery,
            'num_docs' : len(docIntersectnForQuery),
            'num_comparisons' : num_comparisons
        }

    return queryToResults

def mergeLists(list1, list2):
    finalList = []
    p1 = 0
    p2 = 0
    comparisonCount = 0

    while p1 < len(list1) and p2 < len(list2):
        if list1[p1] < list2[p2]:
            comparisonCount += 1
            p1 += 1
        elif list1[p1] > list2[p2]:
            p2 += 1
            comparisonCount += 1     
        else:
            finalList.append(list1[p1])
            comparisonCount += 1
            p1 += 1
            p2 += 1
    return (finalList, comparisonCount)

def getDocIdToTokens(pathToCorpus):
    """Step 1: Build Your Own Inverted Index
    Implement a pipeline which takes as input the given corpus, and returns an inverted
    index.
    1. Extract the document ID and document from each line.
    2. Perform a series of preprocessing on the document:
        a. Convert document text to lowercase
        b. Remove special characters. Only alphabets, numbers and whitespaces
        should be present in the document. only ascii!
        c. Remove excess whitespaces. There should be only 1 white space
        between tokens, and no whitespace at the starting or ending of the
        document.
        d. Tokenize the document into terms using white space tokenizer.
        e. Remove stop words from the document.
        f. Perform Porter’s stemming on the tokens.
        g. Sample preprocessing output"""
    fileHandl = open(pathToCorpus)
    completeDocList = fileHandl.readlines()
    docIdToTokens = {}

    for line in completeDocList:
        if line == None:
            break
        lineContents = line.split("\t")
        try:
            docId = int(lineContents[0])
            docContents = lineContents[1]
            tokens = tokenizeDocument(docContents)
            docIdToTokens[docId] = tokens
        except:
            print("Exception"+str(docId))
        #wordCnt = wordCount(tokens)
    return docIdToTokens


if __name__ == "__main__":
    """docText = "Management of ophthalmic perioperative period during 2019 novel coronavirus disease outbreak/ 新型冠状病毒肺炎疫情下眼科患者围手术期管理实践"
    tokens = tokenizeDocument(docText)
    docText = "Management of coronavirus is getting really hard. The outbreak is bad! Coronavirus is a deadly disease!"
    tokens2 = tokenizeDocument(docText)
    dic = {1:tokens, 2: tokens2}
    pl = buildPostingsList(dic)
    for token in pl:
        print(token)
        pl[token].print()
    exit()"""

    # expected jgan2_project2.py path_of_input_corpus output.json query.txt
    pathToCorpus = sys.argv[1] if sys.argv[1] != None else "Null"
    outputFilePath = sys.argv[2] if sys.argv[2] != None else "Null"
    queryFilePath = sys.argv[3] if sys.argv[3] != None else "Null"

    print("Corpus Path: "+pathToCorpus)
    print("Output Path: "+outputFilePath)
    print("Query  Path: "+queryFilePath)

    docIdToTokens = getDocIdToTokens(pathToCorpus)

    """print("Doc to tokens: ")
    for docID in docIdToTokens:
        st = ""
        for token in docIdToTokens[docID]:
            st += token+", "
        print(str(docID)+" " + st)"""

    print("Preparing Postings list")
    postingsList = buildPostingsList(docIdToTokens)
    """for token in postingsList:
        lList = postingsList[token]
        lList.print()"""
    print("Postings list created")

    queryToTokens = getQueryToTokens(queryFilePath)
    for queryId in queryToTokens:
        for query in queryToTokens[queryId]:
            print(query)

    queryPostingsList = getPostingsListForQueries(queryToTokens, postingsList)
    daatAnd = getDaatAnd(queryToTokens, queryPostingsList)
    generateOutputJson(outputFilePath, queryPostingsList, daatAnd)
