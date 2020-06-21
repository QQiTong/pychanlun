# -*- coding: utf-8 -*-

import pydash

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


def FindPrevEntanglement(e_list, t):
    for idx in range(len(e_list) - 1, -1, -1):
        if e_list[idx].endTime < t:
            return e_list[idx]
    return None


PERIODS = ["1m", "3m", "5m", "15m", "30m", "60m", "180m", "1d", "3d"]


def get_required_period_list(period):
    x = pydash.find_index(PERIODS, lambda value: pydash.eq(value, period))
    return pydash.chain(PERIODS[x:]).filter_(lambda _, i: i % 2 == 0).value()
