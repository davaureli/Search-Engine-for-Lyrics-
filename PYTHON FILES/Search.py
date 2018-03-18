##here we implement search algorithms

import time
start_time = time.time()

import heapq
from pymongo import MongoClient
from sklearn.cluster import KMeans 
from collections import Counter
import nltk
from wordcloud import WordCloud
import matplotlib.pyplot as plt
import pprint
import numpy as np
import collections


def normalise(lyric):
    #remove punctuation
    tokenizer = nltk.tokenize.RegexpTokenizer(r'\w+')
    lyric_sw = tokenizer.tokenize(lyric) #split the lyric in to tokens
    
    #Normalizing to lower
    lyric_sw = [token.lower() for token in lyric_sw]
    
    #Removing stop words and small words
    stops = set(nltk.corpus.stopwords.words('english') + nltk.corpus.stopwords.words('french') + nltk.corpus.stopwords.words('spanish') + nltk.corpus.stopwords.words('italian'))
    minlength = 2
    lyric_sw = [token for token in lyric_sw if ((not token in stops) and len(token) >= minlength)]
    
    #Stemming
    porter = nltk.PorterStemmer()
    lyric_sw = [porter.stem(token) for token in lyric_sw]
    
    return ' '.join(lyric_sw)


#This is for localmongodb
connection = MongoClient('localhost', 27017)
db = connection.HW3ADM #creation or re-creation of the database called HW3ADM


print('collecting data from the database...')
print('this operation could take a while...')

'''
#we used multiple mlab dbs to avoid 0.5gb space limitation issue
#this is for online mongodb
server1 = 'ds119446.mlab.com'
server2 = 'ds119436.mlab.com'
server3 = 'ds147985.mlab.com'
port1 = 19446
port2 = 19436
port3 = 47985
db_name = 'hw3adm'
username = 'GROUP-17'
password = 'hw3-GROUP-17'

conn1 = MongoClient(server1, port1)
conn2 = MongoClient(server2, port2)
conn3 = MongoClient(server3, port3)
db1 = conn1[db_name]
db2 = conn2[db_name]
db3 = conn3[db_name]
db1.authenticate(username, password)
db2.authenticate(username, password)
db3.authenticate(username, password)
'''

#Ninverted = (db2.index.find().count()) - 1 #retrun the total number of terms
Ninverted = (db.index.find().count()) - 1 #retrun the total number of terms

#getting the tf-idf's from the DB
diz_Tf_Idf = {}
#for tfidf in db3.indexTfIdf.find():
for tfidf in db.indexTfIdf.find():
    for k in tfidf.keys():
        diz_Tf_Idf[k] = tfidf[k]

#getting all the norms
norms = {}
#for norm in db1.norms.find():
for norm in db.norms.find():
    for k in norm.keys():
        norms[k] = norm[k]



#getting the total documents number from the DB
#N = db1.lyrics.find().count()
N = db.lyrics.find().count()

#getting some input from the user
Query = input('What are you looking for?: ')
Q=Query.split()
qt = input('what type of query do you need to perform? (1/2): ')







if qt == '1':
    ###Query type 1
    #Computatation of the numerators for the cosine similarity formula: scalar product between documents and the input stream
    
    l=[]

    for word in Q:
        if word.lower() in diz_Tf_Idf.keys(): #if the word exist in the dataset
            for i in set([e[0] for e in diz_Tf_Idf[word.lower()]]):
                l.append(i)
    
    l=list(set(l))
    
    numerator=[] #to get the document id of a numerator just take the content of the list l in the same position  
    for fileID in l:
        num=0
        for word in Q:
            if word.lower() in diz_Tf_Idf.keys():
                for elem in diz_Tf_Idf[word.lower()]:
                    if elem[0] == fileID:
                        num += elem[1]
                        break
        numerator.append(num)
    
    #computation of the cosine similarities between input stream an all documents
    cosineSim = []
    for i in range(len(l)):
        cos = (numerator[i])/((norms[str(l[i])])*(len(Q)**0.5))
        cosineSim.append(cos)
    
    if(len(cosineSim) >= 10):
        first10 = heapq.nlargest(10, enumerate(cosineSim), key=lambda x: x[1])
        
        first10Titles = []
        first10heap = []
        for i in first10:
            #s = db1.lyrics.find({'_id':l[i[0]]}, {'title':1})
            s = db.lyrics.find({'_id':l[i[0]]}, {'title':1})
            for el in s:
                first10Titles.append(el['title'])
            
            heapq.heappush(first10heap, (i[1], str(l[i[0]])))
        
        print('\nHeap of cosines and ID\'s of the first 10 songs that match your request:\n') #print from the lowest cosine to the heighest
        pprint.pprint(first10heap)
        print('\nTop 10 songs titles matching your requirements:\n')
        pprint.pprint(first10Titles)
    
    else: #the results are fewer than 10
    
        titles = []
        Songsheap = []
        for i in range(len(cosineSim)):
            #s = db1.lyrics.find({'_id':l[i]}, {'title':1})
            s = db.lyrics.find({'_id':l[i]}, {'title':1})
            for el in s :
                titles.append(el['title'])
            
            heapq.heappush(Songsheap, (cosineSim[i], str(l[i])))
            
        print('\nHeap of cosines and ID\'s of the songs that match your request:\n')
        pprint.pprint(Songsheap)
        print('\nTitles of songs matching your requirements:\n')
        pprint.pprint(titles)
    









