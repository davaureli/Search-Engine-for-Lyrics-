#Second step: Parse the downloaded pages and extract the lyrics, artist, title, and the url of the song and store them in mongoDB

import time
start_time = time.time()

import os
from pymongo import MongoClient
from bs4 import BeautifulSoup


#This is for localmongodb
connection = MongoClient('localhost', 27017)
#connection.drop_database('HW3ADM') #drop database if already exists
db = connection.HW3ADM #creation or re-creation of the database called HW3ADM


'''
#this is for online mongodb
server = 'ds119446.mlab.com'
port = 19446
db_name = 'hw3adm'
username = 'GROUP-17'
password = 'hw3-GROUP-17'

conn = MongoClient(server, port)
db = conn[db_name]
db.authenticate(username, password)
'''

ID = 1

path = r''+os.getcwd()+'\..\lyrics_collection'

#removing collection lyrics if exists
#db.lyrics.drop()

DocList = []#documents list

for name in os.listdir(path):
    print("Working on Ducument: ",ID)
        
    f = open(path+'\\'+name, 'r', encoding="utf8")
    contents = f.read()
    f.close()
        
    if(len(contents) != 0):
        htmlpage = BeautifulSoup(contents, "html.parser")
            
        # parsing author, url, song etc and saving on mongoDB
        title_Author = list(htmlpage.find_all('span', attrs={'itemprop':'title'}))
            
        if len(title_Author) == 3:
            title = title_Author[2].get_text()
            Author = title_Author[1].get_text()
                
            div = list(htmlpage.find_all('div', attrs={'id':'content_h'}))
                
            if(len(div) != 0):
                lyric = div[0].get_text(' ')
                               
                for link in htmlpage.find_all('a'):
                    if link.get_text() == 'English':
                        url = 'https://www.azlyrics.com'+link.get('href') 
                        break
                
                # creating new document to insert in mongoDB for this song
                DocList.append({"_id":ID, "lyric":lyric, "artist":Author, "title":title, "url":url})
                ID += 1


#inserting all the songs in the mongoDB
db.lyrics.insert_many(DocList)

elapsed_time = time.time() - start_time
print('Insertion Compleated : ',ID,' Lyrics Inserted') 
print('Elapsed time: ', elapsed_time)                        
             