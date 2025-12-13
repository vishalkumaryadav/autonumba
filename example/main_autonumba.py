from numba import njit
import warnings
from numba.core.errors import NumbaPerformanceWarning
warnings.simplefilter('ignore', category=NumbaPerformanceWarning)

import time
import random
from typing import List

@njit(cache=True, fastmath=True, parallel=True, nogil=True, boundscheck=True)
def matrix_heavy(n: int=200) -> List[List[float]]:
    a: List[List[float]] = [[random.random() for _ in range(n)] for _ in range(n)]
    b: List[List[float]] = [[random.random() for _ in range(n)] for _ in range(n)]
    c: List[List[float]] = [[0.0 for _ in range(n)] for _ in range(n)]
    for i in range(n):
        for j in range(n):
            for k in range(n):
                c[i][j] += a[i][k] * b[k][j]
    return c

@njit(cache=True, fastmath=True, parallel=True, nogil=True, boundscheck=True)
def fib(n: int) -> int:
    if n <= 1:
        return n
    return fib(n - 1) + fib(n - 2)

@njit(cache=True, fastmath=True, parallel=True, nogil=True, boundscheck=True)
def heavy_loop(n: int=1500) -> int:
    total: int = 0
    for i in range(n):
        for j in range(n):
            total += i * j % (j + 1)
    return total
if __name__ == '__main__':
    print('Running heavy Python demo...')
    start = time.time()
    mat_sum: float = sum((sum(row) for row in matrix_heavy(100)))
    print('Matrix multiply sum:', mat_sum)
    print('Matrix multiply done in', time.time() - start, 'seconds\n')
    start = time.time()
    fib_result: int = fib(35)
    print('Fibonacci(35):', fib_result)
    print('Fibonacci done in', time.time() - start, 'seconds\n')
    start = time.time()
    loop_result: int = heavy_loop(1000)
    print('Heavy loop result:', loop_result)
    print('Heavy loop done in', time.time() - start, 'seconds')