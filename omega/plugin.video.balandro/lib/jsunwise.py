# -*- coding: utf-8 -*-

import re

def unwise(wise):
    ## js2python
    def js_wise(wise):
        w, i, s, e = wise
        v0 = 0;
        v1 = 0;
        v2 = 0
        v3 = [];
        v4 = []
        while True:
            if v0 < 5:
                v4.append(w[v0])
            elif v0 < len(w):
                v3.append(w[v0])
            v0 += 1
            if v1 < 5:
                v4.append(i[v1])
            elif v1 < len(i):
                v3.append(i[v1])
            v1 += 1
            if v2 < 5:
                v4.append(s[v2])
            elif v2 < len(s):
                v3.append(s[v2])
            v2 += 1
            if len(w) + len(i) + len(s) + len(e) == len(v3) + len(v4) + len(e): break
        v5 = "".join(v3);
        v6 = "".join(v4)
        v1 = 0
        v7 = []
        for v0 in range(0, len(v3), 2):
            v8 = -1
            if ord(v6[v1]) % 2: v8 = 1
            v7.append(chr(int(v5[v0:v0 + 2], 36) - v8))
            v1 += 1
            if v1 >= len(v4): v1 = 0
        return "".join(v7)
    ## loop2unobfuscated
    ret = ''
    while True:
        wise = re.search("var\s.+?\('([^']+)','([^']+)','([^']+)','([^']+)'\)", wise, re.DOTALL)
        if not wise: break
        ret = wise = js_wise(wise.groups())
    return ret
