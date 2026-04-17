from random import randint

class BoardGenerator:
    def __init__(self, dimension, scramble_moves):
        self.dimension = dimension
        self.grid = self.construct_grid(scramble_moves)

    def construct_grid(self, moves_count):
        grid = [[0 for _ in range(self.dimension)] for _ in range(self.dimension)]
        for _ in range(moves_count):
            row, col = randint(0, self.dimension - 1), randint(0, self.dimension - 1)
            grid = self.switch_cells(row, col, grid)
        return grid

    def switch_cells(self, row, col, grid):
        if 0 <= row < self.dimension and 0 <= col < self.dimension:
            grid[row][col] = 1 - grid[row][col]
        else:
            print("Invalid position. Please choose a position within the board.")
            return False
        for delta_row, delta_col in [(-1, 0), (1, 0), (0, -1), (0, 1)]:
            adj_row, adj_col = row + delta_row, col + delta_col
            if 0 <= adj_row < self.dimension and 0 <= adj_col < self.dimension:
                grid[adj_row][adj_col] = 1 - grid[adj_row][adj_col]
        return grid

    def validate_solution(self):
        for line in self.grid:
            for value in line:
                if value != 0:
                    return False
        return True
        
    def display_grid(self):
        for line in self.grid:
            print(' '.join(str(value) for value in line))
        print()
    
    def rebuild(self, scramble_moves=None, dimension=None):
        if dimension is not None:
            self.dimension = dimension
        if scramble_moves is None:
            scramble_moves = 2
        self.grid = self.construct_grid(scramble_moves)
        return self.grid
