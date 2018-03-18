import matplotlib.pyplot as plt
from pylab import figure
from pymongo import MongoClient
import nltk
import pprint
import operator


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




###First Query
print('\nIdentifying the artist with most songs...')
AuthorDict = {}

artists = db.lyrics.find( {},{ '_id':0, 'artist': 1 } )
artistsl = []
for i in artists:
    artistsl.append(i['artist'])
for i in set(artistsl):
    AuthorDict[i] = artistsl.count(i)

Authors = sorted(AuthorDict.items(), key = operator.itemgetter(1), reverse = True)
print('The artist with most song is: ', Authors[0][0], ' with ', Authors[0][1], ' songs...')

print('Generating the bar graph of the number of songs per Artist...')

# this is the  histogram of the number of songs per Artist
values = [x[1] for x in Authors]
fig=figure(figsize=(20,10))
barlist = plt.bar(range(len(Authors)),values, color = 'c')
plt.title('Number of songs per Artist')
plt.xlabel("Artists")
plt.ylabel("Number of songs")
cathegorie = [y[0] for y in Authors]
plt.xticks(range(len(Authors)), cathegorie, rotation='vertical')
barlist[0].set_color('g')
plt.savefig('number_of_songs_per_Artist.png', dpi = 300)
plt.show()

#let's zoom on the 50 first songs
print('\nZooming on the first 50...')

values = [x[1] for x in Authors]
fig=figure(figsize=(20,10))
barlist = plt.bar(range(len(values[:50])),values[:50], color = 'c')
plt.title('Number of songs per Artist: first 50')
plt.xlabel("Artists")
plt.ylabel("Number of songs")
cathegorie = [y[0] for y in Authors]
plt.xticks(range(len(cathegorie[:50])), cathegorie[:50], rotation='vertical')
barlist[0].set_color('g')
plt.savefig('firt_50_number_of_songs_per_Artist.png', dpi = 300)
plt.show()

#let's zoom on the 50 last songs
print('\nZooming on the last 50...')

values = [x[1] for x in Authors]
fig=figure(figsize=(20,10))
barlist = plt.bar(range(len(values[-50:])),values[-50:], color = 'c')
plt.title('Number of songs per Artist: last 50')
plt.xlabel("Artists")
plt.ylabel("Number of songs")
cathegorie = [y[0] for y in Authors]
plt.xticks(range(len(cathegorie[-50:])), cathegorie[-50:], rotation='vertical')
plt.savefig('last_50_number_of_songs_per_Artist.png', dpi = 300)
plt.show()





###Second query

print('\nSelecting the 20 most popular words (excluding stopwords)...')

wordsDict = {}

#select all the lyrics from the mongoDB database
lyrics = db.lyrics.find( {},{ '_id':0, 'lyric': 1 } )

#put all the lyrics in a list
lyricsl = []
for i in lyrics:
    lyricsl.append(i['lyric'])
    
#for every song lyric
for i in lyricsl:
    # removing all the stopwords from the lyric i
    iNoStop = normalise(i)
    
    #updating the dictionary containing all the words
    for p in iNoStop.split():
        if(p in wordsDict.keys()):
            wordsDict[p] += 1
        else:
            wordsDict[p] = 1
                        

# this return the 20 most popular words (excluding stopwords)
first20 = sorted(wordsDict.items(), key = operator.itemgetter(1), reverse = True)[:20]
print('20 most popular words (exclude stopwords): ')
pprint.pprint(first20)

print('Generating the histogram of the 20 most popular words (excluding stopwords)...')
# this is the  histogram of the number of occurence per word for the 20 most popular words
values2 = [x[1] for x in first20]
fig=figure(figsize=(20,10))
barlist2 = plt.bar(range(len(first20)),values2, color = 'c')
plt.title('Number of occurence per word for the 20 most popular words')
plt.xlabel("Words")
plt.ylabel("Number of occurence")
cathegorie2 = [y[0] for y in first20]
plt.xticks(range(len(first20)), cathegorie2)
barlist[0].set_color('g')
plt.savefig('Number_of_occurence_per_word_for_the_20_most_popular_words.png', dpi = 300)
plt.show()









