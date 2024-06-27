import base64

a2j = 'abcdefghij'

def Int2Char(x: int) -> str:
    x = str(x)
    int_list = [int(y) for y in x]
    txt = [a2j[z] for z in int_list]
    return ''.join(txt)

def Char2Int(x: str) -> int:
    int_list = [a2j.index(y) for y in x]
    txt = ''.join([str(z) for z in int_list])
    return int(txt)

def encrypt(txt: str) -> str:
    return base64.b64encode(txt.encode('utf-8')).decode('utf-8')

def decrypt(txt: str) -> str:
    x = len(txt) % 4
    if x != 0:
        txt += '=' * x
    return base64.b64decode(txt.encode('utf-8')).decode('utf-8')
