# n, k = map(int, input().split())

# a = list(map(int, input().split()))
# t = list(map(int, input().split()))
# max_t = 0
# for i in range(n):
#     if t[i] == 1: max_t += a[i]
#     else: 
#         first_zero = i
#         break

# for i in range(first_zero, n):
#     t_check = t
#     cur_max = 0
#     if t_check[i] == 0:
#         for j in range(i, i+k-1):
#             t_check[j] = 1
#     for j in range(i, n):
#         if t_check[j] == 1:
#             cur_max += a[j]
#             if cur_max > max_t:
#                 max_t = cur_max

# print(max_t)
        
