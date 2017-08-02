#! python3
# dailyTracklist.py - scrapes tracks played yesterday on BBC 6Music from 7am-7pm and outputs a text file of the tracklist

import bs4, requests, datetime, os, pprint, pyperclip

# generate baseURL for yesterdays pages for example:  https://www.bbc.co.uk/music/tracks/find/6music/2017/07/15/7AM

# get yesterdays date and covert to tuple
yesterday = list((datetime.datetime.today() - datetime.timedelta(days=1)).timetuple())
# get year month day as strings
year = str(yesterday[0])
# as timetuplereturns single digit for month and day and URL needs double digit, check if month and day < 10 and if true add a leading 0
if yesterday[1] < 10:
	month = '0' + str(yesterday[1])
else:
	month = str(yesterday[1])
if yesterday[2] < 10:
	day = '0' + str(yesterday[2])
else:
	day = str(yesterday[2])
	
baseURL = 'https://www.bbc.co.uk/music/tracks/find/6music/' + year + '/' + month + '/' + day + '/'
	
# loop over webpages from 7am-7pm yesterday and request html source of tracks played page for yesterday at a certain time
print('Fetching track data for BBC6 music on ' + year + '/' + month + '/' + day + '...')
trackList= []

for i in ('7AM', '8AM', '9AM', '10AM', '11AM', '12PM', '1PM', '2PM', '3PM', '4PM', '5PM', '6PM'):
	res = requests.get(baseURL + i)
	res.raise_for_status()
	soup = bs4.BeautifulSoup(res.text, 'lxml')
	
# retrieve track and artist information
	tracks = soup.select('.music-track__title')
	artists = soup.select( '.music-track__artist')
	
# append to trackList
	for j in range(len(tracks)):
			trackList.append(artists[j].getText() + '-' + tracks[j].getText())
			

# strip whitespace from list items
stripList = []
for k in trackList:
	stripList.append(k.strip())

#copy to clipboard
pyperclip.copy(pprint.pformat(stripList, width=200))
print(str(len(stripList)) + ' tracks copied to clipboard')
print('Now paste into a new notepad++ window')
print("""Find: (\[)|(\])|(',)|(")|(,)|(\(.*\))|(\&.*-)""")
print("""Replace with: (?1 )(?2 )(?3 )(?4 )(?5 )(?6 )(?7-)""")
print("""Then find: ^..(.*.\\r\\n)""") # just the first 2 characters, gets the first apostrophe
print("""And replace with: \\1""")
print('Then copy that and import as a playlist on soundiiz.com')
print('Then run the deduplicator at: https://jmperezperez.com/spotify-dedup/')

'''	
# TODO convert list to string separated by newlines and write to txt file
textFile = open('C:\\Users\\Owner\\Downloads\\BBC.6Music.Tracklists.Archive\\' + year + '.' + month + '.' + day + '.txt', 'a')
for item in stripList:
	textFile.write('%s\n' % item.encode('ascii', 'ignore')) # deal with random characters that are in the list - THIS GIVES THE PROBLEM THAT TRACKNAMES ARE NOT INTERPRETED CORRECTLY BY SOUNDIIZ PLAYLIST MAKER
textFile.close()
'''

