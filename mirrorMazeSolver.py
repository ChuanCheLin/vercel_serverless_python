"""
Copyright Chuan-Che (Eric) Lin.
"""

import numpy as np
import random


class MirrorMazeSolver:

    def __init__(self, monster_nums: dict, grid: np.ndarray, border_nums: dict = None, solution: np.ndarray = None):
        self.monster_nums = monster_nums  # dict store the num for each monster in the sequence of Z, V, G
        self.grid = grid  # 0 means empty slots, 1 is mirror "/" , 2 is mirror "\"
        self.border_nums = border_nums  # the border numbers given by the puzzle
        self.answer_list = []  # ordered and flattened border_nums in the sequence of ["top", "left", "bottom", "right"]
        self.all_path = []  # list of list, every sublist contains a path for each start point(border_num)
        self.empty_slots = []  # ordered list for coordinates of every empty slot
        self.monster_position = {}  # current status for what monster in each slot
        self.monster_position_determined = {}  # monsters determined in advance by solving strategies
        self.height, self.width = grid.shape
        self.final_grid = solution  # when using generator, we got one solution from the generating process
        self.solutions = []  # cumulative solutions for the given puzzle

        # for debugging only: check element in each position
        # for i, row in enumerate(grid):
        #     for j, elem in enumerate(row):
        #         print(f"Element at ({i}, {j}) is {elem}")

        # generate all the path for each border num
        self.path_finder()
        # print(self.all_path)

        # when we are using the generator
        if not border_nums:
            self.border_nums = self.generate_border_nums(solution)

        # generate the answer_list
        for values in self.border_nums.values():
            for val in values:
                self.answer_list.append(val)
        # print(self.answer_list)


    def path_finder(self) -> None:
        """
        generate the path for each border num, which is also all the path we need to check whether the puzzle is valid
        or not
        :return: None
        >>> puzzle_2x2 = ({"Z": 1, "V": 1, "G": 1}, [[0, 2], [0, 0]], {"top": [1, 0], "left": [1, 2], "bottom": [1, 2], "right": [0, 2]})
        >>> MS_test = MirrorMazeSolver(puzzle_2x2[0], np.array(puzzle_2x2[1]), puzzle_2x2[2])
        >>> MS_test.all_path
        [[[(0, 0), False], [(1, 0), False]], [], [[(0, 0), False], [(1, 1), True]], [[(1, 0), False], [(1, 1), False]], [[(1, 0), False], [(0, 0), False]], [[(1, 1), False], [(0, 0), True]], [], [[(1, 1), False], [(1, 0), False]]]

        """
        # dir: WASD for 4 directions
        all_dim = ["top", "left", "bottom", "right"]

        # every loop is a dimension
        for cur_dim in all_dim:
            if cur_dim == "top" or cur_dim == "bottom":
                length = self.width
            else:
                length = self.height
            # every loop is a path
            for i in range(length):
                # initial point and status for each path
                mirror_status = False
                cur_path = []
                if cur_dim == "top":
                    cur_x, cur_y = 0, i
                    cur_dir = "S"
                elif cur_dim == "left":
                    cur_x, cur_y = i, 0
                    cur_dir = "D"
                elif cur_dim == "bottom":
                    cur_x, cur_y = length - 1, i
                    cur_dir = "W"
                elif cur_dim == "right":
                    cur_x, cur_y = i, length - 1
                    cur_dir = "A"

                # each time, check if the light already get out of the maze
                while self.is_inside(cur_x, cur_y):
                    # add the cur_loc into the path if it is an empty slot
                    # print(cur_x, cur_y)
                    if self.grid[(cur_x, cur_y)] == 0:
                        cur_path.append([(cur_x, cur_y), mirror_status])
                        if cur_dir == "S":
                            cur_x += 1
                        elif cur_dir == "W":
                            cur_x -= 1
                        elif cur_dir == "A":
                            cur_y -= 1
                        elif cur_dir == "D":
                            cur_y += 1

                    # turn for two kinds of mirror
                    elif self.grid[(cur_x, cur_y)] == 1:
                        mirror_status = True
                        if cur_dir == "S":
                            cur_dir = "A"
                            cur_y -= 1
                        elif cur_dir == "A":
                            cur_dir = "S"
                            cur_x += 1
                        elif cur_dir == "D":
                            cur_dir = "W"
                            cur_x -= 1
                        elif cur_dir == "W":
                            cur_dir = "D"
                            cur_y += 1

                    elif self.grid[(cur_x, cur_y)] == 2:
                        mirror_status = True
                        if cur_dir == "S":
                            cur_dir = "D"
                            cur_y += 1
                        elif cur_dir == "D":
                            cur_dir = "S"
                            cur_x += 1
                        elif cur_dir == "W":
                            cur_dir = "A"
                            cur_y -= 1
                        elif cur_dir == "A":
                            cur_dir = "W"
                            cur_x -= 1

                self.all_path.append(cur_path)

    def is_inside(self, x, y):
        """
        Check if the point (x, y) is inside the bounds of the grid.

        :param x: The x-coordinate of the point.
        :param y: The y-coordinate of the point.
        :return: True if the point is inside the grid, False otherwise.
        >>> puz_2x2 = ({"Z": 1, "V": 1, "G": 1}, [[0, 2], [0, 0]], {"top": [1, 0], "left": [1, 2], "bottom": [1, 2], "right": [0, 2]})
        >>> ms = MirrorMazeSolver(puz_2x2[0], np.array(puz_2x2[1]), puz_2x2[2])
        >>> ms.is_inside(0, 0)
        True
        >>> ms.is_inside(-1, 0)
        False
        >>> ms.is_inside(0, 2)
        False
        """
        num_rows, num_cols = self.grid.shape
        return 0 <= x < num_rows and 0 <= y < num_cols

    def deterministic_zero_border_value(self) -> None:
        """
        >>> puz_2x2 = ({"Z": 1, "V": 1, "G": 1}, [[0, 2], [0, 0]], {"top": [1, 0], "left": [0, 2], "bottom": [1, 2], "right": [0, 2]})
        >>> ms = MirrorMazeSolver(puz_2x2[0], np.array(puz_2x2[1]), puz_2x2[2])
        >>> ms.deterministic_zero_border_value()
        >>> print(ms.monster_position_determined)
        {(0, 0): 'G', (1, 1): 'V'}
        """
        for i in range(len(self.all_path)):
            # print(self.all_path[i], self.answer_list[i])
            if self.answer_list[i] == 0:
                # means that the border value (clue) is zero, so the ones after mirror got to be V, otherwise, G
                for cell in self.all_path[i]:
                    position, mirror_status = cell[0], cell[1]
                    if position not in self.monster_position_determined:
                        # avoid the same position again, it would cause bugs due to the incorrect monster_nums
                        if mirror_status:
                            self.monster_position_determined[position] = "V"
                            self.monster_nums["V"] -= 1
                        else:
                            self.monster_position_determined[position] = "G"
                            self.monster_nums["G"] -= 1

    def deterministic_surrounded_by_mirror(self):
        """
        example:
        / \
        \ Z
        >>> puz_2x2 = ({"Z": 1, "V": 0, "G": 0}, [[1, 2], [2, 0]], {"top": [0, 0], "left": [0, 0], "bottom": [0, 2], "right": [0, 2]})
        >>> ms = MirrorMazeSolver(puz_2x2[0], np.array(puz_2x2[1]), puz_2x2[2])
        >>> ms.deterministic_surrounded_by_mirror()
        >>> print(ms.monster_position_determined)
        {(1, 1): 'Z'}
        """
        for i in range(len(self.all_path)):
            if len(self.all_path[i]) == 2 and self.answer_list[i] == 2:
                if self.all_path[i][0][0] == self.all_path[i][1][0]:
                    position = self.all_path[i][0][0]
                    if position not in self.monster_position_determined:
                        self.monster_position_determined[position] = "Z"
                        self.monster_nums["Z"] -= 1

    def fill_one_slot(self) -> bool:
        """
        Fill one empty slot at a time, always fill in the zombies first because that can eliminate impossible solutions
        quicker. Then, the sequence of vampire or ghost should not matter, I choose to fill in vampire first in my code.

        :return: True means the maze is full
        the return boolean is used to decide to use check_puzzle() or check_full_puzzle()
        """
        for i in range(len(self.empty_slots)):
            slot = self.empty_slots[i]
            if slot not in self.monster_position:
                if self.monster_nums["Z"]:
                    self.monster_position[slot] = "Z"
                    self.monster_nums["Z"] -= 1
                    if i == len(self.empty_slots) - 1:
                        return True
                    return False
                elif self.monster_nums["V"]:
                    self.monster_position[slot] = "V"
                    self.monster_nums["V"] -= 1
                    if i == len(self.empty_slots) - 1:
                        return True
                    return False
                elif self.monster_nums["G"]:
                    self.monster_position[slot] = "G"
                    self.monster_nums["G"] -= 1
                    if i == len(self.empty_slots) - 1:
                        return True
                    return False
        return True

    def backtrack(self) -> None:
        """
        As the name suggest, this function serves to backtrack the status of the puzzle to the previous state. In the
        meantime, it also helps to maintain the monster_nums, the remaining monster we have. The logic is simple. We pop
        the last item we put in to the monster_position, a dict that keeps track of the current status for what monster
        in each slot.
        IF we tried zombie last time, we will try vampire then ghost, respectively. Also, we can only fill in the
        monster type if they still remains.
        AND if we have tried ghost in the last item in monster_position, it suggests that the one before the last
        item is also wrong, so we have to backtrack again.
        :return:
        """
        if len(self.monster_position) == 0:
            raise ValueError('Backtracked all the way to beginning. No more solutions.')
        pos, monster = self.monster_position.popitem()
        self.monster_nums[monster] += 1
        if monster == "Z":
            if self.monster_nums["V"]:
                self.monster_position[pos] = "V"
                self.monster_nums["V"] -= 1
                return
            elif self.monster_nums["G"]:
                self.monster_position[pos] = "G"
                self.monster_nums["G"] -= 1
                return
            else:
                self.backtrack()
        elif monster == "V":
            if self.monster_nums["G"]:
                self.monster_position[pos] = "G"
                self.monster_nums["G"] -= 1
                return
            else:
                self.backtrack()
        elif monster == "G":
            self.backtrack()

        else:
            print("Error! Every monster should be Z, V ,or G")

    def generate_border_nums(self, solution_grid) -> dict:
        all_num = []
        for i, path in enumerate(self.all_path):
            cur_num = 0  # the num of monster we can see along the path

            if not path:
                pass
            else:
                for e in path:
                    # e[0] => coordinates, e[1] => mirror_status
                    monster = solution_grid[e[0]]
                    if monster == "Z":
                        cur_num += 1
                    elif monster == "G" and e[1]:
                        cur_num += 1
                    elif monster == "V" and not e[1]:
                        cur_num += 1
            all_num.append(cur_num)

        border_num = {}

        all_dim = ["top", "left", "bottom", "right"]
        for cur_dim in all_dim:
            if cur_dim == "top":
                border_num["top"] = all_num[:self.width]
            elif cur_dim == "left":
                border_num["left"] = all_num[self.width:self.width+self.height]
            elif cur_dim == "bottom":
                border_num["bottom"] = all_num[self.width+self.height:2*self.width+self.height]
            elif cur_dim == "right":
                border_num["right"] = all_num[2*self.width+self.height:2*self.width+2*self.height]

        return border_num

    def check_puzzle(self) -> bool:
        """
        This function only check the non-full puzzle.
        The difference between this and check_full_puzzle() is that this functions check larger than (>) while the
        check_full_puzzle() needs exact matches on every path.

        :return: True means that every path have exceeded their given value (we kept it in the self.answer_list)
        """
        for i, path in enumerate(self.all_path):
            cur_num = 0  # the num of monster we can see along the path, compare this to the answer we have
            ans = self.answer_list[i]  # the correct number that we should see along this path

            if not path:
                if ans:
                    return False
            else:
                for e in path:
                    # e[0] => coordinates, e[1] => mirror_status
                    if e[0] in self.monster_position:
                        monster = (self.monster_position[e[0]])
                    elif e[0] in self.monster_position_determined:
                        monster = (self.monster_position_determined[e[0]])
                    else:
                        continue  # means that we haven't filled the slot yet
                    if monster == "Z":
                        cur_num += 1
                    elif monster == "G" and e[1]:
                        cur_num += 1
                    elif monster == "V" and not e[1]:
                        cur_num += 1
            if cur_num > ans:
                return False

        return True

    def check_full_puzzle(self) -> bool:
        """
        see check_puzzle()
        """
        for i, path in enumerate(self.all_path):
            # print(path, self.answer_list[i])
            # print(path)
            cur_num = 0  # the num of monster we can see along the path, compare this to the answer we have
            ans = self.answer_list[i]  # the correct number that we should see along this path

            if not path:
                if ans:
                    return False
            else:
                for e in path:
                    # e[0] => coordinates, e[1] => mirror_status
                    if e[0] in self.monster_position:
                        monster = (self.monster_position[e[0]])
                    elif e[0] in self.monster_position_determined:
                        monster = (self.monster_position_determined[e[0]])
                    else:
                        raise ValueError("Every empty slot should have a monster in it.")

                    if monster == "Z":
                        cur_num += 1
                    elif monster == "G" and e[1]:
                        cur_num += 1
                    elif monster == "V" and not e[1]:
                        cur_num += 1
            if cur_num != ans:
                return False

        return True


    def write_answer_puzzle_to_file(self, file_path: str) -> None:
        """
        Write out the final answer of the mirror maze to a file.
        :param file_path: The path of the file where to save the final answer.
        :return: None
        """
        if self.final_grid is None:
            final_grid = self.grid.astype(str)

            for i, row in enumerate(final_grid):
                for j, elem in enumerate(row):
                    if elem == "0":
                        if (i, j) in self.monster_position:
                            final_grid[i, j] = str(self.monster_position[(i, j)])
                        else:
                            final_grid[i, j] = str(self.monster_position_determined[(i, j)])
                    elif elem == "1":
                        final_grid[i][j] = "/"
                    elif elem == "2":
                        final_grid[i, j] = "\\"
        else:
            final_grid = self.final_grid

        with open(file_path, 'w') as file:
            for row in final_grid:
                file.write(' '.join(row) + '\n')

    def find_solutions(self, det: bool = False):
        """
        Solve the puzzle by brute-force using backtracking.
        :param det: We can choose whether we want to use the deterministic solving strategies or not by changing det
        :return:
        """
        # before generating empty solt, we can eliminate some slots using deterministic solving strategies
        if det:
            self.deterministic_zero_border_value()
            self.deterministic_surrounded_by_mirror()
            # print(self.monster_position_determined)

        # generate the list of empty slots
        for i, row in enumerate(self.grid):
            for j, elem in enumerate(row):
                if (i, j) not in self.monster_position_determined and elem == 0:
                    self.empty_slots.append((i, j))

        while True:
            try:
                is_full = self.fill_one_slot()
                # print(self.monster_position)
                if self.check_puzzle():
                    if is_full:
                        if self.check_full_puzzle():
                            # print(self.monster_position)
                            self.solutions.append(self.monster_position)
                            # print(self.solutions)
                            self.write_answer_puzzle_to_file("./answer.txt")
                        self.backtrack()
                else:
                    self.backtrack()
            except ValueError as ex:
                if ex.args[0] == 'Backtracked all the way to beginning. No more solutions.':
                    return
                else:
                    raise ex  # something unexpected happened.

