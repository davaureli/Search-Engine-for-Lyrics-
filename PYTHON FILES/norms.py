##here we implement the inverted index tf-idf that we are going to use wile searching

import time
start_time = time.time()

from pymongo import MongoClient


#This is for localmongodb
connection = MongoClient('localhost', 27017)
db = connection.HW3ADM #creation or re-creation of the database called HW3ADM
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

#INDEX = db2.index.find()
INDEX = db.index.find()

#N = db1.lyrics.find().count()
N = db.lyrics.find().count()

idfID = 1

#norms computation
normsDocList = []
   
norms = [0 for i in range(N)]

#TFIDF = db3.indexTfIdf.find()
TFIDF = db.indexTfIdf.find()

looper = 1
for diz_Tf_Idf in TFIDF:
    for w in diz_Tf_Idf.keys():
        print('On term: ', looper)
        if(w != '_id'):
            for l in diz_Tf_Idf[w]:
               norms[l[0]-1] += (l[1])**2
    looper += 1    
norms = [e**0.5 for e in norms]

for fileID in range(1, N+1):
    normsDocList.append({str(fileID):norms[fileID-1]})

#insertion into the DB
#db1.norms.insert_many(normsDocList)
db.norms.insert_many(normsDocList)


elapsed_time = time.time() - start_time
print('...norms computation completed...')
print('Elapsed time: ', elapsed_time)