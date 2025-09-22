# -*- coding: utf-8 -*-
import requests as requests_
from doh import DNSOverrideDoH

class requests:
    session = requests_.Session()
    agent = 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/58.0.3029.110 Safari/537.3'
    default_timeout = 15

    # Chamada única para configurar o DoH na primeira importação
    DNSOverrideDoH()

    @classmethod
    def _prepare_headers(cls, headers):
        if headers is None:
            headers = {}
        if 'User-Agent' not in headers:
            headers['User-Agent'] = cls.agent
        return headers

    @classmethod
    def get(cls, url, headers=None, params=None, timeout=None, proxies=None, stream=False, verify=False, allow_redirects=True):
        headers = cls._prepare_headers(headers)
        if timeout is None and not stream:
            timeout = cls.default_timeout
        return cls.session.get(url, headers=headers, params=params, timeout=timeout, proxies=proxies, stream=stream, verify=verify, allow_redirects=allow_redirects)

    @classmethod
    def post(cls, url, headers=None, data=None, json=None, timeout=None, proxies=None, stream=False, verify=False, allow_redirects=True):
        headers = cls._prepare_headers(headers)
        if timeout is None and not stream:
            timeout = cls.default_timeout
        return cls.session.post(url, headers=headers, data=data, json=json, timeout=timeout, proxies=proxies, stream=stream, verify=verify, allow_redirects=allow_redirects)

    @classmethod
    def put(cls, url, headers=None, data=None, json=None, timeout=None, proxies=None, stream=False, verify=False, allow_redirects=True):
        headers = cls._prepare_headers(headers)
        if timeout is None and not stream:
            timeout = cls.default_timeout
        return cls.session.put(url, headers=headers, data=data, json=json, timeout=timeout, proxies=proxies, stream=stream, verify=verify, allow_redirects=allow_redirects)

    @classmethod
    def delete(cls, url, headers=None, params=None, timeout=None, proxies=None, verify=False, allow_redirects=True):
        headers = cls._prepare_headers(headers)
        if timeout is None:
            timeout = cls.default_timeout
        return cls.session.delete(url, headers=headers, params=params, timeout=timeout, proxies=proxies, verify=verify, allow_redirects=allow_redirects)
    
    @classmethod
    def head(cls, url, headers=None, params=None, timeout=None, proxies=None, verify=False, allow_redirects=True):
        headers = cls._prepare_headers(headers)
        if timeout is None:
            timeout = cls.default_timeout
        return cls.session.head(url, headers=headers, params=params, timeout=timeout, proxies=proxies, verify=verify, allow_redirects=allow_redirects)    