###third query
print('\nSelecting the 10 most common singer names...')
nameDict = {}

for artist in list(AuthorDict.keys()):
    ##let's normalise the artist name
    artistNoStop = normalise(artist)
    
    for name in artistNoStop.split():
        if name.lower() in nameDict.keys():
            nameDict[name.lower()] += 1
        else:
            nameDict[name.lower()] = 1

# this return the 10 most common singer names          
first10 = sorted(nameDict.items(), key = operator.itemgetter(1), reverse = True)[:10]
print('The 10 most common singer names: ')
pprint.pprint(first10)

#lets visualise the number of songs of those to see whether they tend to publish more songs than others

first10w = set(dict(first10).keys())
PopularNamesDict = {}

sumOfSongsPopularName = 0
numberOfArtistPopularName = 0
sumOfSongsNotPopularName = 0
numberOfArtistNotPopularName = 0

for artist in Authors:
    t = 0
    for p in first10w:
        if p in [x.lower() for x in artist[0].split()]:
            sumOfSongsPopularName += artist[1]
            numberOfArtistPopularName += 1
            t = 1
            break
    if (t == 0):
        sumOfSongsNotPopularName += artist[1]
        numberOfArtistNotPopularName += 1

PopularNamesDict['Artists having top 10 names'] = sumOfSongsPopularName / numberOfArtistPopularName
PopularNamesDict['Others'] = sumOfSongsNotPopularName / numberOfArtistNotPopularName

PopularNames = sorted(PopularNamesDict.items(), key = operator.itemgetter(1), reverse = True)
values3 = [x[1] for x in PopularNames]
fig=figure(figsize=(15,10))
barlist3 = plt.bar(range(len(PopularNames)),values3, color = 'c')
plt.title('Average number of songs for artists having popular names vs Average number of songs for others')
plt.xlabel("Cathegories")
plt.ylabel("Average number of songs")
cathegorie3 = [y[0] for y in PopularNames]
plt.xticks(range(len(PopularNames)), cathegorie3)

#now let's give the green color to those with name in the top 10 most popular name
barlist3[0].set_color('g')
plt.savefig('Average number of songs for artists having popular names vs Average number of songs for others.png', dpi = 300)

plt.show()








###fourth query
print('Creating the bar graph of song lengths...')

lenDict = {}

lyrics_title = db.lyrics.find( {},{ '_id':0, 'lyric': 1, 'title':1 } )

for i in lyrics_title:
    lenDict[i['title'].replace('$', '')] = len(i['lyric'].split()) #removing $ sign from the title cause it's consider as the eof.
    
lens = sorted(lenDict.items(), key = operator.itemgetter(1), reverse = True)
values4 = [x[1] for x in lens]
fig=figure(figsize=(20,5))
barlist4 = plt.bar(range(len(lens)),values4, color = 'c')
plt.title('Song lengths')
plt.xlabel("Songs")
plt.ylabel("Lengths")
cathegorie4 = [y[0] for y in lens]
plt.xticks(range(len(lens)), cathegorie4, rotation='vertical')

plt.savefig('Song lengths.png', dpi = 300)
plt.show()

#let's zoom on the 50 first longest songs
print('\nZooming on the first 50...')

fig=figure(figsize=(20,5))
barlist4 = plt.bar(range(len(lens[:50])),values4[:50], color = 'c')
plt.title('Song lengths')
plt.xlabel("Songs")
plt.ylabel("Lengths")
cathegorie4 = [y[0] for y in lens[:50]]
plt.xticks(range(len(lens[:50])), cathegorie4[:50], rotation='vertical')

plt.savefig('zoom on the 50 first Song lengths.png', dpi = 300)
plt.show()

