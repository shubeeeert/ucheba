import csv, sys, hashlib
import random as rnd

def h(name):
	return int(hashlib.sha1(name.encode("utf-8")).hexdigest(), 16) % (10 ** 9)

def task(td):
	res = []
	for t in td:
		res = res + rnd.sample(data[t[0]][1:], t[1])
	return res


def tasks(n):
	if n == 1:
		t = task([(0, 1), (1, 1), (2, 1), (3, 1), (4, 1)])
	if n == 2:
		t = task([(5, 2), (6, 1), (7, 1)])
	return("Ваш вариант: " + ", ".join(t))


reader = csv.reader(open("data.csv"), delimiter = ",")
data = []
for row in reader:
	row = [x for x in row if x != ""]
	data.append(row)

if len(sys.argv) != 3:
	exit()

name, n = sys.argv[1], int(sys.argv[2])
rnd.seed(h(name))
print(tasks(n))