# -*- coding: utf-8 -*-

""" Plexus (c)  2015 enen92

    This file contains web utilities
    
    Classes:
    
    download_tools() -> Contains a downloader, a extraction function and a remove function
    
    Functions:
    
    get_page_source -> Get a webpage source code through urllib_request
    mechanize_browser(url) -> Get a webpage source code through mechanize module. To avoid DDOS protections.
    makeRequest(url, headers=None) -> check if a page is up and retrieve its source code
    clean(text) -> Remove specific characters from the page source
    url_isup(url, headers=None) -> Check if url is up. Returns True or False.
   	
"""

import gzip
import os
import re
import sys
import tarfile

import xbmc
import xbmcgui

from six.moves import StringIO
from six.moves import urllib_request


user_agent = 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/74.0.3729.169 Safari/537.36'


class download_tools():

    def Downloader(self, url, dest, description, heading):
        dp = xbmcgui.DialogProgress()
        dp.create(heading, description, '')
        dp.update(0)
        urllib_request.urlretrieve(url, dest, lambda nb, bs, fs, url=url: self._pbhook(nb, bs, fs, dp))

    def _pbhook(self, numblocks, blocksize, filesize, dp=None):
        try:
            percent = int(
                (int(numblocks) * int(blocksize) * 100) / int(filesize))
            dp.update(percent)
        except:
            percent = 100
            dp.update(percent)
        if dp.iscanceled():
            dp.close()

    def extract(self, file_tar, destination):
        dp = xbmcgui.DialogProgress()
        dp.create(translate(30000), translate(30023))
        tar = tarfile.open(file_tar)
        tar.extractall(destination)
        dp.update(100)
        tar.close()
        dp.close()

    def remove(self, file_):
        dp = xbmcgui.DialogProgress()
        dp.create(translate(30000), translate(30024))
        os.remove(file_)
        dp.update(100)
        dp.close()


def get_page_source(url):
    req = urllib_request.Request(url)
    req.add_header('User-Agent', user_agent)
    response = urllib_request.urlopen(req)
    if response.info().get('Content-Encoding') == 'gzip':
        buf = StringIO(response.read())
        f = gzip.GzipFile(fileobj=buf)
        link = f.read()
    else:
        link = response.read()
    response.close()
    return link


def makeRequest(url, headers=None):
    try:
        if not headers:
            headers = {'User-agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/74.0.3729.169 Safari/537.36'}
        req = urllib_request.Request(url, None, headers)
        response = urllib_request.urlopen(req)
        data = response.read()
        response.close()
        return data
    except:
        sys.exit(0)


def url_isup(url, headers=None):
    try:
        if not headers:
            headers = {'User-agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/74.0.3729.169 Safari/537.36'}
        req = urllib_request.Request(url, None, headers)
        response = urllib_request.urlopen(req)
        data = response.read()
        response.close()
        return True
    except:
        return False


def clean(text):
    command = {'\r': '', '\n': '', '\t': '', '&nbsp;': ' ', '&quot;': '"', '&#039;': '', '&#39;': "'", '&#227;': '?', '&170;': '?', '&#233;': '?', '&#231;': '?', '&#243;': '?', '&#226;': '?', '&ntilde;': '?',
               '&#225;': '?', '&#237;': '?', '&#245;': '?', '&#201;': '?', '&#250;': '?', '&amp;': '&', '&#193;': '?', '&#195;': '?', '&#202;': '?', '&#199;': '?', '&#211;': '?', '&#213;': '?', '&#212;': '?', '&#218;': '?'}
    regex = re.compile("|".join(map(re.escape, command.keys())))
    return regex.sub(lambda mo: command[mo.group(0)], text)
