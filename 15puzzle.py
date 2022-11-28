from random import choice
from collections import deque
import numpy as np
import time

# bfs sa obe strane da bi se minimizovalo rasireno grananje

dy = [-1, 0, 0, 1]
dx = [0, -1, 1, 0]
dname = ["U", "L", "R", "D"]
directions = list(zip(dy, dx, dname))
reverse_dir = {"U": "D", "L": "R", "R": "L", "D": "U"}


def legit(y, x, m, n):
    return y >= 0 and y < m and x >= 0 and x < n


def find0(matrix):
    a = np.where(matrix == 0)
    return (a[0][0], a[1][0])


def make_end_pos(m, n):
    end_pos = []
    for i in range(m):
        lst = []
        for j in range(n):
            num = i * n + j + 1
            lst.append(num)
        end_pos.append(lst)
    end_pos[m - 1][n - 1] = 0
    return np.array(end_pos, np.int8)


def make_random_start_pos(m, n, shuffle_count=1000):
    pos = make_end_pos(m, n)
    c0y, c0x = m - 1, n - 1
    for _ in range(shuffle_count):
        dy, dx, dn = choice(directions)
        n0y = c0y + dy
        n0x = c0x + dx
        if legit(n0y, n0x, m, n):
            pos[c0y][c0x], pos[n0y][n0x] = pos[n0y][n0x], pos[c0y][c0x]
            c0y, c0x = n0y, n0x
    return np.array(pos, np.int8)


class State:
    def __init__(self, parent, matrix, zero_pos, last_move):
        self.parent = parent
        self.matrix = matrix
        self.zero_pos = zero_pos
        self.last_move = last_move

    def create_children(self):
        m, n = self.matrix.shape
        c0y, c0x = self.zero_pos
        for dy, dx, dname in directions:
            n0y = c0y + dy
            n0x = c0x + dx
            if legit(n0y, n0x, m, n):
                n_mat = np.copy(self.matrix)
                n_mat[n0y][n0x], n_mat[c0y][c0x] = n_mat[c0y][c0x], n_mat[n0y][n0x]
                yield State(self, n_mat, (n0y, n0x), dname)

    def print_matrix(self):
        print("-" * 50)
        for row in self.matrix:
            print("\t".join(map(str, row.tolist())))

    def __hash__(self):
        return hash(self.matrix.data.tobytes())

    def __eq__(self, other):
        return np.array_equal(self.matrix, other.matrix)


def solve(start_pos):
    m, n = start_pos.shape
    end_pos = make_end_pos(m, n)
    start_state = State(None, start_pos, find0(start_pos), "_start_")
    print("Starting position:")
    start_state.print_matrix()
    end_state = State(None, end_pos, find0(end_pos), "_end_")
    end_state.print_matrix()
    last_level1 = [start_state]
    last_level2 = [end_state]
    record1 = dict()
    record1[start_state] = start_state
    record2 = dict()
    record2[end_state] = end_state

    intersection = None
    while len(last_level1) + len(last_level2) > 0:
        print(f"shallow copies = {len(record1)+len(record2)}")
        new_level1 = []
        for state in last_level1:
            if intersection is not None:
                break
            for child in state.create_children():
                if child in record1:
                    continue
                record1[child] = child
                if child in record2:
                    intersection = child
                    break
                new_level1.append(child)
        last_level1 = new_level1

        new_level2 = []
        for state in last_level2:
            if intersection is not None:
                break
            for child in state.create_children():
                if child in record2:
                    continue
                record2[child] = child
                if child in record1:
                    intersection = child
                    break
                new_level2.append(child)
        last_level2 = new_level2

    if intersection is None:
        print("No solution found")
        return None

    lst1 = []
    curr = record1[intersection]
    while curr is not None:
        lst1.append(curr)
        curr = curr.parent
    lst1 = lst1[::-1]

    lst2 = []
    curr = record2[intersection]
    while curr is not None:
        lst2.append(curr)
        curr = curr.parent

    print_flag = False
    if print_flag:
        for state in lst1:
            state.print_matrix()
        for state in lst2[1:]:
            state.print_matrix()

    moves = []
    for state in lst1[1:]:
        moves.append(state.last_move)
    for state in lst2[:-1]:
        move = reverse_dir[state.last_move]
        moves.append(move)
    print(f"{len(moves) = }")
    print("".join(moves))


if __name__ == "__main__":
    m, n = map(int, input("Enter dimension (M N): ").split())

    op = 0
    while op < 1 or op > 2:
        op = int(input("Auto generate matrix (1) or input a matrix (2): "))
        if op == 1:
            start_pos = make_random_start_pos(m, n, 10000)
            # 10000, ubije program ili kompijuter posle 10M shallow kopija za 4x4
        elif op == 2:
            start_pos = np.array(
                [list(map(int, input(f"Row {i+1}: ").split())) for i in range(m)],
                np.int8,
            )
        else:
            print("Wrong input")
    start_t = time.time()
    solve(start_pos)
    end_t = time.time()
    print(f"Finished after {end_t - start_t}s")
