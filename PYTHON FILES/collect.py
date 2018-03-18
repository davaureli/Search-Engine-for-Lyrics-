##First step: let's collect all the html lyrics pages

import string
import time
import random
import requests
from bs4 import BeautifulSoup


#to fake as we are mozilla firefox
headers = { 'User-Agent': 'Mozilla/5.0 (Windows NT 6.0; WOW64; rv:24.0) Gecko/20100101 Firefox/24.0' }

alphabet = list(string.ascii_lowercase)
Number_of_songs = 0

# exploration by alphabetics letters
for c in alphabet:
    AUTHORS = []
    url = 'https://www.azlyrics.com/'+c+'.html'
    print('I am exploring', url)
    response = requests.get(url, headers=headers)
    soup = BeautifulSoup(response.text, "lxml")
    
    # getting all authors and saving them in a list
    for link in soup.find_all('a'):
        LinkURL = link.get('href') 
        if(LinkURL.startswith('a/')):
            AUTHORS.append(LinkURL)
    
    # exploring by authors
    for author in AUTHORS:
        print('Now on this author: ', author[2:-5])
        SONGSLIST = []
        response2 = requests.get('https://www.azlyrics.com/'+author, headers=headers)
        songs = BeautifulSoup(response2.text, "lxml")
    
        # getting all the songs of the author and saving them in a list
        for link2 in songs.find_all('a'):
            song = link2.get('href')
            if(song != None): 
                if(song.startswith('../lyrics/')): SONGSLIST.append(song)
    
        # exploring every song for dowloading the coresponding html page
        for s in SONGSLIST:
            
            # Stop dowloading songs if we have yet downloaded 31000 html pages
            if(Number_of_songs == 31000): break
            
            print('Downloading the song: ', s.split('/')[-1][:-5])
            response3 = requests.get('https://www.azlyrics.com'+s[2:], headers=headers)
            lyrics = BeautifulSoup(response3.text, "lxml")
    
            #creating the html file
            try:
                text = response3.text
                print('saved with name: ',s[3:].replace("/", "_"))
                f = open(r'./html pages2/'+s[3:].replace("/", "_"), 'w') 
                f.write(text)
                f.close()
                
                Number_of_songs += 1 # since we downloaded the song let's increment the number of downloaded songs
            
            except UnicodeEncodeError:
                pass          
            
            # Waiting for a random period of 1 - 2 seconds between downloading two pages
            time.sleep(random.randint(1,2))
            
        # Stop exploring authors if we have yet downloaded 31000 html pages    
        if(Number_of_songs == 31000): break
    
    # Stop exploring alphabet if we have yet downloaded 30000 html pages
    if(Number_of_songs == 31000): break

print('Download Compleated : ',Number_of_songs,' pages downloaded')


                