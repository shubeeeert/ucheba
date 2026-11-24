t = int(input())
for _ in range(t):
    n, k = map(int, input().split())
    a = set(map(int, input().split()))
    yes = False
    for i in a:
        if i + k in a:
            yes = True
            break
    if yes:
        print("YES")
    else:
        print("NO")