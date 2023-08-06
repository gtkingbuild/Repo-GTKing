# -*- coding: utf-8 -*-
# Python 3

import xbmc

class XstreamPlayer(xbmc.Player):
    def __init__(self, *args, **kwargs):
        xbmc.Player.__init__(self, *args, **kwargs)
        self.streamFinished = False
        self.streamSuccess = True
        self.playedTime = 0
        self.totalTime = 999999
        #log(LOGMESSAGE + ' -> [player]: player instance created', LOGNOTICE)

    def onPlayBackStarted(self):
        #log(LOGMESSAGE + ' -> [player]: starting Playback', LOGNOTICE)
        self.totalTime = self.getTotalTime()

    def onPlayBackStopped(self):
        #log(LOGMESSAGE + ' -> [player]: Playback stopped', LOGNOTICE)
        if self.playedTime == 0 and self.totalTime == 999999:
            self.streamSuccess = False
            #log(LOGMESSAGE + ' -> [player]: Kodi failed to open stream', LOGERROR)
        self.streamFinished = True

    def onPlayBackEnded(self):
        #log(LOGMESSAGE + ' -> [player]: Playback completed', LOGNOTICE)
        self.onPlayBackStopped()


class cPlayer:
    def clearPlayList(self):
        oPlaylist = self.__getPlayList()
        oPlaylist.clear()

    def __getPlayList(self):
        return xbmc.PlayList(xbmc.PLAYLIST_VIDEO)

    def addItemToPlaylist(self, oGuiElement):
        oListItem = cGui().createListItem(oGuiElement)
        self.__addItemToPlaylist(oGuiElement, oListItem)

    def __addItemToPlaylist(self, oGuiElement, oListItem):
        oPlaylist = self.__getPlayList()
        oPlaylist.add(oGuiElement.getMediaUrl(), oListItem)

    def startPlayer(self):
        #log(LOGMESSAGE + ' -> [player]: start player', LOGNOTICE)
        xbmcPlayer = XstreamPlayer()
        monitor = xbmc.Monitor()
        while (not monitor.abortRequested()) & (not xbmcPlayer.streamFinished):
            if xbmcPlayer.isPlayingVideo():
                xbmcPlayer.playedTime = xbmcPlayer.getTime()
            monitor.waitForAbort(10)
        return xbmcPlayer.streamSuccess
