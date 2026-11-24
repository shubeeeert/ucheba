t = int(input())
for _ in range(t):
    n = int(input())
    p = list(map(int, input().split()))
 
    if n == 1:
        print(-1)
        continue
 
    used = [0] * n
    a = [0] * n
 
    for i in range(n):
        for j in range(n):
            if (j + 1 == p[i] and i != n - 1) or used[j]:
                continue
            a[i] = j + 1
            used[j] = True
            break
 
    if a[n - 1] == p[n - 1]:
        a[n - 1], a[n - 2] = a[n - 2], a[n - 1]
 
    print(*a)