if qt == '2':
    ###Query type 2
    
    l = []

    for word in Q:
        if word.lower() in diz_Tf_Idf.keys(): #if the word exist in the dataset
            for i in set([e[0] for e in diz_Tf_Idf[word.lower()]]):
                l.append(i)
        
    counts = Counter(l)
    
    ## this is to consider only documents that contain all the terms(and operation)
    intersection = [elem for elem in set(l) if counts[elem] == len(Q)]
    
    print('\nNumber of matching songs found: ', len(intersection))
    
    if len(intersection) > 0:
        ##  Now our user has to introduce k-value
        k = int(input("insert a value k for clustering (0 < k <= "+str(len(intersection))+"): "))
        
        if k > 0 and k <= len(intersection):
            ## for clustering, we have to normalize all the documents in the intersection ##                
            
            len_tot = ''
            for i in intersection:
                #s = db1.lyrics.find({'_id':i}, {'lyric':1})
                s = db.lyrics.find({'_id':i}, {'lyric':1})
                for stringa in s:
                    len_tot += ' '+normalise(stringa['lyric'])
            
            len_tot_L = list(set(len_tot.split()))
            
            vectors = np.zeros((len(intersection), len(len_tot_L))) #matrix with rows = intersection, coloumns = all_terms
            indexOrdered = collections.OrderedDict(diz_Tf_Idf)
            
            print('converting songs to vectors...')
            for doc in range(len(intersection)):
                term = 0 
                test = 0
                for key in len_tot_L:
                    for l in indexOrdered[key]:
                        if (l[0] == intersection[doc]):
                            vectors[doc][term] = l[1]
                            term += 1
                            test = 1
                            break
                    if(test == 0):
                        term += 1
            
            
            #normalizing vector: dividing each element by the norm of the vector  
            print('normalising vectors...')
            data_frame=[] #data frame for the clustering: list of lists
            for file in range(len(intersection)):
                    A = np.array(vectors[file])
                    norm = np.linalg.norm(A)
                    A = [elem/norm for elem in A]
                    data_frame.append(A)
            
            #converting the data_frame list of lists into a numpy array
            data_frame = np.array(data_frame) 
            
            #calling the kmeans clustering methodology
            kmeans = KMeans(n_clusters = k, init = 'random') # initialization
            kmeans.fit(data_frame)
            c = kmeans.predict(data_frame)
            
            print('start clustering...')
            
            for cluster in range(k):
                
                clusterList = []
                
                for i in range(len(c)):
                    if(c[i] == cluster):
                        clusterList.append(intersection[i])
                
                allLyrics = ''
                allArtistAndTitle = []
                
                for doc in clusterList:
                    #Result = db1.lyrics.find({'_id':doc},{'lyric':1, 'artist':1, 'title':1}) #2 in the DB is the id of inverted index dictionary
                    Result = db.lyrics.find({'_id':doc},{'lyric':1, 'artist':1, 'title':1}) #2 in the DB is the id of inverted index dictionary
                    for e in Result:
                        allLyrics  = (allLyrics +' '+normalise(e['lyric'])).strip()
                        allArtistAndTitle.append([e['artist'], e['title']])
                    
                print('\n-->> Cluster ',cluster+1,':')
                print('\nWordCloud of the most common words in the cluster:')
                plt.figure(figsize = (20,10))
                wordcloud = WordCloud(background_color = 'black', mode = 'RGB', width = 2000, height = 1000).generate(allLyrics)
                plt.title('Wordcloud of the most common words in the cluster')
                plt.imshow(wordcloud, interpolation="bilinear")
                plt.axis("off")
                plt.show()
                
                print('\nArtists and titles:')
                for i in allArtistAndTitle:
                    print(i[0],'-',i[1])
                
        else:
            print("\nInvalid input for k")

else:
    if (qt != '1' and qt != '2'):
        print('\nInvalid input: input should be 1 or 2')


elapsed_time = time.time() - start_time
print('...Operation compleated...')
print('Elapsed time: ', elapsed_time)