import numpy as np


def same_parity(x, y):
    return (x % 2 == 0 and y % 2 == 0) or (x % 2 == 1 and y % 2 == 1)

def init_board(shape = (6, 6)):
    new_shape = (shape[0] * 2 - 1, shape[1] * 2 - 1)
    x = np.zeros(new_shape, dtype = np.int8)
    for i in range(len(x)):
        for j in range(len(x[i])):
            if same_parity(i + 1, j + 1):
                x[i][j] = 1
    return x

def pop_from_list(tar_list):
    item = tar_list[0]
    tar_list = tar_list[1:]
    return item, tar_list

x = [1,2,3,4]
print(x)
item, x = pop_from_list(x)
print(x)
print(item)