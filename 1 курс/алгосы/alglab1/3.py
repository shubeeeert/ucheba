n = int(input())
k = 1
a = [int(a) for a in input().split()]
a = sorted(a)
 
for i in range(n):
    if k > a[i]:
        continue
    else:
        k=k+1

print(k - 1)