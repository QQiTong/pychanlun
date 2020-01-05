def FindPrevEq(a, v, i):
    result = -1
    for x in range(i - 1, -1, -1):
        if a[x] == v:
            result = x
            break
    return result


def FindNextEq(a, v, i, end):
    result = -1
    for x in range(i, end):
        if a[x] == v:
            result = x
            break
    return result
