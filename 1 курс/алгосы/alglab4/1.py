t = int(input())
for _ in range(t):
    n = int(input())
    res = [2 * i + 1 for i in range(n)]
    print(*res)