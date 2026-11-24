t = int(input())
for _ in range(t):

    n = int(input())
    a = list(map(int, input().split()))

    L = 0
    for i in range(n - 1):
        if a[i] > a[i + 1]:
            L = max(L, a[i] - a[i + 1])

    prev = a[0]
    for i in range(1, n):
        if a[i] >= prev:
            prev = a[i]
        elif a[i] + L >= prev:
            prev = a[i] + L
        else:
            print("NO")
            break
    else:
        print("YES")