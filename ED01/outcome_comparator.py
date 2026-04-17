import json
import glob
from pathlib import Path
from datetime import datetime

def apply_color(text, code):
    return f"\033[{code}m{text}\033[0m"

OUTPUT_DIR = Path(__file__).parent / "test_results"

class OutcomeComparator:
    @staticmethod
    def retrieve_all_outcomes():
        if not OUTPUT_DIR.exists():
            return []
        
        files = sorted(OUTPUT_DIR.glob("*.json"))
        outcomes = []
        
        for filepath in files:
            try:
                with open(filepath, 'r', encoding='utf-8') as file:
                    content = json.load(file)
                    outcomes.append({
                        'filename': filepath.name,
                        'content': content,
                        'timestamp': datetime.fromisoformat(content['timestamp'])
                    })
            except Exception as error:
                print(f"Error loading {filepath.name}: {error}")
        
        return outcomes
    
    @staticmethod
    def display_single_outcome(outcome):
        content = outcome['content']
        config = content.get('configuration', content.get('config', {}))
        metrics = content.get('metrics', content.get('statistics', {}))
        
        print(f"\n{'='*140}")
        print(f" {outcome['filename']}")
        print(f"{'='*140}")
        print(f"Date: {content['timestamp'][:19]}")
        print(f"Config: {config.get('test_count', config.get('num_tests', 0))} tests | {config['grid_size']}x{config['grid_size']} | Base difficulty: {config.get('base_difficulty', config.get('initial_difficulty', 0))}")
        print(f"{'='*140}\n")
        
        print(f"{'Solver':<20} {'Vic/Def':<12} {'Min Mov':<12} {'Avg Mov':<12} {'Max Mov':<12} {'Min Time':<15} {'Avg Time':<15} {'Max Time':<15}")
        print("-" * 140)
        
        for solver_label in sorted(metrics.keys()):
            data = metrics[solver_label]
            
            vic_def = f"{data.get('victories', data.get('successes', 0))}/{data.get('defeats', data.get('failures', 0))}"
            
            min_mov_key = 'min_sequences' if 'min_sequences' in data else 'min_moves'
            avg_mov_key = 'avg_sequences' if 'avg_sequences' in data else 'avg_moves'
            max_mov_key = 'max_sequences' if 'max_sequences' in data else 'max_moves'
            
            min_mov = f"{data[min_mov_key]:.0f}" if data[min_mov_key] != '-' else '-'
            avg_mov = f"{data[avg_mov_key]:.1f}" if data[avg_mov_key] != '-' else '-'
            max_mov = f"{data[max_mov_key]:.0f}" if data[max_mov_key] != '-' else '-'
            
            min_time_key = 'min_duration' if 'min_duration' in data else 'min_time'
            avg_time_key = 'avg_duration' if 'avg_duration' in data else 'avg_time'
            max_time_key = 'max_duration' if 'max_duration' in data else 'max_time'
            
            min_time = f"{data[min_time_key]:.5f}s" if isinstance(data[min_time_key], (int, float)) else data[min_time_key]
            avg_time = f"{data[avg_time_key]:.5f}s" if isinstance(data[avg_time_key], (int, float)) else data[avg_time_key]
            max_time = f"{data[max_time_key]:.5f}s" if isinstance(data[max_time_key], (int, float)) else data[max_time_key]
            
            print(f"{solver_label:<20} {vic_def:<12} {min_mov:<12} {avg_mov:<12} {max_mov:<12} {min_time:<15} {avg_time:<15} {max_time:<15}")
    
    @staticmethod
    def compare_multiple_outcomes(outcomes):
        if not outcomes:
            print(apply_color("No outcomes to compare.", "31"))
            return
        
        print(f"\n{'='*140}")
        print(apply_color(" COMPARISON OF TEST SESSIONS", "34"))
        print(f"{'='*140}\n")
        
        print(f"{'Session':<5} {'Config':<25} {'BFS':<15} {'PathFind':<15} {'HeuSearch':<15} {'HillClimb':<15} {'Annealing':<15} {'DFS':<15}")
        print("-" * 140)
        
        for idx, outcome in enumerate(outcomes, 1):
            content = outcome['content']
            config = content.get('configuration', content.get('config', {}))
            metrics = content.get('metrics', content.get('statistics', {}))
            
            config_str = f"{config['grid_size']}x{config['grid_size']}-{config.get('test_count', config.get('num_tests', 0))}t"
            
            test_total = config.get('test_count', config.get('num_tests', 0))
            
            def get_success_rate(label):
                if label in metrics:
                    vic = metrics[label].get('victories', metrics[label].get('successes', 0))
                    return f"({vic}/{test_total})"
                return "(-/-)"
            
            bfs_rate = get_success_rate('BFS')
            path_rate = get_success_rate('Path Finder') if 'Path Finder' in metrics else get_success_rate('A*')
            heur_rate = get_success_rate('Heuristic Search') if 'Heuristic Search' in metrics else get_success_rate('Greedy Search')
            hill_rate = get_success_rate('Hill Climber') if 'Hill Climber' in metrics else get_success_rate('Hill Climbing')
            anneal_rate = get_success_rate('Annealing Optimizer') if 'Annealing Optimizer' in metrics else get_success_rate('Simulated Annealing')
            dfs_rate = get_success_rate('DFS')
            
            print(f"{idx:<5} {config_str:<25} {bfs_rate:<15} {path_rate:<15} {heur_rate:<15} {hill_rate:<15} {anneal_rate:<15} {dfs_rate:<15}")
        
        print(f"\n{apply_color('Success rate (Victories/Total)', '32')}\n")

def main():
    import os
    os.system('cls' if os.name == 'nt' else 'clear')
    
    while True:
        outcomes = OutcomeComparator.retrieve_all_outcomes()
        
        print("\n" + "="*80)
        print(apply_color(" OUTCOME COMPARATOR", "34"))
        print("="*80)
        
        if not outcomes:
            print(apply_color("\nNo saved outcomes found!", "31"))
            print("Execute 'python batch_analyzer.py' or 'python execution_manager.py' to generate outcomes.")
            break
        
        print(f"\nOutcomes available: {len(outcomes)}\n")
        
        for idx, outcome in enumerate(outcomes, 1):
            config = outcome['content'].get('configuration', outcome['content'].get('config', {}))
            print(f"{idx}. {outcome['filename']} ({config['grid_size']}x{config['grid_size']}, {config.get('test_count', config.get('num_tests', 0))} tests)")
        
        print(f"\n0. Compare all")
        print(f"-1. Exit")
        
        try:
            selection = int(input("\nChoose an option: ").strip())
            
            if selection == 0:
                OutcomeComparator.compare_multiple_outcomes(outcomes)
                input("\nPress Enter to continue...")
            elif 0 < selection <= len(outcomes):
                OutcomeComparator.display_single_outcome(outcomes[selection - 1])
                input("\nPress Enter to continue...")
            elif selection == -1:
                print(apply_color("\nGoodbye!", "32"))
                break
            else:
                print(apply_color("Invalid option.", "31"))
        
        except ValueError:
            print(apply_color("Invalid input.", "31"))
        
        os.system('cls' if os.name == 'nt' else 'clear')

if __name__ == "__main__":
    main()
