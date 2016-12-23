import matplotlib.pyplot as plt

# For unigrams : 2b
# filename = "graph_2b.csv"
# title = 'Rank vs Frequency for Unigrams'

# For ending unigrams  : 2c
filename1 = "graph_author1__real_sold.csv"
filename2 = "graph_author2__Famous.csv"
filename3 = "graph_author3__Representative.csv"

title = "Log(freq) vs Log(rank) for 3 authors for 1-gram"

X1, Y1, X2, Y2, X3, Y3 = [], [], [], [], [], []
with open(filename1) as f:
    data1 = f.readlines()
with open(filename2) as f:
    data2 = f.readlines()
with open(filename3) as f:
    data3 = f.readlines()


count = 1
for i in data1:
    [x, y] = i.strip().split()
    X1.append(x)
    Y1.append(y)
count = 1
for i in data2:
    [x, y] = i.strip().split()
    X2.append(x)
    Y2.append(y)
count = 1
for i in data3:
    [x, y] = i.strip().split()
    X3.append(x)
    Y3.append(y)
    # # Plot first 100 points only
    # count += 1
    # if count >= 100:
    #     break

# plot with various axes scales
plt.figure(1)
plt.title(title)
plt.plot(X1, Y1, 'r--', X2, Y2, "b--", X3, Y3, "m--")
# plt.axis([0, 6, 0, 20])
plt.grid()
plt.show()
