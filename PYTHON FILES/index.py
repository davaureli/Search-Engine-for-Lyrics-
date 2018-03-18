##here we implement the main inverted index

import time
start_time = time.time()

from pymongo import MongoClient
import nltk

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

'''

#we used multiple mlab dbs to avoid 0.5gb space limitation issue
#this is for online mongodb
server1 = 'ds119446.mlab.com'
server2 = 'ds119436.mlab.com'
port1 = 19446
port2 = 19436
db_name = 'hw3adm'
username = 'GROUP-17'
password = 'hw3-GROUP-17'

conn1 = MongoClient(server1, port1)
conn2 = MongoClient(server2, port2)
db1 = conn1[db_name]
db2 = conn2[db_name]
db1.authenticate(username, password)
db2.authenticate(username, password)
'''

#lista = db1.lyrics.find( {},{'lyric': 1} )
lista = db.lyrics.find( {},{'lyric': 1} )

dizTerms= {}
diz={}

Id = 1

#for each term, let's add a posting list document
for Docstring in lista:
    print ('working on document: ', Docstring['_id'])
    normalizedLyricList = normalise(Docstring['lyric']).split()
    for char in set(normalizedLyricList):
        if char not in diz:
            diz[char.lower()] = [[Id, normalizedLyricList.count(char)]]
        else:
            diz[char.lower()].append([Id, normalizedLyricList.count(char)])
            
    Id += 1    

#Creating the vocabulary document that contain all the terms
print ('Creating the vocabulary document that contain all the terms...')
for i in diz.keys():
    dizTerms[str(i)] = i

dizTerms['_id'] = 1

#removing collection index if exists
#db.index.drop()

#inserting the vocabulary document
#db2.index.insert_one(dizTerms)
db.index.insert_one(dizTerms)

#creating a list of documents that we are going to insert into the DB
DocList = []#documents list
termID = 2
for term in diz:
    print('Inserting into the documents list the term: ', termID-1)
    DocList.append({'_id':termID, term:diz[term]})
    termID += 1

print('Inserting dictionaries into DB...')
#db2.index.insert_many(DocList)
db.index.insert_many(DocList)

elapsed_time = time.time() - start_time
print('...Inverted index creation completed...')
print('Elapsed time: ', elapsed_time)
