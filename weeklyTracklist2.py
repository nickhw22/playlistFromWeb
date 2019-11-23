#! python3
# weeklyTracklist2 - BBC sounds website has moved where the tracklist for the shows are
# each show for each day is on its own page and there is no logical URL make it easy

import bs4, requests, datetime, os, pyperclip, re

#loop over pages for M-F in the last week
for z in (5,4,3,2,1): # if you are making the list on a saturday
#for z in (6,5,4,3,2): # if you are making the list on a sunday
    # generate URL for the day  for example: https://www.bbc.co.uk/schedules/p00fzl65/2019/06/06
    # get days date and covert to tuple
    date = list((datetime.datetime.today() - datetime.timedelta(days=z)).timetuple())
    # get year month day as strings
    year = str(date[0])
    # as timetuple returns single digit for month and day and URL needs double digit, check if month and day < 10 and if true add a leading 0
    if date[1] < 10:
        month = '0' + str(date[1])
    else:
        month = str(date[1])
    if date[2] < 10:
        day = '0' + str(date[2])
    else:
	    day = str(date[2])

    print('Fetching artist & title data for tracks played on\nBBC 6Music, 5AM-7PM, ' + year + '/' + month + '/' + day + '...')

    # first make a list of URLs of each show on that day by scraping the dayURL page
    dayURL = 'https://www.bbc.co.uk/schedules/p00fzl65/' + year + '/' + month + '/' + day
    res = requests.get(dayURL)
    res.raise_for_status()
    soup = bs4.BeautifulSoup(res.text, 'lxml')
    shows = soup.select('.programme__titles')
    # the class programme__titles contains this:
    # <a href="https://www.bbc.co.uk/programmes/m0005l7h" class="br-blocklink__link block-link__target" data-linktrack="programmeobjectlink=title" aria-label="31 May 05:00: Chris Hawkins, Jon Hillcock sits in"> plus a bit more we don't want
    # loop through all shows on that day and put the URL into a list called showList based on the time of the show
    showList = []
    trackList = []
    for show in shows:
        show = str(show)
        showURL = re.sub(r'.*href="', '', show)
        showURL = re.sub(r'".*', '', showURL)
        showTime = re.sub(r'.*"\d{1,2}\s\w{3}\s', '', show)
        showTime = re.sub(r':\w{2}:.*', '', showTime)
        if int(showTime) >= 5 and int(showTime) <= 16: # shows starting between 5AM and 4PM
            showList.append(showURL)
        else:
            continue

    #del showList[-1] # the page shows up to 5AM the next day but we don't want to include that show in the current day
    
    # loop through all the show pages on that day and extract artist and track data and add to trackList
    for theShow in showList:
        res = requests.get(str(theShow))
        res.raise_for_status()
        soup = bs4.BeautifulSoup(res.text, 'lxml')
        # retrieve track and artist information. There is a problem where multiple artists can be split up into several spans so they will need to be stuck together - getText should solve this but there are newlines between the artists that were in multiple spans
        tracks = soup.select('p.no-margin > span') # if the track is 'feat.' some artist this span will show up as another track
        artists = soup.select('h3.gamma.no-margin')

        # tidy up the tracks to remove the 'feat. xxx' parts
        tracks2 = []
        for i in range(len(tracks)): 
            tracks2.append(str(tracks[i])) # make a list of strings
        tracks3 =[]
        for i in range(len(tracks2)):
            tracks3.append(re.sub(r'<span\sc.*n>', '', tracks2[i])) # delete strings containing <span class='artist'...
        tracks4 = list(filter(None, tracks3)) # remove empty list items left from previous step
        tracks5 = []
        for i in range(len(tracks4)):
            tracks5.append(re.sub(r'<span>', '', tracks4[i]))
        tracks6 = []
        for i in range(len(tracks5)):
            tracks6.append(re.sub(r'</span>', '', tracks5[i]))
        
        # sometimes the artists list can start with 'Choose your file' this has to be removed
        artists2 = []
        for i in range(len(artists)):
            artists2.append(artists[i].getText()) # convert from bs4 object to list of strings

        if 'Choose your file' in artists2[0]:
            artists2 = artists2[1:]

        # append to trackList     
        for j in range(len(tracks6)):
            try:
                if artists2[j] + '-' + tracks6[j] not in trackList: # check for duplicates
                    trackList.append(artists2[j] + '-' + tracks6[j])
            except IndexError:
                continue
            '''try: # to find issues
                print(artists2[j] + '-' + tracks6[j]) 
            except UnicodeEncodeError:
                print('UnicodeEncodeError')'''

    # strip whitespace, newlines, and amp;s from list items
    print('Stripping whitespace, newlines, and amp;s...')
    stripList = []
    for k in trackList:
    	stripList.append(k.strip())
    stripList2 = []
    for i in range(len(stripList)):
        stripList2.append(re.sub(r'\n', '', stripList[i]))
    stripList3 = []
    for i in range(len(stripList2)):
        stripList3.append(re.sub(r'amp;', '', stripList2[i]))
    stripList4 = []
    for i in range(len(stripList3)):
        stripList4.append(re.sub(r'-', ' - ', stripList3[i]))
    
    # convert list to string separated by newlines and write to txt file
    print('Adding to file: Downloads\\BBC.6Music.Tracklists.Archive\\' + year + '.' + month + '.' + day + '.txt...')
    textFile = open('C:\\Users\\Owner\\Downloads\\BBC.6Music.Tracklists.Archive\\' + year + '.' + month + '.' + day + '.txt', 'w', encoding='utf8')
    for item in stripList4:
    	textFile.write('%s\n' % item)
    textFile.close()

    # open the text file to remove some problematic parts of text
    file = open('C:\\Users\\Owner\\Downloads\\BBC.6Music.Tracklists.Archive\\' + year + '.' + month + '.' + day + '.txt', 'r', encoding='utf8').read()
    print('Cleaning list ready for clipboard...')
    file = re.sub(r'\(.*\)', '', file) # delete anything in parentheses
    file = re.sub(r'\&.*-', '-', file) # delete anything after & in the artist part

    # artists I don't want in the playlist
    file = re.sub(r'\nthe\sxx.*','', file, flags=re.I) # anything by the xx :(
    file = re.sub(r'\ntricky.*','', file, flags=re.I) # anything by tricky
    file = re.sub(r'\nrostam.*','', file, flags=re.I) # anything by rostam
    file = re.sub(r'\nm\.?i\.?a\.?.*','', file, flags=re.I) # anything by m.i.a.
    file = re.sub(r'\njamie\sxx.*','', file, flags=re.I) # anything by jamie xx
    file = re.sub(r'\nsigur.*','', file, flags=re.I) # anything by sigur ros
    file = re.sub(r'\nloyle\scarner.*','', file, flags=re.I) # anything by loyle carner
    file = re.sub(r'\nprincess\snokia.*','', file, flags=re.I) # anything by princess nokia
    file = re.sub(r'\nrapsody.*','', file, flags=re.I) # anything by rapsody
    file = re.sub(r'\ntune\s-\syards.*','', file, flags=re.I) # anything by tune-yards
    file = re.sub(r'\nriton.*', '', file, flags=re.I) # anything by riton
    file = re.sub(r'\nsantigold.*', '', file, flags=re.I) # anything by santigold
    file = re.sub(r'\nlittle\ssimz.*', '', file, flags=re.I) # etc
    file = re.sub(r'\nkate\stempest.*', '', file, flags=re.I)
    file = re.sub(r'\nsquid.*', '', file, flags=re.I)
    file = re.sub(r'\nblack\scountry,\snew\sroad.*', '', file, flags=re.I)
    file = re.sub(r'\nblack\smidi.*', '', file, flags=re.I)
    file = re.sub(r'\nVeruca\sSalt.*', '', file, flags=re.I)
    file = re.sub(r'\nslowthai.*', '', file, flags=re.I)
    file = re.sub(r'\nKim\sGordon.*', '', file, flags=re.I)

    # so spotify will recognise
    file = re.sub(r'6\sMusic\sLive.*','', file, flags=re.I)
    file = re.sub(r'\nN\*E\*R\*D.*','\nN.E.R.D', file, flags=re.I)
    file = re.sub(r'\nMaxïmo\sPark','\nMaximo Park', file, flags=re.I)
    file = re.sub(r'My\skeys\syour\sboyfriend', 'MY KZ, UR BF', file, flags=re.I)
    file = re.sub(r'\nEx:Re','\nEx Re', file, flags=re.I)
    file = re.sub(r'Girls\swho\splay\sguitars','Girls who play guitar', file, flags=re.I)
    file = re.sub(r'\nO\.D\.B\.','\nOl\' Dirty Bastard', file, flags=re.I)
    file = re.sub(r'\nSuper\sFurry\sAnimals\s-\sSomething\sfor\sthe\sweekend','\nSuper Furry Animals - Something 4 the weekend', file, flags=re.I)
    file = re.sub(r'\nThe\sPretenders\s-\sPrivate\sLife','\nThe Pretenders - Private Life (live)', file, flags=re.I)
    file = re.sub(r'Activ\s8*','Activ 8 (Come with me)', file, flags=re.I)
    file = re.sub(r'\nJAY\s-\sZ','\nJay Z', file, flags=re.I)
    file = re.sub(r'Yazoo\s-\sSituation*','Yazoo - Situation 12" Remix', file, flags=re.I)
    file = re.sub(r'Mungo\'s\sHi\sFi.*-', 'Mungo\'s Hi Fi -', file, flags=re.I)
    file = re.sub(r'Pink\sFloyd\s-\sAnother\sBrick\sIn\sThe\sWall,\sPart\s2', 'Pink Floyd - Another Brick In The Wall, Pt.2', file, flags=re.I)

    # copy to clipboard
    pyperclip.copy(file)
    print('Copying ' + str(len(stripList)) + ' tracks to clipboard...')
    print('BBC6 ' + day + '.' + month + '.' + year[2:] + '...done!\n')
	
# instruct user on next step
print('Now you can import these new playlists on soundiiz.com\n\nEnjoy a new playlist every day with 6Music Daily Tracklist!\nThanks for using!\n')