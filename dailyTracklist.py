#! python3
# dailyTracklist.py - scrapes tracks played yesterday on BBC 6Music from 7am-7pm and outputs a text file of the tracklist

import bs4, requests, datetime, os, pyperclip, re

# generate baseURL for yesterday's pages for example:  https://www.bbc.co.uk/music/tracks/find/6music/2017/07/15/7AM

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
print('Fetching track data played on BBC 6Music between 7AM and 7PM yesterday: ' + year + '/' + month + '/' + day + '...')
trackList= []

for i in ('7AM', '8AM', '9AM', '10AM', '11AM', '12PM', '1PM', '2PM', '3PM', '4PM', '5PM', '6PM'):
	res = requests.get(baseURL + i)
	res.raise_for_status()
	soup = bs4.BeautifulSoup(res.text, 'lxml')
	
# retrieve track and artist information
	tracks = soup.select('.music-track__title')
	artists = soup.select( '.music-track__artist')
	
# append to trackList
print('Removing duplicates...')
	for j in range(len(tracks)):
		if artists[j].getText() + '-' + tracks[j].getText() not in trackList: # check for duplicates
			trackList.append(artists[j].getText() + '-' + tracks[j].getText())
			
# strip whitespace from list items
print('Stripping whitespace...')
stripList = []
for k in trackList:
	stripList.append(k.strip())

# convert list to string separated by newlines and write to txt file
print('Adding to file: C:\\Users\\Owner\\Downloads\\BBC.6Music.Tracklists.Archive\\' + year + '.' + month + '.' + day + '.txt...')
textFile = open('C:\\Users\\Owner\\Downloads\\BBC.6Music.Tracklists.Archive\\' + year + '.' + month + '.' + day + '.txt', 'w', encoding='utf8')
for item in stripList:
	textFile.write('%s\n' % item)
textFile.close()

# open the text file to remove some problematic parts of text
file = open('C:\\Users\\Owner\\Downloads\\BBC.6Music.Tracklists.Archive\\' + year + '.' + month + '.' + day + '.txt', 'r', encoding='utf8').read()
print('Cleaning list ready for upload...')
file = re.sub(r'\(.*\)', '', file) # anything in parentheses
file = re.sub(r'\&.*-', '-', file) # anything with & in the artist
file = re.sub(r'\nthe\sxx.*','', file, flags=re.I) # anything by the xx :(
file = re.sub(r'\ntricky\s-\sthe\sonly\sway','', file, flags=re.I) # other rubbish
# copy to clipboard (TODO upload to soundiiz.com)
pyperclip.copy(file)
print(str(len(stripList)) + ' tracks copied to clipboard')

# instruct user on next step
print('Now you can import a new playlist on soundiiz.com\n\nEnjoy a new playlist every day with 6Music Daily Tracklist!')