n, t = map(int, input().split())
s = input()
s_list = list(s)
for _ in range(t):
        flag = False
        for i in range(len(s) - 1):
            if s_list[i] == 'B' and s_list[i + 1] == 'G' and not flag:
                s_list[i], s_list[i + 1] = s_list[i + 1], s_list[i]
                flag = True
            elif flag:
                flag = False
                continue
print(''.join(s_list))
