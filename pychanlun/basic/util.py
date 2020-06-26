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