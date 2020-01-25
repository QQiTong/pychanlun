# -*- coding: utf-8 -*-

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

def FindPrevGt(a, v, i):
    result = -1
    for x in range(i - 1, -1, -1):
        if a[x] > v:
            result = x
            break
    return result

def FindNextGt(a, v, i, end):
    result = -1
    for x in range(i, end):
        if a[x] > v:
            result = x
            break
    return result

def FindPrevLt(a, v, i):
    result = -1
    for x in range(i - 1, -1, -1):
        if a[x] < v:
            result = x
            break
    return result

def FindNextLt(a, v, i, end):
    result = -1
    for x in range(i, end):
        if a[x] < v:
            result = x
            break
    return result

def FindPrevEntanglement(entanglement_list, t):
    for idx in range(len(entanglement_list) - 1, -1, -1):
        if entanglement_list[idx].endTime < t:
            return entanglement_list[idx]
    return None
