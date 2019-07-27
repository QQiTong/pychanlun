import pydash

def notHigher(duan_s, high_s):
    """
    不破前高
    """
    i1 = pydash.find_last_index(duan_s, lambda d: d == 1)
    i2 = pydash.find_last_index(duan_s[:i1], lambda d: d == 1)
    if i1 > i2 > -1:
        if high_s[i1] <= high_s[i2]:
            return True
    return False

def notLower(duan_s, low_s):
    """
    不破前低
    """
    i1 = pydash.find_last_index(duan_s, lambda d: d == -1)
    i2 = pydash.find_last_index(duan_s[:i1], lambda d: d == -1)
    if i1 > i2 > -1:
        if low_s[i1] >= low_s[i2]:
            return True
    return False