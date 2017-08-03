"""\
Set command line papameters
--------------------------------------------------------------------------------
    USE: python <PROGNAME> (options) keyfile response
    ACTION: computes IR system performance measures, given input files:
        
    OPTIONS:
        -h : print this help message
        -s FILE : use stoplist file FILE (not Required)
        -d FILE : use document Collection file FILE (required if not reading index file)
        -q FILE : use query file FILE (required)
        -S Boolean : use stemming (not required)
        -i FILE : index file for either reading or creating based on I option FILE (required)
        -I Boolean : create index file (if not included read index file i)
        -m : method of term weighting can be 'b' (binary), 'tf' (term frequency) or 'tfidf' (term frequency, inverse document frequency) (required)
        -n Int : number of documents to return per query (required)
        -r FILE : create results file FILE (required)
    
--------------------------------------------------------------------------------
"""
import sys, re, getopt
from read_documents import ReadDocuments
from nltk.stem import PorterStemmer
import numpy as np
import pickle
import math

opts, args = getopt.getopt(sys.argv[1:],'hs:d:q:Ii:m:n:r:S')
opts = dict(opts)
filenames = args

def checkOpts():
    if '-i' not in opts:
        print ("-i is a required option")
        sys.exit(0)
    if '-q' not in opts:
        print ("-q is a required option")
        sys.exit(0)
    if '-I' in opts:
        if '-d' not in opts:
            print ("-d is a required option when creating index file")
            sys.exit(0)
    if '-m' not in opts:
        print ("-m is a required option")
        sys.exit(0)
    if '-n' not in opts:
        print ("-n is a required option")
        sys.exit(0)
    if '-r' not in opts:
        print ("-r is a required option")
        sys.exit(0)

def getStopWords():
    
    stops=set()   
    with open(opts['-s'],'r') as stopList:
        for line in stopList:
            stops.add(line.strip())
    return stops
        
                

def tokenizeInput(stops):
    
    docIndex=[] #list of dictionaries where each index is token frequency in one doc
    docFrequency={} # number of documents that contain each token, frequency of each token in collection
        
    docCount=0 #number of docs in collection
    
    documents = ReadDocuments(opts['-d'])
    for doc in documents:
            
        docDict={} #token is key value is number of times word appears in document
        docCount+=1 #docCount=len(documents)?
        
        for line in doc.lines:
                
                
            tokenize = re.compile(r'[A-Za-z]+') #regex to tokenize each line
            tokens = tokenize.findall(line.lower())
                
            for token in tokens:
                if (token!=None and token!=''):
                                            
                    if  '-S' in opts: #perform stemming using porter stemmer
                        stemmer = PorterStemmer()
                        token = stemmer.stem(token)
                        
                    if token not in stops:
                            
                        if token not in docDict: #add token to document dictionary
                                
                            docDict[token]=1
                            
                            if token not in docFrequency: #first time token is seen in collection
                                docFrequency[token] = 1
                                
                            elif token in docFrequency: #add 1 for every document containing token in collection
                                docFrequency[token] += 1
                            
                        elif token in docDict: #increment token if already in dictionary
                            docDict[token] += 1
                            
        docIndex.append(docDict)
            
   
    return docIndex, docFrequency, docCount
    
    
                        
def tokenizeQuery(stops, queries):

    queryIndex=[] #list of dictionaries where each index is token frequency in one query
        
    for query in queries:
            queryDict={}
            for line in query.lines:
                
                tokenize = re.compile(r'[A-Za-z]+') #regex to tokenize each line
                tokens = tokenize.findall(line.lower())
                
                for token in tokens:
                    if (token != None) and (token != ''):
                                                
                        if  '-S' in opts: #perform stemming using porter stemmer
                            stemmer = PorterStemmer()
                            token = stemmer.stem(token)
                        
                        if token not in stops:
                            
                            if token not in queryDict: #add token to query dictionary
                                
                                queryDict[token]=1
                            
                            elif token in queryDict: #increment token if alread in dictionary
                                queryDict[token] += 1
                            
            queryIndex.append(queryDict)
    
    return queryIndex

    
