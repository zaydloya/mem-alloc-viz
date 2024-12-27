from django.shortcuts import render
from django import forms
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

    if size == 0:
        return size, unit
    elif size < mapping[unit] and unit == 'MB':
        return size, 'KB'
    elif size < mapping[unit] and unit == 'GB':
        return size // 1000, 'MB'

    return size // mapping[unit], unit


def first_fit(partitions: list, processes: list):
    partitions = [{'partition': partition['size'],
                   'unit': partition['unit'],
                   'processes': [],
                   'remaining': partition['size_kb'],
                   'size_kb': partition['size_kb'],
                   'label': f"{str(partition['size']) + partition['unit']}"}
                  for partition in partitions]
    unsatisfied = []

    for process in processes:
        allocated = False
        for partition in partitions:
            if partition['remaining'] - process['size_kb'] >= 0:
                partition['processes'].append({'process_size': process['size'],
                                               'process_unit': process['unit'],
                                               'process_label': f"{str(process['size']) + process['unit']}"
                                               })
                partition['remaining'] -= process['size_kb']
                allocated = True
                break
            else:
                continue
        if not allocated:
            unsatisfied.append({'process_size': process['size'],
                                'process_unit': process['unit'],
                                'process_label': f"{str(process['size']) + process['unit']}"
                                })

    for partition in partitions:
        size, unit = to_original(partition['remaining'], partition['unit'])
        partition['remaining'] = {'remaining_size': size, 'remaining_unit': unit}

    return partitions, unsatisfied


def best_fit(partitions: list, processes: list):
    partitions = [{'partition': partition['size'],
                   'unit': partition['unit'],
                   'processes': [],
                   'remaining': partition['size_kb'],
                   'size_kb': partition['size_kb'],
                   'label': f"{str(partition['size']) + partition['unit']}"}
                  for partition in partitions]
    unsatisfied = []

    for process in processes:
        diffs = [(i, partition['remaining'] - process['size_kb']) for i, partition in enumerate(partitions)
                 if partition['remaining'] - process['size_kb'] >= 0]
        if diffs:
            best, _ = min(diffs, key=lambda x: x[1])
            partitions[best]['processes'].append({'process_size': process['size'],
                                                  'process_unit': process['unit'],
                                                  'process_label': f"{str(process['size']) + process['unit']}"
                                                  })
            partitions[best]['remaining'] -= process['size_kb']
        else:
            unsatisfied.append({'process_size': process['size'],
                                'process_unit': process['unit'],
                                'process_label': f"{str(process['size']) + process['unit']}"
                                })

    for partition in partitions:
        size, unit = to_original(partition['remaining'], partition['unit'])
        partition['remaining'] = {'remaining_size': size, 'remaining_unit': unit}

    return partitions, unsatisfied


def worst_fit(partitions: list, processes: list):
    partitions = [{'partition': partition['size'],
                   'unit': partition['unit'],
                   'processes': [],
                   'remaining': partition['size_kb'],
                   'size_kb': partition['size_kb'],
                   'label': f"{str(partition['size']) + partition['unit']}"}
                  for partition in partitions]
    unsatisfied = []

    for process in processes:
        diffs = [(i, partition['remaining'] - process['size_kb']) for i, partition in enumerate(partitions)
                 if partition['remaining'] - process['size_kb'] >= 0]
        if diffs:
            worst, _ = max(diffs, key=lambda x: x[1])
            partitions[worst]['processes'].append({'process_size': process['size'],
                                                   'process_unit': process['unit'],
                                                   'process_label': f"{str(process['size']) + process['unit']}"
                                                   })
            partitions[worst]['remaining'] -= process['size_kb']
        else:
            unsatisfied.append({'process_size': process['size'],
                                'process_unit': process['unit'],
                                'process_label': f"{str(process['size']) + process['unit']}"
                                })

    for partition in partitions:
        size, unit = to_original(partition['remaining'], partition['unit'])
        partition['remaining'] = {'remaining_size': size, 'remaining_unit': unit}

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


class AllocationForm(forms.Form):
    partitions = forms.CharField(label="partitions")
    processes = forms.CharField(label="processes")


def index(request):
    return render(request, "mem-alloc/index.html", {"form": AllocationForm()})


def result(request):
    if request.method == "POST":
        form = AllocationForm(request.POST)
        if form.is_valid():
            partitions = process_input(list(re.split(r'[,\s]+', form.cleaned_data["partitions"])))
            processes = process_input(list(re.split(r'[,\s]+', form.cleaned_data["processes"])))

            first_fit_result, first_fit_unallocated = first_fit(partitions, processes)
            best_fit_result, best_fit_unallocated = best_fit(partitions, processes)
            worst_fit_result, worst_fit_unallocated = worst_fit(partitions, processes)

            context = {
                "partitions": partitions,
                "processes": processes,
                "first_fit_result": first_fit_result,
                "first_fit_unallocated": first_fit_unallocated,
                "best_fit_result": best_fit_result,
                "best_fit_unallocated": best_fit_unallocated,
                "worst_fit_result": worst_fit_result,
                "worst_fit_unallocated": worst_fit_unallocated,
            }

            return render(request, "mem-alloc/result.html", context)

    return render(request, "mem-alloc/index.html", {"form": AllocationForm(), "error": "Invalid input!"})
