# -*- coding: utf-8 -*-
try:
    from lib.ClientScraper import cfscraper, USER_AGENT
except ImportError:
    from ClientScraper import cfscraper, USER_AGENT
try:
    from lib.helper import *
except:
    from helper import *
import re

class VOD:
    def __init__(self):
        self.base = '\x68\x74\x74\x70\x73\x3a\x2f\x2f\x73\x75\x70\x65\x72\x66\x6c\x69\x78\x61\x70\x69\x2e\x64\x65\x76'

    def tvshows(self,imdb,season,episode):
        stream = ''
        try:
            if imdb and season and episode:
                url = '{0}/serie/{1}/{2}/{3}'.format(self.base,imdb,season,episode)
                parsed_url_r = urlparse(url)
                r_ = '{uri.scheme}://{uri.netloc}/'.format(uri=parsed_url_r)
                r = cfscraper.get(url)
                src = r.text
                soup = BeautifulSoup(src, 'html.parser')
                div = soup.find('div', class_='episodeOption active')
                data_contentid = div['data-contentid']
                api = '{0}/api'.format(self.base)
                r = cfscraper.post(api,data={'action': 'getOptions', 'contentid': data_contentid})
                src = r.json()
                id_ = src['data']['options'][0]['ID']
                r = cfscraper.post(api,data={'action': 'getPlayer', 'video_id': id_})
                src = r.json()
                video_url = src['data']['video_url']
                video_hash = video_url.split('/')[-1]
                parsed_url = urlparse(video_url)
                origin = '{uri.scheme}://{uri.netloc}'.format(uri=parsed_url)
                player = '{uri.scheme}://{uri.netloc}/player/index.php?data={0}&do=getVideo'.format(video_hash, uri=parsed_url)
                r = cfscraper.get(video_url, headers={'Referer': self.base + '/'})
                cookies_dict = r.cookies.get_dict()
                r = cfscraper.post(player,headers={'Origin': origin, 'x-requested-with': 'XMLHttpRequest'}, data={'hash': str(video_hash), 'r': r_}, cookies=cookies_dict)
                src = r.json()
                stream = src['videoSource'] + '|User-Agent=' + quote_plus(USER_AGENT)
        except:
            pass
        return stream
    
    def movie(self,imdb):
        stream = ''
        try:
            if imdb:
                url = '{0}/filme/{1}'.format(self.base,imdb)
                parsed_url_r = urlparse(url)
                r_ = '{uri.scheme}://{uri.netloc}/'.format(uri=parsed_url_r)
                r = cfscraper.get(url)
                src = r.text
                soup = BeautifulSoup(src, 'html.parser')
                div = soup.find('div',{'class': 'players_select'}) # dublado
                data_id = div.find('div', {'class': 'player_select_item'}).get('data-id', '')
                api = '{0}/api'.format(self.base)
                r = cfscraper.post(api,data={'action': 'getPlayer', 'video_id': data_id})
                src = r.json()
                video_url = src['data']['video_url']
                video_hash = video_url.split('/')[-1]
                parsed_url = urlparse(video_url)
                origin = '{uri.scheme}://{uri.netloc}'.format(uri=parsed_url)
                player = '{uri.scheme}://{uri.netloc}/player/index.php?data={0}&do=getVideo'.format(video_hash, uri=parsed_url)
                r = cfscraper.get(video_url, headers={'Referer': self.base + '/'})
                cookies_dict = r.cookies.get_dict()
                r = cfscraper.post(player,headers={'Origin': origin, 'x-requested-with': 'XMLHttpRequest'}, data={'hash': str(video_hash), 'r': r_}, cookies=cookies_dict)
                src = r.json()
                stream = src['videoSource'] + '|User-Agent=' + quote_plus(USER_AGENT)
        except:
            pass
        return stream

