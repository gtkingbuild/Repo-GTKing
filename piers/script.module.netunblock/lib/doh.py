# -*- coding: utf-8 -*-
import socket
import sys
import logging
import requests
addon_id = 'script.module.netunblock'
PY2 = sys.version_info[0] == 2
if PY2:
    from urlparse import urlparse
else:
    from urllib.parse import urlparse
logging.basicConfig(level=logging.DEBUG)
# Silencia logs do requests e urllib3
logging.getLogger("requests").setLevel(logging.WARNING)
logging.getLogger("urllib3").setLevel(logging.WARNING)



def get_doh_url():
    """
    Retorna a URL DoH configurada no ambiente.
    Se não estiver configurada, retorna a URL padrão.
    """
    from kodi_six import xbmcaddon
    addon = xbmcaddon.Addon(addon_id)
    doh_url = addon.getSetting("doh_url")
    return doh_url

def get_mode():
    """
    Retorna o modo de operação do addon.
    """
    from kodi_six import xbmcaddon
    addon = xbmcaddon.Addon(addon_id)
    mode = addon.getSetting("debug_mode")
    if mode == "true":
        return True
    else:
        return False

class DNSOverrideDoH:
    def __init__(self):
        if not get_doh_url().startswith('http'):
            self.doh_url_ = 'https://' + get_doh_url() + '/resolve?domain='
        else:
            self.doh_url_ = get_doh_url() + '/resolve?domain='
        # fix url
        self.doh_url = self.doh_url_.replace('//resolve', '/resolve')
        self.original_getaddrinfo = socket.getaddrinfo
        self.cache = {}
        self.debug_mode = False
        self.mode_logger = get_mode()

        # Override DNS
        socket.getaddrinfo = self._resolver

    def is_valid_ipv4(self, ip):
        try:
            socket.inet_aton(ip)
            return True
        except socket.error:
            return False    

    def resolve(self, domain):
        if domain in self.cache:
            if self.mode_logger:
                logging.info("Cache hit for {0}: {1}".format(domain, self.cache[domain]))
            return self.cache[domain]

        try:
            domain_target = domain.strip(".")
            url_dns = self.doh_url + domain_target
            parsed_url_resolver = urlparse(self.doh_url)
            domain_resolver = parsed_url_resolver.netloc
            if not domain_target in domain_resolver:
                if self.mode_logger:
                    logging.debug("Resolvendo {0} via DoH: {1}".format(domain, url_dns))
                response = requests.get(url_dns, timeout=5)
                if response.status_code == 200:
                    data = response.json()
                    ip = data.get("ip")
                    if ip:
                        self.cache[domain] = ip
                        if self.mode_logger:
                            logging.debug("Resolved {0} to {1}".format(domain, ip))
                        return ip
            return None
        except Exception as e:
            if self.mode_logger:
                logging.error("Erro ao resolver {0} via DoH: {1}".format(domain, e))
            return None

    def _resolver(self, host, port, *args, **kwargs):
        try:
            # Evita resolver o próprio servidor DoH para não causar recursão
            if self.doh_url and host in self.doh_url:
                return self.original_getaddrinfo(host, port, *args, **kwargs)

            if self.is_valid_ipv4(host):
                if self.mode_logger:
                    logging.debug("Bypass DNS: {0} já é um IP".format(host))
                return [(socket.AF_INET, socket.SOCK_STREAM, 6, '', (host, port))]

            ip = self.resolve(host)
            if ip:
                return [(socket.AF_INET, socket.SOCK_STREAM, 6, '', (ip, port))]
            if self.mode_logger:
                logging.warning("Falha ao resolver {0}, usando getaddrinfo original".format(host))
            if not self.debug_mode:
                return self.original_getaddrinfo(host, port, *args, **kwargs)
        except Exception as e:
            if self.mode_logger:
                logging.error("Erro no resolver para {0}: {1}".format(host, e))
            else:
                pass
        if not self.debug_mode:
            return self.original_getaddrinfo(host, port, *args, **kwargs)

