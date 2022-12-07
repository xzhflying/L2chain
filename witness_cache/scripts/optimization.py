# The optimization algorithm for witness cache
# Input: An array of state access frequencies
# Output: the partition of witness cache
import numpy as np
from itertools import combinations
from math import floor

def bf_search(freq, state_count, cache_count):
    freq.sort()
    freq = freq[::-1]

    min_cost = np.inf
    for item in combinations(range(1, state_count), cache_count - 1):
        cost = 0
        for i in range(cache_count-1):
            ind = item[i]
            if i == 0:
                cost += sum(freq[:ind]) * (ind - 1)
            else:
                cost += sum(freq[item[i-1]:ind]) * (ind-item[i-1]-1)
        cost += sum(freq[ind:]) * (state_count-ind-1)
        if cost < min_cost:
            min_cost = cost
            partition = item
    return min_cost, partition

def opt_partition(freq, state_count, cache_count):
    freq.sort()
    freq = freq[::-1]

    partition = [[] for _ in range(cache_count)]
    table = np.array([[[np.inf for _ in range(cache_count)] for _ in range(state_count)] for _ in range(state_count)])
    
    for i in range(state_count):
        for j in range(state_count-i):
            table[i][j][0] = (state_count - i -1)*sum(freq[-(state_count - i ):])

    for k in range(1, cache_count):
        for i in range(state_count - 2, -1, -1):
            for j in range(int(floor((state_count-i)/(k+1))) - 1, -1, -1):
                # print("{},{},{}".format(i,j,k))
                par = table[i+j+1][j][k-1] + j*sum(freq[i:(i+j+1)])
                non_par = table[i][j+1][k]
                table[i][j][k] = min(par, non_par)

    # TODO: output partition
    
    return table


if __name__ == '__main__':
    state_count = 16
    cache_count = 3
    freq = np.random.uniform(0, 1, state_count)
    print(opt_partition(freq, state_count, cache_count)[0])
    
    min_cost, part = bf_search(freq, state_count, cache_count)

    print(min_cost)
    print(part)
