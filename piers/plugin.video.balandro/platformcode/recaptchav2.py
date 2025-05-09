# -*- coding: utf-8 -*-

from core import httptools, scrapertools
from platformcode import logger


def rev2(site_key, co, sa, loc):
    logger.info()

    cb = '123456789'

    api_url = 'https://www.google.com/recaptcha/api.js'

    headers = {"User-Agent": httptools.get_user_agent(), "Referer": loc,
               "Accept": "text/html,application/xhtml+xml,application/xml;q=0.9,*/*;q=0.8",
               "Accept-Language": "ro-RO,ro;q=0.8,en-US;q=0.6,en-GB;q=0.4,en;q=0.2"}

    r_data = httptools.downloadpage(api_url, headers=headers, follow_redirects=False).data

    v = scrapertools.find_single_match(r_data, 'releases/([^/]+)')

    base_url = 'https://www.google.com/recaptcha/api2/anchor?ar=1&k=%s&co=%s&hl=ro&v=%s&size=invisible&cb%s' % (site_key, co, v, cb)

    r_data = httptools.downloadpage(base_url, headers=headers, follow_redirects=False).data

    c = scrapertools.find_single_match(r_data, 'id="recaptcha-token" value="([^"]+)"')

    t_url = 'https://www.google.com/recaptcha/api2/reload?k=%s' % site_key

    post = {"v": v, "reason": "q", "k": site_key, "c": c, "sa": sa, "co": co}

    p = "v=%s&reason=q&k=%s&c=%s&sa=%s&co=%s" % (v, site_key, c, sa, co)

    head = {"Accept": "*/*'",
            "Accept-Language": "ro-RO,ro;q=0.8,en-US;q=0.6,en-GB;q=0.4,en;q=0.2",
            "Accept-Encoding": "deflate",
            "Content-Type": "application/x-www-form-urlencoded;charset=utf-8",
            "Content-Length": "%s" % len(p), "Connection": "keep-alive", "referer": base_url}

    r_data = httptools.downloadpage(t_url, headers=head, follow_redirects=False, post=post).data

    response = scrapertools.find_single_match(r_data, '"rresp","([^"]+)"')

    return response