# -*- coding: utf-8 -*-

import sys
PY3 = False
if sys.version_info[0] >= 3: PY3 = True; unicode = str; unichr = chr; long = int

from platformcode import config, logger


def test_video_exists(page_url):
    # El servidor no está soportado, lo informamos
    return False, config.get_localized_string(30065)


def get_video_url(page_url, premium=False, user="", password="", video_password=""):
    return []