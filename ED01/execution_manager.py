import json
import os
from datetime import datetime
from pathlib import Path
import glob

def apply_color(text, code):
    return f"\033[{code}m{text}\033[0m"

class OutcomeAnalyzer:
    @staticmethod
    def enumerate_saved_outcomes():
        outcomes = sorted(glob.glob("test_results/*.json"))
        return outcomes
    
    @staticmethod
    def load_outcome(filepath):
        try:
            with open(filepath, 'r', encoding='utf-8') as file:
                return json.load(file)
        except Exception as error:
            print(f"Error loading {filepath}: {error}")
            return None
    
    @staticmethod
    def display_outcomes_table(outcomes):
        if not outcomes or 'metrics' not in outcomes and 'statistics' not in outcomes:
            return
        
        metrics = outcomes.get('metrics', outcomes.get('statistics', {}))
        config = outcomes.get('configuration', outcomes.get('config', {}))
        
        print(f"\n{'='*130}")
        print(f" Tests: {config.get('test_count', config.get('num_tests', 0))} | Grid: {config['grid_size']}x{config['grid_size']} | Difficulty: {config.get('base_difficulty', config.get('initial_difficulty', 0))}")
        print(f" Date: {outcomes['timestamp'][:19]}")
        print(f"{'='*130}\n")
        
        print(f"{'Solver':<20} {'Victories':<12} {'Defeats':<12} {'Min':<12} {'Average':<12} {'Max':<12} {'T.Min':<12} {'T.Avg':<12} {'T.Max':<12}")
        print("-" * 130)
        
        for solver_label in sorted(metrics.keys()):
            data = metrics[solver_label]
            
            min_mov_key = 'min_sequences' if 'min_sequences' in data else 'min_moves'
            avg_mov_key = 'avg_sequences' if 'avg_sequences' in data else 'avg_moves'
            max_mov_key = 'max_sequences' if 'max_sequences' in data else 'max_moves'
            
            min_mov = f"{data[min_mov_key]:.0f}" if data[min_mov_key] != '-' else '-'
            avg_mov = f"{data[avg_mov_key]:.1f}" if data[avg_mov_key] != '-' else '-'
            max_mov = f"{data[max_mov_key]:.0f}" if data[max_mov_key] != '-' else '-'
            
            min_time_key = 'min_duration' if 'min_duration' in data else 'min_time'
            avg_time_key = 'avg_duration' if 'avg_duration' in data else 'avg_time'
            max_time_key = 'max_duration' if 'max_duration' in data else 'max_time'
            
            min_time = f"{data[min_time_key]:.4f}s" if isinstance(data[min_time_key], (int, float)) else data[min_time_key]
            avg_time = f"{data[avg_time_key]:.4f}s" if isinstance(data[avg_time_key], (int, float)) else data[avg_time_key]
            max_time = f"{data[max_time_key]:.4f}s" if isinstance(data[max_time_key], (int, float)) else data[max_time_key]
            
            vic_count = data.get('victories', data.get('successes', 0))
            def_count = data.get('defeats', data.get('failures', 0))
            
            print(f"{solver_label:<20} {vic_count:<12} {def_count:<12} {min_mov:<12} {avg_mov:<12} {max_mov:<12} {min_time:<12} {avg_time:<12} {max_time:<12}")
    
    @staticmethod
    def compare_outcomes(files):
        print(f"\n{'='*130}")
        print(f" OUTCOME COMPARISON")
        print(f"{'='*130}\n")
        
        all_outcomes = []
        for filepath in files:
            outcomes = OutcomeAnalyzer.load_outcome(filepath)
            if outcomes:
                all_outcomes.append((filepath, outcomes))
        
        if not all_outcomes:
            print("No outcomes to compare.")
            return
        
        for filepath, outcomes in all_outcomes:
            print(f"\n {filepath}")
            OutcomeAnalyzer.display_outcomes_table(outcomes)

def execute_isolated_analysis():
    from batch_analyzer import BulkAnalyzer, IsolatedSolverAnalyzer
    
    solvers = ['BFS', 'DFS', 'Hill Climber', 'Annealing Optimizer', 'Path Finder', 'Heuristic Search']
    
    print("\n" + "="*80)
    print(" ISOLATED ANALYSIS - SELECT A SOLVER")
    print("="*80 + "\n")
    
    for idx, solver in enumerate(solvers, 1):
        print(f"{idx}. {solver}")
    
    print(f"\n0. Back")
    
    try:
        selection = int(input("\nChoose a solver: ").strip())
        
        if selection == 0:
            return
        elif 0 < selection <= len(solvers):
            solver = solvers[selection - 1]
            
            print(f"\n" + "="*80)
            print(f" CONFIGURATION - {solver}")
            print("="*80)
            
            try:
                test_count = int(input("Test quantity (10): ").strip() or "10")
                grid_size = int(input("Grid size (5): ").strip() or "5")
                base_difficulty = int(input("Base difficulty (1): ").strip() or "1")
                
                if test_count <= 0:
                    test_count = 10
                if grid_size <= 0:
                    grid_size = 5
                if base_difficulty <= 0:
                    base_difficulty = 1
                
                print(f"\nStarting isolated analysis for {solver}...")
                
                analyzer = IsolatedSolverAnalyzer(
                    solver_label=solver,
                    test_count=test_count,
                    grid_size=grid_size,
                    base_difficulty=base_difficulty
                )
                analyzer.run_complete_analysis(persist=True)
            
            except ValueError:
                print(apply_color("Invalid input.", "31"))
        else:
            print(apply_color("Invalid option.", "31"))
    
    except ValueError:
        print(apply_color("Invalid input.", "31"))

