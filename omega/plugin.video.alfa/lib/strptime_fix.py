# -*- coding: utf-8 -*-
import sys
import datetime
import time

#fix for datatetime.strptime returns None
class proxydt(datetime.datetime):
    def __init__(self, *args, **kwargs):
        if sys.version_info[0] < 3:
            super(proxydt, self).__init__(*args, **kwargs)
        else:
            super(proxydt, self).__init__()

    @classmethod
    def strptime(cls, date_string, format):
        return datetime(*(time.strptime(date_string, format)[0:6]))

datetime.datetime = proxydt
from datetime import datetime