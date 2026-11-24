def prime(n):
    return n > 1 and all(n % i != 0 for i in range(2, int(n**0.5) + 1))

n = int(input())
for m in range(1, 10^3 + 1):
    if not prime(n*m+1):
        print(m)
        break