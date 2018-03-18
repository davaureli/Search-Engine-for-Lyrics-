##here we implement the inverted index tf-idf that we are going to use while searching

import time
start_time = time.time()

from pymongo import MongoClient
import math


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

#db.indexTfIdf.drop()

tfidfDocList = []

for i in INDEX:
    
    if (i['_id'] > 1):
        diz_Tf_Idf = i
        for k in diz_Tf_Idf.keys():
            if(k != '_id'):
                print ('Computing the weight of: ', k)
                idf = math.log10(N/len(diz_Tf_Idf[k]))
                for elem in diz_Tf_Idf[k]:
                    elem[1] *= idf
                
        #let's add diz_Tf_Idf into the doc list
        tfidfDocList.append(diz_Tf_Idf)

#let's add all the docs into the db
print('inserting td-idf\'s into the db...')

#db3.indexTfIdf.insert_many(tfidfDocList)
db.indexTfIdf.insert_many(tfidfDocList)

elapsed_time = time.time() - start_time
print('...Tf-Idf inverted index creation completed...')
print('Elapsed time: ', elapsed_time)