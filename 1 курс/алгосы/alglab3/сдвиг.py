t = int(input())
for _ in range(t):
    n = int(input())
    tt = input()
    result = []
    used = set()
    t_s = {}
    for ch_t in tt:
        if ch_t in t_s:
            result.append(t_s[ch_t])
        else:
            for code in range(ord('a'), ord('z') + 1):
                ch_s = chr(code)
                
                if ch_s in used:
                    continue
                    
                curr = ch_s
                while curr in t_s:
                    curr = t_s[curr]
                    
                if curr == ch_t and len(t_s) < 25:
                    continue
                    
                t_s[ch_t] = ch_s
                used.add(ch_s)
                result.append(ch_s)
                break
    print("".join(result))