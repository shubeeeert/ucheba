t = int(input())
for _ in range(t):
    n = int(input())
    a = input().split()
    counts = {}
    for x in a:
        x = int(x)
        counts[x] = counts.get(x, 0) + 1
    freq = {}
    cost = {}

    for x, cnt in counts.items():
        curr = x
        d = 0
        seen = set()
        while curr not in seen:
            seen.add(curr)
            if curr not in freq:
                freq[curr] = cnt
                cost[curr] = d * cnt
            else:
                freq[curr] += cnt
                cost[curr] += d * cnt
            d += 1
            if curr % 2 == 0:
                curr //= 2
            else:
                curr += 1
                
    ans = -1
    for k, v in freq.items():
        if v == n:
            if ans == -1 or cost[k] < ans:
                ans = cost[k]
    print(ans)