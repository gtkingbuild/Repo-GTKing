/* ************************************************************************************
***     Support for some DOM functions to let run JS and used by runJavascript.py   ***
* ************************************************************************************/

/*
 Definition of window and document
*/
if (!window) {
    var window = {};
}
if (!document) {
    var document = {};
}
if (!atob) {
    var atob = alfa_atob;
}
if (!window.atob) {
    window.atob = alfa_atob;
}
if (!btoa) {
    var btoa = alfa_btoa;
}
if (!window.btoa) {
    window.btoa = alfa_btoa;
}

/*
 VanillaJS function to replace DOM function "window.atob"
*/
function alfa_atob(data) {
    if (arguments.length == 0) {
        throw new TypeError('1 argument required, but only 0 present.');
    }
    data = data + '';
    data = data.replace(/[ \t\n\f\r]/g, '');
    if (data.length % 4 == 0) {
        data = data.replace(/==?$/, '');
    }

    if (data.length % 4 == 1 || /[^+/0-9A-Za-z]/.test(data)) {
        return null;
    }
    output = '';
    buffer = 0;
    accumulatedBits = 0;
    for (i = 0; i < data.length; i++) {
        buffer <<= 6;
        buffer |= alfa_atobLookup(data[i]);
        accumulatedBits += 6;
        if (accumulatedBits == 24) {
            output += String.fromCharCode((buffer & 0xff0000) >> 16);
            output += String.fromCharCode((buffer & 0xff00) >> 8);
            output += String.fromCharCode(buffer & 0xff);
            buffer = accumulatedBits = 0;
        }
    }
    if (accumulatedBits == 12) {
        buffer >>= 4;
        output += String.fromCharCode(buffer);
    } else if (accumulatedBits == 18) {
        buffer >>= 2;
        output += String.fromCharCode((buffer & 0xff00) >> 8);
        output += String.fromCharCode(buffer & 0xff);
    }
    return output;
}
var keystr = 'ABCDEFGHIJKLMNOPQRSTUVWXYZabcdefghijklmnopqrstuvwxyz0123456789+/';
function alfa_atobLookup(chr) {
    var index = keystr.indexOf(chr);
    return index < 0 ? undefined : index;
}


/*
 VanillaJS function to replace DOM function "window.btoa"
*/
function alfa_btoa(s) {
    if (arguments.length === 0) {
        throw new TypeError("1 argument required, but only 0 present.");
    }
    i;
    s = s + '';
    for (i = 0; i < s.length; i++) {
        if (s.charCodeAt(i) > 255) {
            return null;
        }
    }
    out = "";
    for (i = 0; i < s.length; i += 3) {
        groupsOfSix = [undefined, undefined, undefined, undefined];
        groupsOfSix[0] = s.charCodeAt(i) >> 2;
        groupsOfSix[1] = (s.charCodeAt(i) & 0x03) << 4;
        if (s.length > i + 1) {
            groupsOfSix[1] |= s.charCodeAt(i + 1) >> 4;
            groupsOfSix[2] = (s.charCodeAt(i + 1) & 0x0f) << 2;
        }
        if (s.length > i + 2) {
            groupsOfSix[2] |= s.charCodeAt(i + 2) >> 6;
            groupsOfSix[3] = s.charCodeAt(i + 2) & 0x3f;
        }
        for (j = 0; j < groupsOfSix.length; j++) {
            if (typeof groupsOfSix[j] === "undefined") {
                out += "=";
            } else {
                out += alfa_btoaLookup(groupsOfSix[j]);
            }
        }
    }
    return out;
}
keystr = "ABCDEFGHIJKLMNOPQRSTUVWXYZabcdefghijklmnopqrstuvwxyz0123456789+/";
function alfa_btoaLookup(index) {
    if (index >= 0 && index < 64) {
        return keystr[index];
    }
    return undefined;
}
