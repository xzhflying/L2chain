# The optimization algorithm for witness cache
# Input: An array of state access frequencies
# Output: the partition of witness cache
import numpy as np
from itertools import combinations

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
    
    # inital for f(0, j, 2)
    for j in range(1, int(state_count/2)):
        table[0][j][2] = (j-1)*sum(freq[:j]) + (state_count - j - 1) * (sum(freq) - sum(freq[:j]))

    for i in range(int(state_count/3)):
        for j in range(i, int((state_count-i)/2)):
            table[i][j][2] = (i-1) * sum(freq[:i]) + (j-1) * sum(freq[i:(i+j)]) + (state_count-i-j-1) * sum(freq[(i+j):])

    for k in range(3, cache_count):
        for j in range(int(state_count/k)-1, 0, -1):
            par = table[j][j][k-1] + (j-1)*sum(freq[:j])
            non_par = table[0][j+1][k]
            table[0][j][k] = min(par, non_par)

    # TODO: partition
    

    return table


if __name__ == '__main__':
    state_count = 8
    cache_count = 3
    freq = np.random.uniform(0, 1, state_count)
    print(opt_partition(freq, state_count, cache_count))
    
    min_cost, part = bf_search(freq, state_count, cache_count)
    print(min_cost)
    print(part)
