import pydash

def FindPivots(from_idx, to_idx, duan_serial, high_serial, low_serial, direction):
    pivots = []
    if direction == -1:
        start = from_idx
        end = to_idx + 1
        sequence = []
        while True:
            d = pydash.find_index(duan_serial[start:end], lambda x: x == -1)
            if d == -1:
                break
            d = start + d
            if d >= to_idx:
                break
            g = pydash.find_index(duan_serial[d:end], lambda x: x == 1)
            if g == -1:
                break
            g = d + g
            sequence.append({ 'start': d, 'end': g, 'low': low_serial[d], 'high': high_serial[g] })
            start = g
        # 至少有2个特征序列才可能出现中枢
        if len(sequence) >= 2:
            pivot = { 'sequence_count': 0 }
            for idx in range(len(sequence)-1):
                if pivot['sequence_count'] == 0:
                    pivot['zg'] = sequence[idx]['high']
                    pivot['zd'] = sequence[idx]['low']
                    pivot['start'] = sequence[idx]['start']
                    pivot['end'] = sequence[idx]['end']
                    pivot['sequence_count'] = 1
                elif pivot['sequence_count'] == 1:
                    zg = min(sequence[idx]['high'], pivot['zg'])
                    zd = max(sequence[idx]['low'], pivot['zd'])
                    if zg >= zd:
                        pivot['zg'] = zg
                        pivot['zd'] = zd
                        pivot['end'] = sequence[idx]['end']
                        pivot['sequence_count'] = pivot['sequence_count'] + 1
                    else:
                        pivot = { 'sequence_count': 0 }
                else:
                    if sequence[idx]['high'] >= pivot['zd'] and sequence[idx]['low'] <= pivot['zg']:
                        pivot['end'] = sequence[idx]['end']
                        pivot['sequence_count'] = pivot['sequence_count'] + 1
                    else:
                        pivots.append(pivot)
                        pivot = { 'sequence_count': 0 }
        elif direction == 1:
            start = from_idx
            end = to_idx + 1
            sequence = []
            while True:
                g = pydash.find_index(duan_serial[start:end], lambda x: x == 1)
                if g == -1:
                    break
                g = start + g
                if g >= to_idx:
                    break
                d = pydash.find_index(duan_serial[g:end], lambda x: x == -1)
                if d == -1:
                    break
                d = g + d
                sequence.append({ 'start': g, 'end': d, 'low': low_serial[d], 'high': high_serial[g] })
                start = g
            # 至少有2个特征序列才可能出现中枢
            if len(sequence) >= 2:
                pivot = { 'sequence_count': 0 }
                for idx in range(len(sequence)-1):
                    if pivot['sequence_count'] == 0:
                        pivot['zg'] = sequence[idx]['high']
                        pivot['zd'] = sequence[idx]['low']
                        pivot['start'] = sequence[idx]['start']
                        pivot['end'] = sequence[idx]['end']
                        pivot['sequence_count'] = 1
                    elif pivot['sequence_count'] == 1:
                        zg = min(sequence[idx]['high'], pivot['zg'])
                        zd = max(sequence[idx]['low'], pivot['zd'])
                        if zg >= zd:
                            pivot['zg'] = zg
                            pivot['zd'] = zd
                            pivot['end'] = sequence[idx]['end']
                            pivot['sequence_count'] = pivot['sequence_count'] + 1
                        else:
                            pivot = { 'sequence_count': 0 }
                    else:
                        if sequence[idx]['high'] >= pivot['zd'] and sequence[idx]['low'] <= pivot['zg']:
                            pivot['end'] = sequence[idx]['end']
                            pivot['sequence_count'] = pivot['sequence_count'] + 1
                        else:
                            pivots.append(pivot)
                            pivot = { 'sequence_count': 0 }

    return pivots
