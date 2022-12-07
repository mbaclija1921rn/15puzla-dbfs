from random import choice
import numpy as np
import time
from functools import partial
from threading import Thread
import math
from typing import Tuple

dy = [-1, 0, 0, 1]
dx = [0, -1, 1, 0]
dname = ["U", "L", "R", "D"]
directions = list(zip(dy, dx, dname))
reverse_dir = {"U": "D", "L": "R", "R": "L", "D": "U"}


def valid(y: int, x: int, m: int, n: int) -> bool:
    return y >= 0 and y < m and x >= 0 and x < n


def find0(matrix: np.ndarray) -> Tuple[int, int]:
    a = np.where(matrix == 0)
    return (a[0][0], a[1][0])


def make_end_pos(m: int, n: int) -> np.ndarray:
    end_pos = []
    for i in range(m):
        lst = []
        for j in range(n):
            num = i * n + j + 1
            lst.append(num)
        end_pos.append(lst)
    end_pos[m - 1][n - 1] = 0
    return np.array(end_pos, np.uint8)


def make_random_start_pos(m: int, n: int, shuffle_count: int = 1000) -> np.ndarray:
    pos = make_end_pos(m, n)
    c0y, c0x = m - 1, n - 1
    for _ in range(shuffle_count):
        dy, dx, dn = choice(directions)
        n0y = c0y + dy
        n0x = c0x + dx
        if valid(n0y, n0x, m, n):
            pos[c0y][c0x], pos[n0y][n0x] = pos[n0y][n0x], pos[c0y][c0x]
            c0y, c0x = n0y, n0x
    return np.array(pos, np.uint8)


class State:
    counter = 0

    def __init__(self, parent, matrix, zero_pos, last_move):
        State.counter += 1
        self.id = State.counter
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
            if valid(n0y, n0x, m, n):
                n_mat = np.copy(self.matrix)
                n_mat[n0y][n0x], n_mat[c0y][c0x] = n_mat[c0y][c0x], n_mat[n0y][n0x]
                yield State(self, n_mat, (n0y, n0x), dname)

    def print_matrix(self):
        cnt = self.matrix.shape[1] * 8 - 7 + int(math.log10((self.matrix.size - 1)))
        print("-" * cnt)
        for row in self.matrix:
            str0X = lambda e: "X" if e == 0 else str(e)
            print("\t".join(map(str0X, row.tolist())))

    def print(self):
        parent_id = None if self.parent is None else self.parent.id
        print(f"last move = {self.last_move}")
        print(f"id = {self.id}")
        print(f"parent_id = {parent_id}")
        self.print_matrix()

    def hash_util(self):
        return hash(self.matrix.data.tobytes())

    def __hash__(self):
        return self.hash

    def __eq__(self, other):
        return self.hash == other.hash
        # return np.array_equal(self.matrix, other.matrix)


def solve(
    start_pos: np.ndarray, print_move_by_move: bool = True, print_trees: bool = False
):
    m, n = start_pos.shape
    end_pos = make_end_pos(m, n)
    start_state = State(None, start_pos, find0(start_pos), "_start_")
    print("Start state (Tree 1 root)")
    start_state.print()
    print()
    end_state = State(None, end_pos, find0(end_pos), "_end_")
    print("End state (Tree 2 root)")
    end_state.print()
    print()
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
        node_cnt = len(record1) + len(record2)
        print(f"Moves {move_count+1}, {move_count+2}: Nodes {node_cnt}")
        move_count += 2

        def bfs_one_level(last_level: list, record: dict):
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

        def find_intersection(
            last_level: list, other_record: dict, intersection_mut: list
        ):
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

        def print_level(title: str, level: list):
            print(title)
            for state in level:
                state.print()
                print()

        if print_trees:
            print_level(
                title=f"Tree 1, Move {move_count//2}, Nodes {len(last_level1)}",
                level=last_level1,
            )
            print("=" * 70)
            print_level(
                title=f"Tree 2, Move {move_count//2}, Nodes {len(last_level2)}",
                level=last_level2,
            )
            print("=" * 70)

    if intersection is None:
        print("No solution found")
        return None

    if print_trees:
        print("Intersection:")
        id1 = record1[intersection].id
        id2 = record2[intersection].id
        print(f"ids ({id1}, {id2})")
        intersection.print_matrix()

    path1 = []
    curr = record1[intersection]
    while curr is not None:
        path1.append(curr)
        curr = curr.parent
    path1 = path1[::-1]

    path2 = []
    curr = record2[intersection]
    while curr is not None:
        path2.append(curr)
        curr = curr.parent

    def print_game(path1: list, path2: list):
        print()
        print("Moves of the game:")
        for state in path1:
            state.print_matrix()
        for state in path2[1:]:
            state.print_matrix()
            # [1: ] zato sto je zadnji u prvoj isti kao prvi u drugoj

    if print_move_by_move:
        print_game(path1, path2)

    print(f"\n{len(record1) + len(record2)} nodes saved")
    print(f"{State.counter} nodes initialized")

    moves = []
    for state in path1[1:]:
        moves.append(state.last_move)
    for state in path2[:-1]:
        move = reverse_dir[state.last_move]
        moves.append(move)
    print(f"{len(moves)} moves long solution:")
    print("".join(moves))


def main():
    m, n = map(int, input("Enter dimension (M N): ").split())

    op = "_"
    while op not in ["1", "2"]:
        inp = input("Auto generate matrix (1-default) or input a matrix (2): ").strip()
        op = "1" if inp == "" else inp
    if op == "1":
        def_sc = 100
        shuffle_ans = input(f"Enter shuffle count ({def_sc}-default): ").strip()
        shuffle_count = def_sc if shuffle_ans == "" else int(shuffle_ans)
        start_pos = make_random_start_pos(m, n, shuffle_count)
    elif op == "2":
        intX0 = lambda e: 0 if e == "X" or e == "x" else int(e)
        start_pos = np.array(
            [list(map(intX0, input(f"Row {i+1}: ").split())) for i in range(m)],
            np.uint8,
        )

    print_mbm_ans = "_"
    while print_mbm_ans not in ["y", "n"]:
        print_mbm_ans = input("Print move by move? (Y/n): ").lower().strip()
        if print_mbm_ans == "":
            print_mbm_ans = "y"

    print_tree_ans = "-"
    while print_tree_ans not in ["y", "n"]:
        print_tree_ans = input("Print trees? (y/N): ").lower().strip()
        if print_tree_ans == "":
            print_tree_ans = "n"

    start_t = time.time()
    solve(
        start_pos=start_pos,
        print_move_by_move=(print_mbm_ans == "y"),
        print_trees=(print_tree_ans == "y"),
    )
    end_t = time.time()
    print(f"Took {round(end_t - start_t, 2)}s")


if __name__ == "__main__":
    main()
