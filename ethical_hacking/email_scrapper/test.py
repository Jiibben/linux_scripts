import string
a = [1,2,3,4]
b = [5,6,7,8]


print({i:j for i,j in zip(list(string.ascii_lowercase), [[] for i in range(0,26)])})