# -*- coding: utf-8 -*-

import sys

if sys.version_info[0] < 3:
    import cookielib

    import urllib
    import urllib2
else:
    import http.cookiejar as cookielib

    import urllib as urllib2
    import urllib.error as urllib2
    import urllib.parse as urllib
    import urllib.request as urllib2


import os, re, socket, json

from authorization import authorization

from core import scrapertools
from platformcode import config, logger


class gdrive(object):
    API_URL = 'https://www.googleapis.com/drive/v3/'

    def __init__(self, instanceName, authenticate=True):
        self.instanceName = instanceName

        username = self.getInstanceSetting('username', default='')
        self.authorization = authorization(username)

        self.cookiejar = cookielib.CookieJar()

        self.user_agent = ''

        if (authenticate == True and (not self.authorization.loadToken(self.instanceName, 'auth_access_token') or not self.authorization.loadToken(self.instanceName, 'auth_refresh_token'))):
            if self.getInstanceSetting('code'):
                self.getToken(self.getInstanceSetting('code'))
            else:
                logger.error('Faltan datos en GDrive!')

    def getToken(self, code):
            header = { 'User-Agent' : self.user_agent }

            url = 'https://accounts.google.com/o/oauth2/token'
            clientID = self.getInstanceSetting('client_id')
            clientSecret = self.getInstanceSetting('client_secret')
            header = {'User-Agent' : self.user_agent , 'Content-Type': 'application/x-www-form-urlencoded'}

            req = urllib2.Request(url, 'code=' + str(code) + '&client_id=' + str(clientID) + '&client_secret=' + str(clientSecret) + '&redirect_uri=urn:ietf:wg:oauth:2.0:oob&grant_type=authorization_code', header)

            try:
                response = urllib2.urlopen(req)
            except urllib2.URLError as e:
                if e.code == 403:
                    logger.error('Login information is incorrect or permission is denied (403)')
                else:
                    logger.error('Login information is incorrect or permission is denied')
                return

            response_data = response.read()
            response.close()

            for r in re.finditer('\"access_token\"\s?\:\s?\"([^\"]+)\".+?\"refresh_token\"\s?\:\s?\"([^\"]+)\".+?', response_data, re.DOTALL):
                accessToken,refreshToken = r.groups()
                self.authorization.setToken('auth_access_token',accessToken)
                self.authorization.setToken('auth_refresh_token',refreshToken)
                self.updateAuthorization()

            for r in re.finditer('\"error_description\"\s?\:\s?\"([^\"]+)\"', response_data, re.DOTALL):
                errorMessage = r.group(1)
                logger.error('The following login error was encountered:')
                logger.error(errorMessage)

            return

    def refreshToken(self):
            header = { 'User-Agent' : self.user_agent }

            url = 'https://accounts.google.com/o/oauth2/token'
            clientID = self.getInstanceSetting('client_id')
            clientSecret = self.getInstanceSetting('client_secret')
            header = { 'User-Agent' : self.user_agent , 'Content-Type': 'application/x-www-form-urlencoded'}

            req = urllib2.Request(url, 'client_id=' + clientID + '&client_secret=' + clientSecret + '&refresh_token=' + self.authorization.getToken('auth_refresh_token') + '&grant_type=refresh_token', header)

            try:
                response = urllib2.urlopen(req)
            except urllib2.URLError as e:
                if e.code == 403:
                    logger.error('Login information is incorrect or permission is denied (403)')
                else:
                    logger.error('Login information is incorrect or permission is denied')
                return

            response_data = response.read()
            response.close()

            for r in re.finditer('\"access_token\"\s?\:\s?\"([^\"]+)\".+?' , response_data, re.DOTALL):
                accessToken = r.group(1)
                self.authorization.setToken('auth_access_token',accessToken)
                self.updateAuthorization()

            for r in re.finditer('\"error_description\"\s?\:\s?\"([^\"]+)\"', response_data, re.DOTALL):
                errorMessage = r.group(1)
                logger.error('The following login error was encountered:')
                logger.error(errorMessage)

            return

    def getHeadersList(self, isPOST=False, additionalHeader=None, additionalValue=None, isJSON=False):
        if self.authorization.isToken(self.instanceName, 'auth_access_token') and not isPOST:
            if additionalHeader is not None:
                return { 'Cookie' : 'DRIVE_STREAM='+ self.authorization.getToken('DRIVE_STREAM'), 'Authorization' : 'Bearer ' + self.authorization.getToken('auth_access_token'), additionalHeader : additionalValue }
            else:
                return {  'Cookie' : 'DRIVE_STREAM='+ self.authorization.getToken('DRIVE_STREAM'), 'Authorization' : 'Bearer ' + self.authorization.getToken('auth_access_token') }
        elif isJSON and self.authorization.isToken(self.instanceName, 'auth_access_token'):
            return { 'Content-Type': 'application/json', 'Cookie' : 'DRIVE_STREAM='+ self.authorization.getToken('DRIVE_STREAM'), 'Authorization' : 'Bearer ' + self.authorization.getToken('auth_access_token') }
        elif self.authorization.isToken(self.instanceName, 'auth_access_token'):
            return { "If-Match" : '*', 'Content-Type': 'application/atom+xml', 'Cookie' : 'DRIVE_STREAM='+ self.authorization.getToken('DRIVE_STREAM'), 'Authorization' : 'Bearer ' + self.authorization.getToken('auth_access_token') }
        elif self.authorization.isToken(self.instanceName, 'DRIVE_STREAM') and not isPOST:
            if additionalHeader is not None:
                return { 'Cookie' : 'DRIVE_STREAM='+ self.authorization.getToken('DRIVE_STREAM'), additionalHeader : additionalValue }
            else:
                return {  'Cookie' : 'DRIVE_STREAM='+ self.authorization.getToken('DRIVE_STREAM') }

        else:
            return { 'User-Agent' : self.user_agent}

    def getHeadersEncoded(self):
        return urllib.urlencode(self.getHeadersList())

    def getDrives(self):
        url = self.API_URL +'drives?pageSize=100'
        drives = []

        req = urllib2.Request(url, None, self.getHeadersList())

        try:
            response = urllib2.urlopen(req)
        except urllib2.URLError as e:
            if e.code == 403 or e.code == 401:
                self.refreshToken()
                req = urllib2.Request(url, None, self.getHeadersList())
                try:
                    response = urllib2.urlopen(req)
                except urllib2.URLError as e:
                    logger.error(str(e))
                    return None
            else:
              logger.error(str(e))
              return None

        response_data = response.read()
        response.close()

        try:
            datos = json.loads(response_data)
            for d in datos['drives']:
                drives.append( (d['id'], d['name']) )
        except:
            logger.error('No se puede cargar la respuesta de google!')

        return drives

    def getFiles(self, drive_id=None, q=None, nextPageToken=None, perpage=10, orden='modifiedTime+desc'):

        if drive_id == 'root': url_parms = 'corpora=user&includeItemsFromAllDrives=false&supportsAllDrives=true'
        elif not drive_id: url_parms = 'corpora=allDrives&includeItemsFromAllDrives=true&supportsAllDrives=true'
        else: url_parms = 'corpora=drive&driveId='+drive_id+'&includeItemsFromAllDrives=true&supportsAllDrives=true'

        url = self.API_URL +'files?'+url_parms
        url += '&pageSize=' + str(perpage)
        if q: url += "&q=" + q
        if orden: url += '&orderBy=' + orden
        if nextPageToken: url += "&pageToken=" + nextPageToken

        req = urllib2.Request(url, None, self.getHeadersList())

        try:
            response = urllib2.urlopen(req)
        except urllib2.URLError as e:
            if e.code == 403 or e.code == 401:
                self.refreshToken()
                req = urllib2.Request(url, None, self.getHeadersList())
                try:
                    response = urllib2.urlopen(req)
                except urllib2.URLError as e:
                    logger.error(str(e))
                    return
            else:
              logger.error(str(e))
              return

        response_data = response.read()
        response.close()

        try:
            datos = json.loads(response_data)
        except:
            logger.error('No se puede cargar la respuesta de google!')
            datos = None

        return datos

    def getFileUrl(self, file_id=None):
        if not file_id: return None

        url = self.API_URL +'files/'+file_id+'?includeTeamDriveItems=true&supportsTeamDrives=true&alt=media'

        headers = self.getHeadersList()
        for i, h in enumerate(headers):
            url += '|' if i == 0 else '&'
            url += h + '=' + str(headers[h])

        return url

    def getFileInfo(self, file_id=None):
        if not file_id: return None

        url = self.API_URL +'files/'+file_id+'?includeTeamDriveItems=true&supportsTeamDrives=true'
        url += '&fields=id%2Cname%2Csize%2CvideoMediaMetadata'

        req = urllib2.Request(url, None, self.getHeadersList())

        try:
            response = urllib2.urlopen(req)
        except urllib2.URLError as e:
            if e.code == 403 or e.code == 401:
                self.refreshToken()
                req = urllib2.Request(url, None, self.getHeadersList())
                try:
                    response = urllib2.urlopen(req)
                except urllib2.URLError as e:
                    logger.error(str(e))
                    return None
              else:
                logger.error(str(e))
                return None

        response_data = response.read()
        response.close()

        try:
            datos = json.loads(response_data)
            datos['url_directo'] = self.getFileUrl(file_id)
        except:
            logger.error('No se puede cargar la respuesta de google!')
            datos = None

        try:
            datos['extra'] = self.getFileInfo_extra(file_id)
        except:
            datos['extra'] = None

        return datos

    def getFileInfo_extra(self, file_id=None):
        if not file_id: return None

        url = 'https://drive.google.com/get_video_info?docid='+file_id

        req = urllib2.Request(url, None, self.getHeadersList())

        try:
            response = urllib2.urlopen(req)
        except urllib2.URLError as e:
            if e.code == 403 or e.code == 401:
                self.refreshToken()
                req = urllib2.Request(url, None, self.getHeadersList())
                try:
                    response = urllib2.urlopen(req)
                except urllib2.URLError as e:
                    logger.error(str(e))
                    return None
            else:
              logger.error(str(e))
              return None

        response_data = response.read()

        cookies = ""
        cookie = response.headers["set-cookie"].split("HttpOnly, ")
        for c in cookie:
            cookies += c.split(";", 1)[0] + "; "

        headers_string = "|Cookie=" + cookies

        response.close()

        video_urls = []; urls = []
        data = response_data.decode('unicode-escape')
        data = urllib.unquote_plus(urllib.unquote_plus(data))

        url_streams = scrapertools.find_single_match(data, 'url_encoded_fmt_stream_map=(.*)')
        streams = scrapertools.find_multiple_matches(url_streams, 'itag=(\d+)&url=(.*?)(?:;.*?quality=.*?(?:,|&)|&quality=.*?(?:,|&))')

        itags = {'18': '360p', '22': '720p', '34': '360p', '35': '480p', '37': '1080p', '43': '360p', '59': '480p'}
        for itag, video_url in streams:
            if not video_url in urls:
                video_url += headers_string
                video_urls.append([itags[itag], video_url])
                urls.append(video_url)

            video_urls.sort(key=lambda video_urls: int(video_urls[0].replace("p", "")), reverse=True)

        return video_urls

    def getInstanceSetting(self,setting, default=None):
        try:
            return config.get_setting(self.instanceName + '_' + setting, default=default)
        except:
            return default

    def updateAuthorization(self):
        if self.authorization.isUpdated :
            self.authorization.saveTokens(self.instanceName)