def execute_quick_analysis():
    from batch_analyzer import BulkAnalyzer
    
    print("\n" + "="*80)
    print(" QUICK ANALYSIS - DIFFICULTY PRESETS")
    print("="*80 + "\n")
    
    print("1. Easy (3x3, 5 tests)")
    print("2. Medium (5x5, 10 tests)")
    print("3. Hard (7x7, 15 tests)")
    print("4. Very Hard (10x10, 20 tests)")
    print("5. Custom")
    print("0. Back")
    
    try:
        selection = int(input("\nChoose preset: ").strip())
        
        presets = {
            1: (3, 5, 1),
            2: (5, 10, 1),
            3: (7, 15, 1),
            4: (10, 20, 1)
        }
        
        if selection == 0:
            return
        elif selection in presets:
            grid_size, test_count, base_difficulty = presets[selection]
        elif selection == 5:
            grid_size = int(input("Grid size: ").strip())
            test_count = int(input("Test count: ").strip())
            base_difficulty = int(input("Base difficulty: ").strip())
        else:
            print(apply_color("Invalid option.", "31"))
            return
        
        print(f"\nStarting analysis with {grid_size}x{grid_size} grid, {test_count} tests...")
        
        analyzer = BulkAnalyzer(
            test_count=test_count,
            grid_size=grid_size,
            base_difficulty=base_difficulty
        )
        analyzer.run_complete_analysis(persist=True)
    
    except ValueError:
        print(apply_color("Invalid input.", "31"))

def view_saved_outcomes():
    outcomes = OutcomeAnalyzer.enumerate_saved_outcomes()
    
    if not outcomes:
        print(apply_color("\nNo saved outcomes found!", "31"))
        return
    
    print("\n" + "="*80)
    print(" SAVED OUTCOMES")
    print("="*80 + "\n")
    
    for idx, filepath in enumerate(outcomes, 1):
        print(f"{idx}. {os.path.basename(filepath)}")
    
    print("\n0. Back")
    
    try:
        selection = int(input("\nView outcome: ").strip())
        
        if selection == 0:
            return
        elif 0 < selection <= len(outcomes):
            outcome = OutcomeAnalyzer.load_outcome(outcomes[selection - 1])
            if outcome:
                OutcomeAnalyzer.display_outcomes_table(outcome)
                input("\nPress Enter to continue...")
        else:
            print(apply_color("Invalid option.", "31"))
    
    except ValueError:
        print(apply_color("Invalid input.", "31"))

def main():
    import os
    
    while True:
        os.system('cls' if os.name == 'nt' else 'clear')
        
        print("\n" + "="*80)
        print(apply_color(" EXECUTION MANAGER - AI SOLVER ANALYSIS", "34"))
        print("="*80 + "\n")
        
        print("1. Quick Analysis (Presets)")
        print("2. Isolated Solver Analysis")
        print("3. View Saved Outcomes")
        print("4. Compare Outcomes")
        print("0. Exit")
        
        try:
            selection = int(input("\nChoose option: ").strip())
            
            if selection == 0:
                print(apply_color("\nExiting. Goodbye!", "32"))
                break
            elif selection == 1:
                execute_quick_analysis()
                input("\nPress Enter to continue...")
            elif selection == 2:
                execute_isolated_analysis()
                input("\nPress Enter to continue...")
            elif selection == 3:
                view_saved_outcomes()
            elif selection == 4:
                outcomes = OutcomeAnalyzer.enumerate_saved_outcomes()
                if outcomes:
                    OutcomeAnalyzer.compare_outcomes(outcomes)
                    input("\nPress Enter to continue...")
                else:
                    print(apply_color("\nNo outcomes to compare!", "31"))
                    input("\nPress Enter to continue...")
            else:
                print(apply_color("Invalid option.", "31"))
                input("\nPress Enter to continue...")
        
        except ValueError:
            print(apply_color("Invalid input.", "31"))
            input("\nPress Enter to continue...")
        except KeyboardInterrupt:
            print(apply_color("\n\nInterrupted by user.", "31"))
            break

if __name__ == "__main__":
    main()
