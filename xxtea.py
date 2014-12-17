__author__ = 'Administrator'
import math
import base64
import binascii


def stringToLongArray(string, includeLength):
    length = len(string)
    result = []
    i = 0;
    while (i < length):
        re = 0
        try:
            re = ord(string[i:i + 1])
            re = re | (ord(string[i + 1:i + 2]) << 8)
            re = re | (ord(string[i + 2:i + 3]) << 16)
            re = re | (ord(string[i + 3:i + 4]) << 24)
        except:
            pass
        result.append(re)
        i += 4
    if (includeLength):
        result.append(length)
    return result


def longArrayToString(data, includeLength):
    length = len(data)
    n = (length - 1) << 2
    if (includeLength):
        m = data[length - 1]
        if ((m < n - 3) or (m > n)):
            return None
        n = m
    bdata = ""
    for i in range(0, length):  # (var i = 0;i < length;i ++ ):
        bdata = bdata + chr(data[i] & 0xff) + chr(data[i] >> 8 & 0xff) + chr(data[i] >> 16 & 0xff) + chr(
            data[i] >> 24 & 0xff)
    if (includeLength):
        return bdata[0:n]
    else:
        return bdata


def Base32encrypt(string, key):
    if (string == ""):
        return "";
    delta = 0x9E3779B8
    v = stringToLongArray(string, True)
    k = stringToLongArray(key, False)
    k_length = len(k)
    if (k_length < 4):
        k.append(0)
        k.append(0)
        k.append(0)
        k_length = 4
    v_length = len(v)
    n = v_length - 1;
    z = v[n]
    y = v[0];
    q = math.floor(6 + 52 / (n + 1))
    sum = 0
    while (0 < q ):
        q = q - 1
        sum = sum + delta & 0xffffffff;
        e = sum >> 2 & 3;
        for p in range(0, n):  # (p = 0; p < n; p ++ ):
            y = v[p + 1];
            mx = (z >> 5 ^ y << 2) + (y >> 3 ^ z << 4) ^ (sum ^ y) + (k[p & 3 ^ e] ^ z);
            z = v[p] = v[p] + mx & 0xffffffff;
        p = n
        y = v[0];
        mx = (z >> 5 ^ y << 2) + (y >> 3 ^ z << 4) ^ (sum ^ y) + (k[p & 3 ^ e] ^ z);
        z = v[n] = v[n] + mx & 0xffffffff;
    return longArrayToString(v, False);

def encode32(inputbuf):
    keyStr = "ABCDEFGHIJKLMNOPQRSTUVWXYZabcdefghijklmnopqrstuvwxyz0123456789+/=";
    #inputbuf = escape(inputbuf);
    output = "";
    i = 0;
    sing = 0
    while (i < len(inputbuf)):
        chr1 = ord(inputbuf[i:i+1])
        i = i + 1
        try:
            chr2 = ord(inputbuf[i:i+1])
            i = i + 1
        except:
            chr2 = 0
            sing = sing or 0x1
        try:
            chr3 = ord(inputbuf[i:i+1])
            i = i + 1
        except:
            chr3 = 0
            sing = sing or 0x2
        enc1 = chr1 >> 2;
        enc2 = ((chr1 & 3) << 4) | (chr2 >> 4);
        enc3 = ((chr2 & 15) << 2) | (chr3 >> 6);
        enc4 = chr3 & 63;
        if (sing and 0x1):
            enc3 = enc4 = 64
        elif (sing and 0x2):
            enc4 = 64
        output = output + keyStr[enc1:enc1+1] + keyStr[enc2:enc2+1] + keyStr[enc3:enc3+1] + keyStr[enc4:enc4+1]


    return output


def encrypt(text, key):
    b = Base32encrypt(text, key)
    print(':'.join(hex(ord(x))[2:] for x in b))
    data = encode32(binascii.a2b_hex(b))
    return data
