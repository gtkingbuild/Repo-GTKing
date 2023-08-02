# -*- coding: utf-8 -*-
"""
Transcodificación de GibberishAES a Python 2/3
Solo decodifica texto, no se necesitó mas que para eso,
pero si se requiere, se pueden transformar más cosas ;)

@autor: SistemaRayoXP (con ayuda de Delta y Kingbox)
@version: 0.5
"""

class GibberishAES(object):

    def __init__(self, string="", pass_="", Nr=14, Nk=8, Decrypt=False):
        # Requerido para determinar versión de Python
        import sys
        self.PY3 = False
        if sys.version_info[0] >= 3:
            self.PY3 = True

        self.Nr = Nr
        self.Nk = Nk
        self.Decrypt = Decrypt
        self.SBox = self.strhex('637c777bf26b6fc53001672bfed7ab76ca82c97dfa5947f0add4a2af9ca472c0b7fd9326363ff7cc34a5e5f171d8311504c723c31896059a071280e2eb27b27509832c1a1b6e5aa0523bd6b329e32f8453d100ed20fcb15b6acbbe394a4c58cfd0efaafb434d338545f9027f503c9fa851a3408f929d38f5bcb6da2110fff3d2cd0c13ec5f974417c4a77e3d645d197360814fdc222a908846eeb814de5e0bdbe0323a0a4906245cc2d3ac629195e479e7c8376d8dd54ea96c56f4ea657aae08ba78252e1ca6b4c6e8dd741f4bbd8b8a703eb5664803f60e613557b986c11d9ee1f8981169d98e949b1e87e9ce5528df8ca1890dbfe6426841992d0fb054bb16', 2)
        self.SBoxInv = self.invertArr(self.SBox)
        self.Rcon = self.strhex('01020408102040801b366cd8ab4d9a2f5ebc63c697356ad4b37dfaefc591', 2)

        self.G2X = self.Gx(2)
        self.G3X = self.Gx(3)
        self.G9X = self.Gx(9)
        self.GBX = self.Gx(0xb)
        self.GDX = self.Gx(0xd)
        self.GEX = self.Gx(0xe)

        if string and pass_:
            self.result = self.dec(string, pass_)

    def strhex(self, str, size):
        ret = []
        for i in range(0, len(str), size):
            ret.append(int(str[i: i + size], 16))
        return ret

    def invertArr(self, arr):
        ret = list(arr)
        for i in range(len(arr)):
            ret[arr[i]] = i
        return ret

    def Gxx(self, a, b):
        ret = 0;
        
        for i in range(8):
            if ((b & 1) == 1): ret = ret ^ a
            # xmult
            if a > 0x7f: a = 0x11b ^ (a << 1)
            else: a = (a << 1)
            b  = b >> 1
        return ret

    def Gx(self, x):
        r = [];
        for i in range(256):
            r.append(self.Gxx(x, i))
        return r

    def arrMD5(self, numArr):
        # Maldito encoding mata-cerebros
        # https://stackoverflow.com/questions/41068617/python-2-vs-3-same-inputs-different-results-md5-hash#41068841
        if self.PY3:
            from hashlib import md5
            realStr = b"".join([chr(x).encode('latin1') for x in numArr])
            hash_ = md5(realStr)
            md5arr = [x for x in hash_.digest()]
        else:
            import md5
            realStr = b"".join([chr(x) for x in numArr])
            hash_ = md5.new(realStr)
            md5arr = [ord(x) for x in hash_.digest()]
        return md5arr

    def aes64decode(self, string):
        flatArr = []
        _chars = 'ABCDEFGHIJKLMNOPQRSTUVWXYZabcdefghijklmnopqrstuvwxyz0123456789+/'
        string = string.replace("\n", "")

        for i in range(0, len(string), 4):
            c = []
            b = []

            try: c.append(_chars.index(string[i:i + 1]))
            except: c.append(-1)
            try: c.append(_chars.index(string[i + 1:i + 2]))
            except: c.append(-1)
            try: c.append(_chars.index(string[i + 2:i + 3]))
            except: c.append(-1)
            try: c.append(_chars.index(string[i + 3:i + 4]))
            except: c.append(-1)

            b.append((c[0] << 2) | (c[1] >> 4))
            b.append(((c[1] & 15) << 4) | (c[2] >> 2))
            b.append(((c[2] & 3) << 6) | c[3])
            flatArr.extend([b[0], b[1], b[2]])

        flatArr = flatArr[0:(len(flatArr) - (len(flatArr) % 16))]
        return flatArr

    def s2a(self, string, binary=None):
        array = []
        if not binary:
            string = string
        for i in range(len(string)):
            array.append(ord(string[i]))

        return array

    def openSSLKey(self, passwordArr, saltArr):
        """
        Number of rounds depends on the size of the AES in use
        3 rounds for 256
            2 rounds for the key, 1 for the IV
        2 rounds for 128
            1 round for the key, 1 round for the IV
        3 rounds for 192 since it's not evenly divided by 128 bits
        """
        rounds = 3
        data00 = list(passwordArr)
        data00.extend(saltArr)

        md5_hash = [self.arrMD5(data00)]
        result = md5_hash[0]

        for i in range(1, rounds):
            md5_hash.append(self.arrMD5( (md5_hash[i - 1] + data00) ))
            result.extend(md5_hash[i])

        key = result[0 : 4 * self.Nk]
        iv = result[4 * self.Nk : 4 * self.Nk + 16]
        return {'key': key, 'iv': iv}

    def subWord(self, w):
        # apply SBox to 4-byte word w
        temp = []
        for i in range(4):
            temp.append(self.SBox[w[i]])
        return temp

    def rotWord(self, w):
        # rotate 4-byte word w left by one byte
        tmp = w[0]

        for i in range(3):
            w[i] = w[i + 1]

        w[3] = tmp
        return w

    def expandKey(self, key):
        # Expects a 1d number array
        w = []
        flat = []

        for i in range(self.Nk):
            r = [
                    key[4 * i],
                    key[4 * i + 1],
                    key[4 * i + 2],
                    key[4 * i + 3]
            ]
            w.append(r)

        for i in range(self.Nk, (4 * (self.Nr + 1))):
            temp = []
            w.append([])

            for t in range(4):
                temp.append(w[i - 1][t])

            if i % self.Nk == 0:
                temp = self.subWord(self.rotWord(temp))
                temp[0] = temp[0] ^ self.Rcon[i // self.Nk - 1]

            elif self.Nk > 6 and i % self.Nk == 4:
                temp = self.subWord(temp)

            for t in range(4):
                w[i].append(w[i - self.Nk][t] ^ temp[t])

        for i in range((self.Nr + 1)):
            flat.append([])
            for j in range(4):
                flat[i].extend([w[i * 4 + j][0], w[i * 4 + j][1], w[i * 4 + j][2], w[i * 4 + j][3]])
        return flat

    def addRoundKey(self, state, words, round):
        temp = []
        for i in range(16):
            temp.append(state[i] ^ words[round][i])
        return temp

    def subBytes(self, state):
        temp = []
        if self.Decrypt: S = self.SBoxInv
        else: S = self.SBox

        for i in range(16):
            temp.append(S[state[i]]);
        return temp

    def shiftRows(self, state):
        temp = []
        if self.Decrypt: shiftBy = [0, 13, 10, 7, 4, 1, 14, 11, 8, 5, 2, 15, 12, 9, 6, 3]
        else: shiftBy = [0, 5, 10, 15, 4, 9, 14, 3, 8, 13, 2, 7, 12, 1, 6, 11]

        for i in range(16):
            temp.append(state[shiftBy[i]]);
        return temp

    def mixColumns(self, state):
        t = []
        if not self.Decrypt:
            for c in range(4):
                t.append(self.G2X[state[c * 4]] ^ self.G3X[state[1 + c * 4]] ^ state[2 + c * 4] ^ state[3 + c * 4])
                t.append(state[c * 4] ^ self.G2X[state[1 + c * 4]] ^ self.G3X[state[2 + c * 4]] ^ state[3 + c * 4])
                t.append(state[c * 4] ^ state[1 + c * 4] ^ self.G2X[state[2 + c * 4]] ^ self.G3X[state[3 + c * 4]])
                t.append(self.G3X[state[c * 4]] ^ state[1 + c * 4] ^ state[2 + c * 4] ^ self.G2X[state[3 + c * 4]])
        else:
            for c in range(4):
                t.append(self.GEX[state[c * 4]] ^ self.GBX[state[1 + c * 4]] ^ self.GDX[state[2 + c * 4]] ^ self.G9X[state[3 + c * 4]])
                t.append(self.G9X[state[c * 4]] ^ self.GEX[state[1 + c * 4]] ^ self.GBX[state[2 + c * 4]] ^ self.GDX[state[3 + c * 4]])
                t.append(self.GDX[state[c * 4]] ^ self.G9X[state[1 + c * 4]] ^ self.GEX[state[2 + c * 4]] ^ self.GBX[state[3 + c * 4]])
                t.append(self.GBX[state[c * 4]] ^ self.GDX[state[1 + c * 4]] ^ self.G9X[state[2 + c * 4]] ^ self.GEX[state[3 + c * 4]])

        return t

    def decryptBlock(self, block, words):
        self.Decrypt = True
        state = self.addRoundKey(block, words, self.Nr)

        for round in reversed(range(self.Nr)):
            state = self.shiftRows(state)
            state = self.subBytes(state)
            state = self.addRoundKey(state, words, round)
            if round > 0:
                state = self.mixColumns(state)
            # last round? don't mixColumns

        return state

    def xorBlocks(self, block1, block2):
        temp = []
        for i in range(16):
            temp.append(block1[i] ^ block2[i])
        return temp;

    def block2s(self, block, lastBlock):
        string = ''

        if (lastBlock):
            padding = block[15]
            if padding > 16:
                raise Exception('Decryption error: Maybe bad key')
            if padding == 16:
                return ''
            for i in range(16 - padding):
                string += chr(block[i])
        else:
            for i in range(16):
                string += chr(block[i])
        return string

    def rawDecrypt(self, cryptArr, key, iv, binary=None):
        # cryptArr, key and iv as byte arrays
        key = self.expandKey(key)
        numBlocks = len(cryptArr) // 16
        cipherBlocks = []
        plainBlocks = []
        string = ''

        for i in range(numBlocks):
            cipherBlocks.append(cryptArr[i * 16 : (i + 1) * 16])

        """
        Bueno, pues resulta que en Javascript este "for" va en reversa
        Es complicado replicar esto en Python dado que también se accede y asigna
        a los valores en reversa, y en JS se accede a índices de array que no existen
        (retornan void (None) en vez de dar excepción)
        De cualquier modo, se logra con un poco de código sucio :S
        """
        for i in reversed(range(len(cipherBlocks))):
            plainBlocks.append(self.decryptBlock(cipherBlocks[i], key))

            # HACK: Asignación en reversa
            if i == 0:
                # Asignamos el bloque xor-eado a una lista temporal
                reversePlainBlocks = [self.xorBlocks(plainBlocks[-1], iv)]
                # La extendemos con plainBlocks, efectivamente
                # colocando el bloque limpio al principio
                reversePlainBlocks.extend(plainBlocks)
                # Reemplazamos plainBlocks con este chack
                plainBlocks = reversePlainBlocks[:]
            else:
                # Asignamos el bloque xor-eado a una lista temporal
                reversePlainBlocks = [self.xorBlocks(plainBlocks[-1], cipherBlocks[i - 1])]
                # La extendemos con plainBlocks, efectivamente
                # colocando el bloque limpio al principio
                reversePlainBlocks.extend(plainBlocks)
                # Reemplazamos plainBlocks con este chack
                plainBlocks = reversePlainBlocks[:]

        for i in range(numBlocks - 1):
            string += self.block2s(plainBlocks[i], False)

        string += self.block2s(plainBlocks[i + 1], True)

        return string

    def dec(self, string, pass_, binary=None):
        cryptArr = self.aes64decode(string)
        salt = cryptArr[8:16]
        pbe = self.openSSLKey(self.s2a(pass_), salt)
        key = pbe['key']
        iv = pbe['iv']
        newCryptArr = cryptArr[16:]
        newString = self.rawDecrypt(newCryptArr, key, iv)
        return newString
