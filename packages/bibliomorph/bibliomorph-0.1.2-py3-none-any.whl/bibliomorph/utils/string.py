from typing import Iterable, Mapping
import numpy as np
from rapidfuzz import fuzz
from scipy.optimize import linear_sum_assignment


def count_strings(strings: Iterable[str]):
    counts = {}
    for string in strings:
        if string not in counts:
            counts[string] = 0
        counts[string] += 1
    return sorted(counts.items(), key=lambda x: x[1], reverse=True)


def longest_common_string(strings: Iterable[str]):
    shortest = min(strings, key=len)
    left, right = 0, len(shortest)

    def is_common(substr):
        return all(substr in s for s in strings)

    best = ""
    while left <= right:
        mid = (left + right) // 2
        found = None
        for i in range(len(shortest) - mid + 1):
            candidate = shortest[i : i + mid]
            if is_common(candidate):
                found = candidate
                break
        if found:
            best = found
            left = mid + 1
        else:
            right = mid - 1
    return best
