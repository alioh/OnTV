# -*- coding: utf-8 -*-
#   OnTV V1.0 .
#   currently dead, OSN updated the website.
#   Contact: @alioh or @3laAlTV
#   https://twitter.com/3laaltv
#   3laaltv at gmail dot com

from bs4 import BeautifulSoup
import requests
from twython import Twython
from twython import TwythonError
import time
import datetime 
import omdb
import xmltodict

#   Channels
#   "Now Playing": "", "NP Year": "", "NP Rate": "", "NP Genre": "", "NP Actors": "", "Next Movie": "",
#   "Next Movie Time":"", "NM Year": "", "NM Rate": "", "NM Genre": "", "NM Actors": "", "NM Runtime": ""
osn = "http://www.osn.com/en-sa/explore/channels"
osn_channels = {'Comedy ' : { "link": "http://www.osn.com/en-sa/explore/channels/cce/comedy-central", "Now Playing": "", "type": "Series"}
                }

#   Twitter Secrets
CONSUMER_KEY = ''
CONSUMER_SECRET = ''
ACCESS_TOKEN = ''
ACCESS_SECRET = ''
twitter = Twython(CONSUMER_KEY, CONSUMER_SECRET, ACCESS_TOKEN, ACCESS_SECRET)

#   Emotes
# time_emote = "\u23f2".encode('utf-16', 'surrogatepass').decode('utf-16')
# channel_emote = "\ud83d\udcfa".encode('utf-16', 'surrogatepass').decode('utf-16')
# title_emote = "\ud83c\udfa5".encode('utf-16', 'surrogatepass').decode('utf-16')
# length_emote = "\u23f3".encode('utf-16', 'surrogatepass').decode('utf-16')
now_playing_emote = "\u25b6\ufe0f".encode('utf-16', 'surrogatepass').decode('utf-16')
next_emote = "\u23ed".encode('utf-16', 'surrogatepass').decode('utf-16')

#   omdbapi
#   Using OMDb API to get movies details
def get_movie_details(movie):
    dict_details = {}
    run = True
    while run:
        try:
            res = omdb.request(t=movie, apikey='' ,r='xml')
            xml_content = res.content
            to_dict = dict(xmltodict.parse(xml_content)['root']['movie'])
            dict_details = [to_dict['@year'], to_dict['@imdbRating'], to_dict['@genre'].split(',')[0], to_dict['@actors'].split(',')[:2], to_dict['@runtime']]
            run = False
        except Exception as e:
            run = False
            continue
        return dict_details