def generate_puzzle(height: int, width: int):
    count = 1
    while True:
        print(f"puzzle #{count}")
        count += 1
        grid = np.zeros((height, width))

        # at least on quarter of the grid would be mirrors, at most halt the grid
        num_mirrors = random.randint(height * width // 4, height * width // 2)

        num = 0
        while num < num_mirrors:
            x, y = random.randint(0, height - 1), random.randint(0, width - 1)
            if grid[x, y] == 0:
                grid[x, y] = random.choice([1, 2])
                num += 1

        final_grid = grid.astype(str)  # the solution
        monster_nums = {}  # dict store the num for each monster in the sequence of Z, V, G

        # generate the solution grid using both numbers and visualized version
        for i, row in enumerate(grid):
            for j, elem in enumerate(row):
                if elem == 0:
                    rand = random.randint(3, 5)  # 3 is Z, 4 is V, 5 is G
                    if rand == 3:
                        final_grid[i, j] = "Z"
                        monster_nums["Z"] = monster_nums.get("Z", 0) + 1
                    elif rand == 4:
                        final_grid[i, j] = "V"
                        monster_nums["V"] = monster_nums.get("V", 0) + 1
                    elif rand == 5:
                        final_grid[i, j] = "G"
                        monster_nums["G"] = monster_nums.get("G", 0) + 1
                elif elem == 1:
                    final_grid[i][j] = "/"
                elif elem == 2:
                    final_grid[i, j] = "\\"
        if "Z" not in monster_nums:
            monster_nums["Z"] = 0
        if "V" not in monster_nums:
            monster_nums["V"] = 0
        if "G" not in monster_nums:
            monster_nums["G"] = 0

        ms_gen = MirrorMazeSolver(monster_nums, grid, None, final_grid)
        ms_gen.find_solutions(True)
        if len(ms_gen.solutions) == 1:
            for value in ms_gen.monster_position_determined.values():
                # return the monsters in the monster_position_determined to the total numbers
                ms_gen.monster_nums[value] += 1
            break

    return {
        'monster_nums': ms_gen.monster_nums,
        'border_nums': ms_gen.border_nums,
        'grid': ms_gen.grid.tolist(),  # Convert np.array to list for JSON serialization
        'solution': ms_gen.solutions  # Make sure this is in a format that can be JSON serialized
    }


if __name__ == '__main__':
    generate_puzzle(5, 5)