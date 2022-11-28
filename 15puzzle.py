from random import choice
import numpy as np
import time
from multiprocessing import Process
from functools import partial
from threading import Thread

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
    return np.array(end_pos, np.uint8)


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
    return np.array(pos, np.uint8)


class State:
    def __init__(self, parent, matrix, zero_pos, last_move):
        self.parent = parent
        self.matrix = matrix
        self.zero_pos = zero_pos
        self.last_move = last_move
        self.hash = self.hash_util()

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

    def hash_util(self):
        return hash(self.matrix.data.tobytes())

    def __hash__(self):
        return self.hash

    def __eq__(self, other):
        return self.hash == other.hash
        # return np.array_equal(self.matrix, other.matrix)


def solve(start_pos, print_flag=True):
    m, n = start_pos.shape
    end_pos = make_end_pos(m, n)
    start_state = State(None, start_pos, find0(start_pos), "_start_")
    print("Starting position:")
    start_state.print_matrix()
    end_state = State(None, end_pos, find0(end_pos), "_end_")
    print("Ending position")
    end_state.print_matrix()

    if start_state == end_state:
        print("Starting and ending positions are the same")
        return

    last_level1 = [start_state]
    last_level2 = [end_state]
    record1 = dict()
    record1[start_state] = start_state
    record2 = dict()
    record2[end_state] = end_state

    move_count = 0
    intersection = None
    while intersection is None and (len(last_level1) + len(last_level2)) > 0:
        print(f"moves {move_count+1}, {move_count+2}")
        move_count += 2
        print(f"shallow copies = {len(record1)+len(record2)}")

        def bfs_one_level(last_level, record):
            new_level = []
            for state in last_level:
                for child in state.create_children():
                    if child in record:
                        continue
                    record[child] = child
                    new_level.append(child)
            last_level.clear()
            last_level.extend(new_level)

        bfs1 = partial(bfs_one_level, last_level1, record1)
        bfs2 = partial(bfs_one_level, last_level2, record2)
        t1 = Thread(target=bfs1)
        t2 = Thread(target=bfs2)
        t1.start()
        t2.start()
        t1.join()
        t2.join()

        def find_intersection(last_level, other_record, intersection_mut):
            for state in last_level:
                if state in other_record:
                    intersection_mut[0] = state
                    return None

        tmp_mut = [None]
        intersection1 = partial(find_intersection, last_level1, record2, tmp_mut)
        intersection2 = partial(find_intersection, last_level2, record1, tmp_mut)
        t1 = Thread(target=intersection1)
        t2 = Thread(target=intersection2)
        t1.start()
        t2.start()
        t1.join()
        t2.join()
        intersection = tmp_mut[0]

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

    def print_game(lst1, lst2):
        for state in lst1:
            state.print_matrix()
        for state in lst2[1:]:
            state.print_matrix()
            # [1: ] zato sto je zadnji u prvoj dodat 2 puta

    if print_flag:
        print_game(lst1, lst2)

    moves = []
    for state in lst1[1:]:
        moves.append(state.last_move)
    for state in lst2[:-1]:
        move = reverse_dir[state.last_move]
        moves.append(move)
    print(f"{len(moves)} moves")
    print("".join(moves))


def main():
    m, n = map(int, input("Enter dimension (M N): ").split())

    op = 0
    while op not in [1, 2]:
        op = int(input("Auto generate matrix (1) or input a matrix (2): "))
    if op == 1:
        def_sc = 100
        shuffle_ans = input(f"Enter shuffle count (default {def_sc}): ")
        shuffle_count = def_sc if (shuffle_ans == "") else int(shuffle_ans)
        start_pos = make_random_start_pos(m, n, shuffle_count)
    elif op == 2:
        start_pos = np.array(
            [list(map(int, input(f"Row {i+1}: ").split())) for i in range(m)],
            np.uint8,
        )
    print_ans = "_"
    while print_ans not in ["y", "n"]:
        print_ans = input("Print move by move? (y/n): ")

    start_t = time.time()
    solve(start_pos=start_pos, print_flag=(print_ans == "y"))
    end_t = time.time()
    print(f"Took {round(end_t - start_t, 1)}s")


if __name__ == "__main__":
    main()
