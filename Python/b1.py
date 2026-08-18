n, k = map(int, input().split())
a = set(list(map(int, input(). split())))
lst = list(a)
lst.sort()
ans = [0] * k
def back_track(i, start):
    if i == k:
        for j in ans:
            print(j, end = " ")
        print()
        return
    for j in range(start, len(lst)):
        ans[i] = lst[j]
        back_track(i+1, j+1)
back_track(0, 0)
