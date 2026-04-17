from copy import deepcopy

class GameState:
    def __init__(self, grid, dimension):
        self.grid = deepcopy(grid)
        self.dimension = dimension
    
    def __eq__(self, other):
        if not isinstance(other, GameState):
            return False
        return self.grid == other.grid
    
    def __hash__(self):
        return hash(tuple(tuple(line) for line in self.grid))
    
    def __str__(self):
        output = ""
        for line in self.grid:
            output += ' '.join(str(value) for value in line) + '\n'
        return output
    
    def check_victory(self):
        for line in self.grid:
            for value in line:
                if value != 0:
                    return False
        return True
    
    def generate_neighbors(self):
        neighbors = []
        for row in range(self.dimension):
            for col in range(self.dimension):
                updated_grid = deepcopy(self.grid)
                updated_grid[row][col] = 1 - updated_grid[row][col]
                for delta_row, delta_col in [(-1, 0), (1, 0), (0, -1), (0, 1)]:
                    adj_row, adj_col = row + delta_row, col + delta_col
                    if 0 <= adj_row < self.dimension and 0 <= adj_col < self.dimension:
                        updated_grid[adj_row][adj_col] = 1 - updated_grid[adj_row][adj_col]
                updated_state = GameState(updated_grid, self.dimension)
                neighbors.append((updated_state, (row, col)))
        return neighbors
    
    def compute_active_count(self):
        total = 0
        for line in self.grid:
            for value in line:
                total += value
        return total
    
    def compute_manhattan_metric(self):
        aggregate = 0
        for row_idx in range(self.dimension):
            for col_idx in range(self.dimension):
                if self.grid[row_idx][col_idx] == 1:
                    nearest_dist = min(row_idx, col_idx, self.dimension - 1 - row_idx, self.dimension - 1 - col_idx)
                    aggregate += nearest_dist
        return aggregate
