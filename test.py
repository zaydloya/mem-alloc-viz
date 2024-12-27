import re


def to_kb(size, unit):
    mapping = {
        "KB": 1,
        "MB": 1000,
        "GB": 1000 ** 2
    }

    return size * mapping[unit]


def to_original(size, unit):
    mapping = {
        "KB": 1,
        "MB": 1000,
        "GB": 1000 ** 2
    }

    return size // mapping[unit]


def first_fit(partitions: list, processes: list):
    partitions = [{'partition': partition['size'],
                   'processes': [],
                   'remaining': partition['size_kb'],
                   'unit': partition['unit'],
                   'repr': partition['size'] + partition['unit']}
                  for partition in partitions]
    unsatisfied = []

    for process in processes:
        allocated = False
        for partition in partitions:
            if partition['remaining'] - process['size_kb'] >= 0:
                partition['processes'].append((process['size'], process['unit']))
                partition['remaining'] -= process['size_kb']
                allocated = True
                break
            else:
                continue
        if not allocated:
            unsatisfied.append((process['size'], process['unit']))

    for partition in partitions:
        partition['remaining'] = to_original(partition['remaining'], partition['unit'])
    return partitions, unsatisfied


def best_fit(partitions: list, processes: list):
    partitions = [{'partition': partition['size'],
                   'processes': [],
                   'remaining': partition['size_kb'],
                   'unit': partition['unit'],
                   'repr': partition['size'] + partition['unit']}
                  for partition in partitions]
    unsatisfied = []

    for process in processes:
        diffs = [(i, partition['remaining'] - process['size_kb']) for i, partition in enumerate(partitions)
                 if partition['remaining'] - process['size_kb'] >= 0]
        if diffs:
            best, _ = min(diffs, key=lambda x: x[1])
            partitions[best]['processes'].append((process['size'], process['unit']))
            partitions[best]['remaining'] -= process['size_kb']
        else:
            unsatisfied.append((process['size'], process['unit']))

    for partition in partitions:
        partition['remaining'] = to_original(partition['remaining'], partition['unit'])
    return partitions, unsatisfied


def worst_fit(partitions: list, processes: list):
    partitions = [{'partition': partition['size'],
                   'processes': [],
                   'remaining': partition['size_kb'],
                   'unit': partition['unit'],
                   'repr': partition['size'] + partition['unit']}
                  for partition in partitions]
    unsatisfied = []

    for process in processes:
        diffs = [(i, partition['remaining'] - process['size_kb']) for i, partition in enumerate(partitions)
                 if partition['remaining'] - process['size_kb'] >= 0]
        if diffs:
            worst, _ = max(diffs, key=lambda x: x[1])
            partitions[worst]['processes'].append((process['size'], process['unit']))
            partitions[worst]['remaining'] -= process['size_kb']
        else:
            unsatisfied.append((process['size'], process['unit']))

    for partition in partitions:
        partition['remaining'] = to_original(partition['remaining'], partition['unit'])
    return partitions, unsatisfied


def process_input(partproc: list):
    pattern = r"^\s*(\d+)\s*(KB|MB|GB)?\s*$"
    processed = []
    for i in partproc:
        match = re.match(pattern, i)
        if match:
            size = int(match.group(1))
            unit = match.group(2).upper() if match.group(2) else 'MB'
            size_kb = to_kb(size, unit)

            processed.append({'size': size, 'size_kb': size_kb, 'unit': unit})
        else:
            return False

    return processed

def main():
    partitions = ['350MB', '300MB']
    processes = ['100MB', '200MB', '50KB', '200MB']
    print(first_fit(process_input(partitions), process_input(processes)))
    print(best_fit(process_input(partitions), process_input(processes)))
    print(worst_fit(process_input(partitions), process_input(processes)))

main()