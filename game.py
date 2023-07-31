import numpy as np
import pdb

class Game:
    def __init__(self, shape = (6, 6)):
        self.shape = shape
        self.actual_shape = (shape[0] * 2 - 1, shape[1] * 2 - 1)
        self.init_valid_board = self.get_init_board()
        self.current_board = self.init_valid_board.copy()
        self.empty = 1
        self.black = 2
        self.white = 3
        self.turn = self.black
        self.game_end = False
        self.last_pass = False
        self.hist = []

    def get_game_state(self):
        state_dict = {}
        state_dict['board'] = self.current_board.copy()
        state_dict['turn'] = self.turn
        state_dict['str'] =  self.get_str_state()
        state_dict['game_end'] = self.game_end
        state_dict['last_pass'] = self.last_pass
        state_dict['hist'] = self.hist.copy()
        return state_dict
    
    def check_appeared(self, state):
        for s in self.hist:
            if state['str'] == s['str']:
                return True
            
        return False
    
    def get_str_state(self):
        return str(self.current_board) + ' ' + str(self.turn)
    
    def load_game_state(self, state_dict):
        self.current_board = state_dict['board'].copy()
        self.turn = state_dict['turn']
        self.game_end = state_dict['game_end']
        self.last_pass = state_dict['last_pass']
        self.hist = state_dict['hist'].copy()

    # Check if number x and y are both even or both odd
    def same_parity(self, x, y):
        return (x % 2 == 0 and y % 2 == 0) or (x % 2 == 1 and y % 2 == 1)
    
    # initialize array of valid actions, will auto consider placing stones in the middle of X
    def get_init_board(self):
        x = np.zeros(self.actual_shape, dtype = np.int8)
        for i in range(len(x)):
            for j in range(len(x[i])):
                if self.same_parity(i + 1, j + 1):
                    x[i][j] = 1
        return x

    # Simply put a stone, returns -1 if failure, otherwise success
    def put(self, x, y, stone_type):
        if stone_type != self.black and stone_type != self.white:
            # print('unclear stone input')
            return -1
        if self.init_valid_board[x][y] != 1:
            # print('A position that is never valid')
            return -1
        if self.current_board[x][y] != self.empty:
            # print('Do not put on other stones')
            return -1
        
        self.current_board[x][y] = stone_type
        return 0

    # Simply removing a stone
    def remove(self, x, y):
        if self.current_board[x][y] != self.black and self.current_board[x][y] != self.white:
            print('nothing to remove')
            return
        self.current_board[x][y] = self.empty

    # Simply changing turns
    def change_turn(self):
        if self.turn == self.black:
            self.turn = self.white
        else:
            self.turn = self.black
    
    # remove a list of stones
    def remove_stones(self, coords):
        for x, y in coords:
            self.remove(x, y)

    # pass
    def pass_move(self):
        if self.game_end:
            print('game has ended')
            return -1
        self.hist.append(self.get_game_state())
        if self.last_pass:
            self.game_end = True
        else:
            self.last_pass = True
        self.change_turn() 

        return 0

    def pop_hist(self):
        item = self.hist[len(self.hist) - 1]
        self.hist = self.hist[:len(self.hist) - 1]
        return item
    #UNDO

    def undo(self):
        if self.is_empty(self.hist):
            return -1
        self.load_game_state(self.pop_hist())
        return 0

    # Starting to make a real step
    def step(self, x, y):
        if self.game_end:
            print('game has ended')
            return
        # Check if this is a suicide
        if self.check_suicide(x, y):
            print("suicide not allowed")
            return -1
        
        self.hist.append(self.get_game_state())
        success_val = self.put(x, y, self.turn)
        if success_val == 0:
            # last is not pass
            self.last_pass = False
            # Stone placed, check breath of neighbors
            neighbors = self.get_neighbors(x, y)
            for xx, yy in neighbors:
                if self.current_board[xx][yy] != self.turn and self.current_board[xx][yy] != self.empty:
                    has_breath, stones, _ = self.has_breath(xx, yy)
                    if not has_breath:
                        self.remove_stones(stones)
            self.change_turn()
            if self.check_appeared(self.get_game_state()):
                print('Invalid move, state appeared before')
                self.undo()
                return -1
            else:
                return 0
        else:
            self.undo()
            return -1
        

    # Check if a coordinate is out of bound
    def out_of_bound(self, x, y):
        return x < 0 or x >= self.actual_shape[0] or y < 0 or y >= self.actual_shape[1]

    # # Get neighbors, make sure you double check this part!!!!!!
    def get_neighbors(self, x, y):
        if self.init_valid_board[x][y] != 1:
            # print('not a valid point')
            return []
        neighbors = []
        if x % 2 == 1:
            pot_neighbors = [[1, 1], [1, -1]]
        else:
            pot_neighbors = [[1, 1], [1, -1], [0, 2], [2, 0]]
        for i, j in pot_neighbors:
            for b in [1, -1]:
                xx = x + b * i
                yy = y + b * j
                if self.out_of_bound(xx, yy):
                    continue
                neighbors.append([xx, yy])
        return neighbors
    
    # # Add a list of point into the list while avoid repetition
    def add_to_list(self, item, tar_list):
        if item not in tar_list:
            tar_list.append(item)
        return tar_list
    
    # # Pop the first node from a list
    def pop_from_list(self, tar_list):
        item = tar_list[0]
        return item, tar_list[1:]

    # # Check if a list is empty
    def is_empty(self, tar_list):
        return len(tar_list) == 0
    
    # # estimate scores, not accurate
    def est(self):
        count_result = self.init_valid_board.copy()
        for i in range(self.actual_shape[0]):
            for j in range(self.actual_shape[1]):
                if self.init_valid_board[i][j] != 1:
                    continue

                if self.current_board[i][j] != 1:
                    count_result[i][j] = self.current_board[i][j]
                    continue

                if count_result[i][j] != 1:
                    continue
                explored = []
                frontier = [[i,j]]
                is_black = False
                is_white = False
                while not self.is_empty(frontier):
                    if is_black or is_white:
                        break
                    point, frontier = self.pop_from_list(frontier)
                    x, y = point
                    explored.append(point)
                    neighbors = self.get_neighbors(x, y)

                    for xx, yy in neighbors:
                        if [xx, yy] in explored:
                            continue

                        if self.current_board[xx][yy] == self.black:
                            is_black = True

                        elif self.current_board[xx][yy] == self.white:
                            is_white = True
                        
                        elif self.current_board[xx][yy] == self.empty:
                            frontier = self.add_to_list([xx, yy], frontier)
                    
                    for xx, yy in explored:
                        if is_black and is_white:
                            count_result[xx][yy] = 4
                        elif is_black:
                            count_result[xx][yy] = self.black
                        elif is_white:
                            count_result[xx][yy] = self.white
                        else:
                            count_result[xx][yy] = 5
        return count_result
    
    # # Check if a stone has breath. Returns [has breath or not: Bool, Friends: list, Breath points: list]
    def has_breath(self, x, y):
        # Take care of an empty spot
        if self.current_board[x][y] == self.empty:
            # print('empty place')
            return True, [], []
        frontier = [[x, y]]
        breath_pts = []
        target_stone = self.current_board[x][y]
        explored = []
        has_breath = False

        while not self.is_empty(frontier):
            # pop a node
            point, frontier = self.pop_from_list(frontier)
            xx, yy = point
            explored.append([xx, yy])
            neighbors = self.get_neighbors(xx, yy)
            
            for i, j in neighbors:
                if [i, j] in explored:
                    continue
                if self.current_board[i][j] == self.empty:
                    has_breath = True
                    breath_pts = self.add_to_list([i, j], breath_pts)
                elif self.current_board[i][j] == target_stone:
                    frontier = self.add_to_list([i, j], frontier)
        return has_breath, explored, breath_pts
    
    # # Check if a move is self-suiucide
    def check_suicide(self, x, y):
        if self.put(x, y, self.turn) == 0:
            # Check if some neighbors are captured
            neighbors = self.get_neighbors(x, y)
            for xx, yy in neighbors:
                if self.current_board[xx][yy] != self.turn and self.current_board[xx][yy] != self.empty:
                    has_breath, _, _ = self.has_breath(xx, yy)
                    if not has_breath:
                        self.remove(x, y)
                        return False
                    
            has_breath, _, _ = self.has_breath(x, y)
            self.remove(x, y)
            if not has_breath:
                return True
        return False
    
    # # Count stones, not accurate and need to end game first
    def count(self):
        count_result = self.init_valid_board.copy()
        for i in range(self.actual_shape[0]):
            for j in range(self.actual_shape[1]):
                if self.init_valid_board[i][j] != 1:
                    continue

                if self.current_board[i][j] != 1:
                    count_result[i][j] = self.current_board[i][j]
                    continue

                if count_result[i][j] != 1:
                    continue
                explored = []
                frontier = [[i,j]]
                is_black = False
                is_white = False
                while not self.is_empty(frontier):
                    point, frontier = self.pop_from_list(frontier)
                    x, y = point
                    explored.append(point)
                    neighbors = self.get_neighbors(x, y)

                    for xx, yy in neighbors:
                        if [xx, yy] in explored:
                            continue

                        if self.current_board[xx][yy] == self.black:
                            is_black = True

                        elif self.current_board[xx][yy] == self.white:
                            is_white = True
                        
                        elif self.current_board[xx][yy] == self.empty:
                            frontier = self.add_to_list([xx, yy], frontier)
                    
                    for xx, yy in explored:
                        if is_black and is_white:
                            # belongs to both
                            count_result[xx][yy] = 4
                        elif is_black:
                            count_result[xx][yy] = self.black
                        elif is_white:
                            count_result[xx][yy] = self.white
                        else:
                            # belongs to no one
                            count_result[xx][yy] = 5
        return count_result


    
    def get_str_turn(self):
        if self.turn == self.black:
            return "black"
        else:
            return "white"
        
    
                
                        

    