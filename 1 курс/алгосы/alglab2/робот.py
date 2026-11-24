n, m = map(int, input().split())
a = [input() for _ in range(n)]
for i in range(n):
    for j in range(m):
        if a[i][j] == 'S':
            start = (i, j)
            break
moves = {
    'U': (-1, 0),
    'D': (1, 0),
    'L': (0, -1),
    'R': (0, 1),
}
prev = (0, 0)
cur = start
path = []
while True:
    r, c = cur
    for ch, (i, j) in moves.items():
        next_i, next_j = r + i, c + j
        if not(0 <= next_i < n and 0 <= next_j <= m): continue
        if a[next_i][next_j] in '*S' and (next_i, next_j) != prev:
            path.append(ch)
            prev = cur
            cur = (next_i, next_j)
            break
    if cur == start:
        break
print("".join(path))