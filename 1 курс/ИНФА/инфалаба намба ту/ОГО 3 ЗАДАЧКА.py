x, m = map(int, input().split())
xx = x
s2 = m + 1
for i in range(m+1):
    if 2**i > x:
        s2 = i - 1
        break

if s2 <= m:
    if m != s2+1:
        for i in range(m - s2 - 1):
            print(0, end='')
    c = s2
    for i in range(s2, -1, -1):
        if 2**i <= xx < 2**(i+1):
            xx = xx - 2**i
            if c == i:
                print(1, end='')
        else:
            print(0, end='')
        c -= 1

else:
    print("ошибка")