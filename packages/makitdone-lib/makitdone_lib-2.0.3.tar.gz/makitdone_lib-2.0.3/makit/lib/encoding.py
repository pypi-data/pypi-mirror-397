# coding:utf-8

def encode(v, encoding='utf-8', errors='strict'):
    if isinstance(v, bytes):
        return v
    elif isinstance(v, memoryview):
        return bytes(v)
    return str(v).encode(encoding, errors)


def decode(v, encoding='utf-8', errors='strict'):
    if isinstance(v, bytes):
        return v.decode(encoding, errors)
    elif isinstance(v, memoryview):
        return bytes(v).decode(encoding, errors)
    return str(v)