def calcRanking(docIndex,queryIndex,docFrequency,docCount, method):
    

    docValues=[]
    idf={} #inverse document frequency for collection
    docVectorSize=[] #length of doc vectors
    #queryVectorSize=[]
    
    for token in docFrequency:
        idf[token]=math.log(docCount/docFrequency[token]) #calculate idf for all tokens
        
    for docDict in docIndex:
        docSize=0
        
        for token in docDict:
            if method == 'b': #binary weighting
                docSize += 1
            if method == 'tf': #term frequency weighting
                docSize += docDict[token]**2
            if method == 'tfidf': #term frequency, inverse document frequency weighting
                docSize += (docDict[token]*idf[token])**2
            
        docVectorSize.append(math.sqrt(docSize))
        
    
    #don't need to calculate query vector size as it doesn't effect ranking
    
    #for queryDict in queryIndex:
        
     #   querySize = 0
        
      #  for token in queryDict:
        #    if method == 'b': #binary weighting
       #         querySize += 1
         #   if method == 'tf': #term frequency weighting
          #      querySize += queryDict[token]**2
           # if method == 'tfidf': #term frequency, inverse document frequency weighting
            #    querySize += (queryDict[token]*idf[token])**2
            
        #queryVectorSize.append(math.sqrt(querySize))

    
    for queryDict in queryIndex:
        queryKeys=set(queryDict.keys())
        tempDocValues=[]
        for docDict in docIndex:
            docKeys=set(docDict.keys())
            tempDict = dict((k,docDict[k]) for k in docKeys & queryKeys) # dict of doc key val pairs where key exists in query
            if method =='b':
               for token in tempDict:
                   tempDict[token]=1 #binary weighting so term frequency is removed
            elif method =='tfidf':
                for token in tempDict:
                    tempDict[token]=tempDict[token]*idf[token] #tfidf weighting
            tempDocValues.append(tempDict)
        
        docValues.append(tempDocValues)
      
    return docValues, docVectorSize

        
 

    
def getSimilarity(queryIndex, docIndex, docVectorSize,numOfQueries, docValues):
    similarities=[]
    
    for i in range (numOfQueries):
        similarity=[]
        for j in range(len(docValues[i])):
            tempDict = {key : val * docValues[i][j][key] for key, val in queryIndex[i].items() if key in docValues[i][j]}                               
            similarity.append((sum((tempDict).values()))/docVectorSize[j])
            
        similarities.append(similarity)
            
            
        
    return similarities
    
def writeResultsFile(path, similarities, numOfQueries, numOfResults):
    
    with open(path, 'w') as results:
        for i in range(numOfQueries):
            #ranking = np.argpartition(similarities[i],-7)[-7:]
            #ranking = [index for index, z in enumerate(similarities[i]) if z > 1] 
            
            #if len(ranking)<10:
            ranking = np.argpartition(similarities[i],-numOfResults)[-numOfResults:]
            
            for j in range(len(ranking)):
                results.write(str(i+1))
                results.write(" ")
                results.write(str(ranking[j]+1))
                results.write('\n')
    
       
def writeIndexFile(path, docCount, docIndex, docFrequency):
    
    with open(path,'wb') as index:
        pickle.dump([docIndex, docFrequency, docCount],index)   
        
                  
    
def readIndexFile(path):
    with open(path,'rb') as index:
        docIndex, docFrequency, docCount = pickle.load(index)
    
    return docIndex, docFrequency, docCount
    


if __name__ == '__main__':
    
    if '-h' in opts:
        help = __doc__.replace('<PROGNAME>',sys.argv[0],1)
        print(help,file=sys.stderr)
        sys.exit()
        
    checkOpts()    

    if opts['-m'] != 'b' and opts['-m'] != 'tf' and opts['-m'] != 'tfidf':
        print ('term weighting method must be "b" or "tf" or "tfidf"' )        
        sys.exit(0)
        
        
    if '-s' in opts:
        stops=getStopWords()#set()
    else:
        stops=set()
        
    
      
    if '-I' in opts:
        docIndex, docFrequency, docCount = tokenizeInput(stops)
        writeIndexFile(opts['-i'], docCount, docIndex, docFrequency)
    else:
        docIndex, docFrequency, docCount = readIndexFile(opts['-i'])
        
    
    
    queryIndex=tokenizeQuery(stops, ReadDocuments(opts['-q']))    
    
    docValues, docVectorSize = calcRanking(docIndex,queryIndex,docFrequency,docCount,opts['-m'])
    
    numOfQueries=len(queryIndex)
    
    similarities=getSimilarity(queryIndex, docIndex, docVectorSize,numOfQueries, docValues)
    
    writeResultsFile(opts['-r'],similarities,numOfQueries, int(opts['-n']))
    
    