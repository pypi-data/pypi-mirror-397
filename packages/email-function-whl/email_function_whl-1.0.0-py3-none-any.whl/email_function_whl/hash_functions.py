import re

def hash_function(s):
    """Hash function for alphanumeric strings"""
    if s is None:
        return None
    s = str(s).upper()
    s = re.sub(r'[^A-Z0-9]', '', s)
    base36_map = {ch: idx for idx, ch in enumerate("0123456789ABCDEFGHIJKLMNOPQRSTUVWXYZ")}
    result = 0
    for i, ch in enumerate(reversed(s)):
        result += base36_map.get(ch, 0) * (36 ** i)
    result += len(s) * (36 ** (len(s) + 1))
    return result