def get_movies(channel, page):
    page_response = requests.get(page)
    page_content = BeautifulSoup(page_response.content, "html.parser")

    #   Get next movie time
    movies_time = page_content.find('ul', attrs={'class':'nav nav-tabs'})
    movies_time = movies_time.find_all('li')
    print(movies_time)
    exit()
    osn_channels[channel]["Next Time"] = movies_time[1].contents[0].text

    #   Get movies titles
    movies_title = page_content.find_all('div', attrs={'class':'tsDetails'})
    series_title = page_content.find_all('div', attrs={'class':'theshow'})

    for c in osn_channels:
        if movies_title[0].contents[1].text == osn_channels[c]['Now Playing']:
            tweet = ''
            continue
        else:
            tweet = ''
            tweet += '{} Now Playing on {}:'.format(now_playing_emote, channel)
            osn_channels[channel]['Now Playing'] = movies_title[0].contents[1].text
            movie_details = get_movie_details(osn_channels[channel]['Now Playing'])
            if movie_details == None:
                osn_channels[channel]["NP Year"] = ''
                osn_channels[channel]["NP Rate"] = ''
                osn_channels[channel]["NP Genre"] = ''
                osn_channels[channel]["NP Actors"] = ''
                tweet += '\n{} '.format(osn_channels[channel]['Now Playing'])
            else:
                osn_channels[channel]["NP Year"] = movie_details[0]
                osn_channels[channel]["NP Rate"] = movie_details[1]
                osn_channels[channel]["NP Genre"] = movie_details[2]
                if len(movie_details[3]) == 1:
                    osn_channels[channel]["NP Actors"] = movie_details[3][0]
                else:
                    osn_channels[channel]["NP Actors"] = movie_details[3][0] + "," + movie_details[3][1]
                tweet += '\n{} '.format(osn_channels[channel]['Now Playing'])
            if osn_channels[channel]['type'] == "Series":
                temp = series_title[0].text.split()
                season_eps = []
                if "Season" in temp:
                    for i in temp:
                        if i.isdigit():
                            season_eps.append(i)
                        else:
                            pass  
                    osn_channels[channel]['Season'] = season_eps[0]
                    osn_channels[channel]['Episode'] = season_eps[1]
                    tweet += 'S{}E{} '.format(osn_channels[channel]['Season'], osn_channels[channel]['Episode'])  
                    if movie_details != None:
                        tweet += 'IMDB: {}'.format(osn_channels[channel]['NP Rate'])
                        tweet += '\nStarring: {}'.format(osn_channels[channel]['NP Actors'])   
                    else:
                        pass
                else:
                    if movie_details != None:
                        tweet += 'IMDB: {}'.format(osn_channels[channel]['NP Rate'])
                        tweet += '\nStarring: {}'.format(osn_channels[channel]['NP Actors'])
                    else:
                        pass
            else:
                if movie_details != None:
                        tweet += 'IMDB: {}'.format(osn_channels[channel]['NP Rate'])
                        tweet += '\nStarring: {}'.format(osn_channels[channel]['NP Actors'])  
                else:
                    tweet += '({}) '.format(osn_channels[channel]['NP Year'])
                    tweet += 'IMDB: {}'.format(osn_channels[channel]['NP Rate'])
                    tweet += '\nStarring: {}'.format(osn_channels[channel]['NP Actors'])
            tweet += '\n{} Next @ {} KSA:'.format(next_emote, osn_channels[channel]['Next Time'])
            osn_channels[channel]['Next'] = movies_title[1].contents[1].text
            movie_details = get_movie_details(osn_channels[channel]['Next'])
            if movie_details == None:
                osn_channels[channel]["NM Year"] = ''
                osn_channels[channel]["NM Rate"] = ''
                osn_channels[channel]["NM Genre"] = ''
                osn_channels[channel]["NM Actors"] = ''
                osn_channels[channel]['NM Runtime'] = ''
                tweet += '\n{} '.format(osn_channels[channel]['Next'])
            else:
                osn_channels[channel]["NM Year"] = movie_details[0]
                osn_channels[channel]["NM Rate"] = movie_details[1]
                osn_channels[channel]["NM Genre"] = movie_details[2]
                if len(movie_details[3]) == 1:
                    osn_channels[channel]["NM Actors"] = movie_details[3][0]
                else:
                    osn_channels[channel]["NM Actors"] = movie_details[3][0] + "," + movie_details[3][1]
                osn_channels[channel]['NM Runtime'] = movie_details[4]
                tweet += '\n{} '.format(osn_channels[channel]['Next'])
                if osn_channels[channel]['type'] == "Series":
                    temp = series_title[1].text.split()
                    season_eps = []
                    if "Season" in temp:
                        for i in temp:
                            if i.isdigit():
                                season_eps.append(i)
                            else:
                                pass  
                        osn_channels[channel]['Season'] = season_eps[0]
                        osn_channels[channel]['Episode'] = season_eps[1]
                        tweet += 'S{}E{} '.format(osn_channels[channel]['Season'], osn_channels[channel]['Episode'])  
                        if movie_details != None:
                            tweet += 'IMDB: {}'.format(osn_channels[channel]['NM Rate'])
                            tweet += '\nStarring: {}'.format(osn_channels[channel]['NM Actors'])   
                        else:
                            pass
                    else:
                        if movie_details != None:
                            tweet += 'IMDB: {}'.format(osn_channels[channel]['NM Rate'])
                            tweet += '\nStarring: {}'.format(osn_channels[channel]['NM Actors'])   
                        else:
                            pass
                else:
                    if movie_details != None:
                        tweet += 'IMDB: {}'.format(osn_channels[channel]['NM Rate'])
                        tweet += '\nStarring: {}'.format(osn_channels[channel]['NM Actors'])   
                    else:
                        tweet += '({}) '.format(osn_channels[channel]['NM Year'])
                        tweet += 'IMDB: {}'.format(osn_channels[channel]['NM Rate'])
                        tweet += '\nStarring: {}'.format(osn_channels[channel]['NM Actors'])
        return tweet
tweets = []

def main_fun():
    for k in osn_channels:
        tweet = get_movies(k, osn_channels[k]['link'])
        try: 
            tweet = get_movies(k, osn_channels[k]['link'])
            time.sleep(15)
            if tweet in tweets:
                continue
            else:
                tweets.append(tweet)
                twitter.update_status(status=tweet)
                print('tweet sent @ {}'.format(datetime.datetime.now()))
        except Exception as e:
            e
            continue
    time.sleep(180)

while True:
    main_fun()