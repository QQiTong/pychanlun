import pydash

PERIODS = ["1m", "3m", "5m", "15m", "30m", "60m", "180m", "1d", "3d"]


def get_required_period_list(period):
    x = pydash.find_index(PERIODS, lambda value: value == period)
    return pydash.chain(PERIODS[x:]).filter_(lambda _, i: i % 2 == 0).value()


def get_Line_data(time_list, signal_list, high_list, low_list):
    resp = {'data': [], 'date': []}
    for i in range(0, len(time_list), 1):
        if signal_list[i] == 1:
            resp['data'].append(high_list[i])
            resp['date'].append(time_list[i])
        elif signal_list[i] == -1:
            resp['data'].append(low_list[i])
            resp['date'].append(time_list[i])
    return resp