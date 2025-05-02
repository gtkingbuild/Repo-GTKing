# -*- coding: utf-8 -*-

from core import httptools, scrapertools
from platformcode import config, logger


def host(host):
    logger.info()

    current_domain = ''

    try:
        data = httptools.downloadpage('https://entrarplaydede.com/').data

        current_domain = scrapertools.find_single_match(data, '>Dirección actual:.*?<a href="(.*?)"')
        if not current_domain: current_domain = scrapertools.find_single_match(data, '>Dirección actual:.*?">(.*?)</a>').strip()

        if current_domain:
            current_domain = current_domain.lower()

            if not 'playdede' in current_domain: current_domain = ''

        if current_domain:
            if not 'https' in current_domain: current_domain  = 'https://' + current_domain
            if not current_domain.endswith('/'): current_domain = current_domain + '/'
    except:
        pass

    if current_domain:
        domain = config.get_setting('dominio', 'playdede', default='')
        if not domain:
            domain = current_domain
            host = domain

        else:
          if not domain == host: host = current_domain

    return host
