t = int(input())
for _ in range(t):
    n, k = map(int, input().split())
    if k < n-1: print(n)
    else: print(1)