# -*- coding: utf-8 -*-

from platformcode import config

class authorization:
    def __init__(self, username):
        self.auth = {}
        self.username = username
        self.isUpdated = False

    def setToken(self, name, value):
        try:
            if self.auth[name] != value: self.auth[name] = value
            self.isUpdated = True
        except:
            self.isUpdated = True

        self.auth[name] = value

    def getToken(self, name):
        if name in self.auth:
            return self.auth[name]
        else:
            return ''

    def getTokenCount(self):
        return len(self.auth)

    def saveTokens(self, instanceName):
        for token in self.auth:
            config.set_setting(instanceName + '_' + token, self.auth[token])

    def loadToken(self, instanceName, token):
        try:
            tokenValue = config.get_setting(instanceName + '_' + token, default='')
            if tokenValue != '':
                self.auth[token] = tokenValue
                return True
            else:
                return False
        except:
            return False

    def isToken(self, instanceName, token):
        try:
            if self.auth[token] != '':
                return True
            else:
                return False
        except:
            return False
