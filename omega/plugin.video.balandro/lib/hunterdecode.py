# -*- coding: utf-8 -*-

import re

argsregex = r'\(h,\s*u,\s*n,\s*t,\s*e,\s*r\).+}\("([^"]+)",[^,]+,\s*"([^"]+)",\s*(\d+),\s*(\d+)'
_0xce1e = "0123456789abcdefghijklmnopqrstuvwxyzABCDEFGHIJKLMNOPQRSTUVWXYZ+/"

def duf(d,e,f):
    g = list(_0xce1e)
    h = g[0:e]
    i = g[0:f]
    d = list(d)[::-1]
    j = 0
    for c,b in enumerate(d):
        if b in h:
            j = j + h.index(b)*e**c

    k = ""
    while j > 0:
        k = i[j%f] + k
        j = (j - (j%f))//f

    return int(k) or 0


def hunter(h, n, t, e):
    r = ""
    i = 0
    while i < len(h):
        j = 0
        s = ""
        while h[i] is not n[e]:
            s = ''.join([s,h[i]])
            i = i + 1

        while j < len(n):
            s = s.replace(n[j],str(j))
            j = j + 1

        r = ''.join([r,''.join(map(chr, [duf(s,e,10) - t]))])
        i = i + 1

    return r

def decode(source):
    try:
       payload, n, t, e = re.search(argsregex, source, re.DOTALL).groups()
       return hunter(payload, n, int(t), int(e))
    except:
       return source