from Core.board_generator import BoardGenerator
from Core.game_state import GameState
from Solver.breadth_explorer import BreadthExplorer
from Solver.depth_explorer import DepthExplorer
from Solver.local_optimizer import HillClimber, AnnealingOptimizer
from Solver.pathfinder import PathFinder
from Solver.heuristic_search import HeuristicSearch

def apply_color(text, code):
    return f"\033[{code}m{text}\033[0m"

class Menu:
    def __init__(self, grid_size=3, shuffle_count=1):
        self.grid_size = grid_size
        self.shuffle_count = shuffle_count
        self.generator = BoardGenerator(grid_size, shuffle_count)
        self.starting_state = GameState(self.generator.grid, grid_size)

    def show_header(self):
        print("\n" + "="*80)
        print(apply_color(" Welcome to AI Algorithm Tester for Light Out ", "34"))
        print("="*80)
        print(f"Goal: Turn off all lights {apply_color('(make matrix all zeros)', '33')}")
        print("="*80 + "\n")

    def show_initial_board(self):
        print("Initial board state:")
        print(self.starting_state)
        print(f"Lights on: {apply_color(self.starting_state.compute_active_count(), '31')}")
    
    def regenerate_puzzle(self, grid_size=None):
        import os
        os.system('cls' if os.name == 'nt' else 'clear')
        if grid_size is not None:
            self.grid_size = grid_size
        self.generator.rebuild(self.shuffle_count, self.grid_size)
        self.starting_state = GameState(self.generator.grid, self.grid_size)
        print("\n" + apply_color("New board generated!", "32"))
        self.show_initial_board()

    def display_outcome(self, sequence, examined, duration):
        if sequence is None:
            print(apply_color("No solution found!", "31"))
            print(f"States explored: {apply_color(examined, '33')}")
            print(f"Time spent: {apply_color(f'{duration:.4f}s', '33')}\n")
            return
        
        print(apply_color("SOLUTION FOUND!", "32"))
        print(f"Number of moves: {apply_color(len(sequence), '33')}")
        print(f"States explored: {apply_color(examined, '33')}")
        print(f"Time spent: {apply_color(f'{duration:.4f}s', '33')}")
        print(f"\nMoves (clicked positions):")
        for idx, (row, col) in enumerate(sequence, 1):
            print(f"  {idx}. Click at ({row}, {col})")
        print()

    def execute_solver(self, solver_label, solver):
        print(f"\nExecuting {solver_label}...")
        print("-" * 50)
        sequence, examined, duration = solver.execute(self.starting_state)
        self.display_outcome(sequence, examined, duration)

    def launch(self):
        import os
        self.show_header()
        self.show_initial_board()
        active = True
        while active:
            print("\n" + "="*50)
            print(apply_color("AVAILABLE SOLVERS:", "32"))
            print("="*50)
            print(f"""   
{apply_color("1. Breadth First Search", "34")}
   - Finds OPTIMAL solution (fewest moves)
   - Uses more memory
   - Slower

{apply_color("2. Depth First Search", "34")}
   - Uses less memory
   - Faster but solution may not be optimal
   - Depth limit: 50

{apply_color("3. Hill Climber (Local Search)", "34")}
   - Very fast
   - May get stuck in local optima
   - Does not guarantee solution

{apply_color("4. Annealing Optimizer (Simulated Annealing)", "34")}
   - Escapes local optima
   - Probabilistically finds solution
   - Slower than Hill Climber

{apply_color("5. Path Finder (A-Star)", "34")}
   - Informed search: uses heuristic + cost
   - Finds OPTIMAL solution
   - More efficient than BFS

{apply_color("6. Heuristic Search (Greedy)", "34")}
   - Informed search: uses only heuristic
   - Fast but does not guarantee optimum
   - Fewer explorations than A*

{apply_color("7. Regenerate Board (New Game)", "34")}
   - Generates a new random board
   - Maintains size and number of moves

{apply_color("0. Exit", "34")}
            """)
            print("="*50)
            
            try:
                selection = input("Choose a solver (0-7): ").strip()
                if selection == "7":
                    size_input = input("New board size (press Enter to keep "+str(self.grid_size)+"): ").strip()
                    if size_input:
                        try:
                            updated_size = int(size_input)
                            self.regenerate_puzzle(grid_size=updated_size)
                        except ValueError:
                            print(apply_color("Invalid size. Keeping current.", "31"))
                            self.regenerate_puzzle()
                    else:
                        self.regenerate_puzzle()
                    continue
                os.system('cls' if os.name == 'nt' else 'clear')
                match selection:
                    case "1":
                        explorer = BreadthExplorer()
                        self.execute_solver("BFS (Breadth-First Search)", explorer)
                    case "2":
                        explorer = DepthExplorer(max_level=20, limit_seconds=10)
                        self.execute_solver("DFS (Depth-First Search)", explorer)
                    case "3":
                        climber = HillClimber()
                        self.execute_solver("Hill Climbing", climber)
                    case "4":
                        optimizer = AnnealingOptimizer()
                        self.execute_solver("Simulated Annealing", optimizer)
                    case "5":
                        finder = PathFinder(strategy='lights')
                        self.execute_solver("A* (A-Star)", finder)
                    case "6":
                        searcher = HeuristicSearch(strategy='lights')
                        self.execute_solver("Greedy Search", searcher)
                    case "0":
                        print(apply_color("\nExiting program. Goodbye!", "32"))
                        active = False
                    case _:
                        print(apply_color("Invalid choice. Try again.", "31"))
            except KeyboardInterrupt:
                print(apply_color("\n\nProgram interrupted by user.", "31"))
                active = False
            except Exception as error:
                print(apply_color(f"\nError occurred: {str(error)}", "31"))

if __name__ == "__main__":
    interface = Menu(board_size=3, initial_moves=1)
    interface.launch()
