# -*- coding: utf-8 -*-

def fq_util_code_append_market_code(code, upper_case=False):
    code_head = code[:2]
    if code_head in ["60", "68", "50", "51", "01", "10", "11", "12", "13", "14", "20"]:
        return 'SH' + code if upper_case else 'sh' + code
    elif code_head in ["00", "30", "15", "16", "10", "11", "12", "13", "14"]:
        return 'SZ' + code if upper_case else 'sz' + code
