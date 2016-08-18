import matplotlib.pyplot as plt

# For unigrams : 2b
# filename = "graph_2b.csv"
# title = 'Rank vs Frequency for Unigrams'

# For ending unigrams  : 2c
filename = "graph_2c.csv"
title = "Rank vs Frequency for all Xs in P(X | </s>) [For UNIGRAMS]"



X, Y = [], []
with open(filename) as f:
    data = f.readlines()


count = 1
for i in data:
    [x, y] = i.strip().split()
    X.append(x)
    Y.append(y)
    # Plot first 100 points only
    count += 1
    if count >= 100:
        break

# plot with various axes scales
plt.figure(1)
plt.title(title)
plt.plot(X, Y, 'r--', X, Y, "bo")
# plt.axis([0, 6, 0, 20])
plt.grid()
plt.show()
