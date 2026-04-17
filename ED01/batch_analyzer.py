import json
import os
import signal
from datetime import datetime
from pathlib import Path
from Core.board_generator import BoardGenerator
from Core.game_state import GameState
from Solver.breadth_explorer import BreadthExplorer
from Solver.depth_explorer import DepthExplorer
from Solver.local_optimizer import HillClimber, AnnealingOptimizer
from Solver.pathfinder import PathFinder
from Solver.heuristic_search import HeuristicSearch

OUTPUT_DIR = Path(__file__).parent / "test_results"
OUTPUT_DIR.mkdir(exist_ok=True)

class BulkAnalyzer:
    def __init__(self, test_count=20, grid_size=5, base_difficulty=1):
        self.test_count = test_count
        self.grid_size = grid_size
        self.base_difficulty = base_difficulty
        self.test_grids = []
        self.outcomes = {}
        self.halted = False
        self.active_solver = None
        self.active_grid_id = None
        self.session_start = None
        self.solver_limit = 30
        signal.signal(signal.SIGINT, self._halt_handler)
    
    def _halt_handler(self, signum, frame):
        self.halted = True
        print(f"\n\n{'='*80}")
        print(" Test halted by user - Saving data...")
        print("="*80)
        raise KeyboardInterrupt("User interruption")
    
    def construct_test_grids(self):
        print(f"\n{'='*80}")
        print(f" Constructing {self.test_count} grids with increasing difficulty")
        print(f"{'='*80}\n")
        
        self.test_grids = []
        for idx in range(1, self.test_count + 1):
            complexity = self.base_difficulty + (idx - 1)
            generator = BoardGenerator(self.grid_size, complexity)
            start_state = GameState(generator.grid, self.grid_size)
            
            self.test_grids.append({
                'id': idx,
                'grid': [row[:] for row in generator.grid],
                'state': start_state,
                'complexity': complexity,
                'active_lights': start_state.compute_active_count()
            })
            
            print(f"  Grid {idx:2d}: Complexity {complexity} | Active lights: {start_state.compute_active_count()}")
    
    def execute_analysis(self):
        print(f"\n{'='*80}")
        print(f" Executing analysis")
        print(f"{'='*80}\n")
        
        solvers = {
            'BFS': BreadthExplorer(),
            'DFS': DepthExplorer(max_level=50, limit_seconds=10),
            'Hill Climber': HillClimber(),
            'Annealing Optimizer': AnnealingOptimizer(start_temp=100, decay_factor=0.98, steps_per_temp=100),
            'Path Finder': PathFinder(strategy='lights'),
            'Heuristic Search': HeuristicSearch(strategy='lights')
        }
        
        for solver_label in solvers.keys():
            self.outcomes[solver_label] = {
                'durations': [],
                'sequences': [],
                'examined': [],
                'victories': 0,
                'defeats': 0
            }
        
        total_runs = len(self.test_grids) * len(solvers)
        current_run = 0
        
        for grid_info in self.test_grids:
            if self.halted:
                break
            
            print(f"\nGrid {grid_info['id']} (Complexity: {grid_info['complexity']}, Active: {grid_info['active_lights']})")
            print("-" * 80)
            
            for solver_label, solver in solvers.items():
                if self.halted:
                    break
                
                current_run += 1
                self.active_solver = solver_label
                self.active_grid_id = grid_info['id']
                print(f"  [{current_run:3d}/{total_runs}] {solver_label:20s} ", end="", flush=True)
                
                try:
                    eval_state = GameState(grid_info['grid'], self.grid_size)
                    sequence, examined, duration = solver.execute(eval_state)
                    
                    if sequence is not None:
                        move_count = len(sequence)
                        self.outcomes[solver_label]['victories'] += 1
                        self.outcomes[solver_label]['sequences'].append(move_count)
                        print(f"Success | Moves: {move_count:3d} | Examined: {examined:6d} | Duration: {duration:.4f}s")
                    else:
                        self.outcomes[solver_label]['defeats'] += 1
                        print(f"Failed  | Examined: {examined:6d} | Duration: {duration:.4f}s")
                    
                    self.outcomes[solver_label]['durations'].append(duration)
                    self.outcomes[solver_label]['examined'].append(examined)
                    
                except Exception as error:
                    self.outcomes[solver_label]['defeats'] += 1
                    print(f"Error: {str(error)[:40]}")
    
    def compute_metrics(self):
        metrics = {}
        
        for solver_label, records in self.outcomes.items():
            metrics[solver_label] = {}
            
            if records['sequences']:
                metrics[solver_label]['min_sequences'] = min(records['sequences'])
                metrics[solver_label]['avg_sequences'] = sum(records['sequences']) / len(records['sequences'])
                metrics[solver_label]['max_sequences'] = max(records['sequences'])
            else:
                metrics[solver_label]['min_sequences'] = '-'
                metrics[solver_label]['avg_sequences'] = '-'
                metrics[solver_label]['max_sequences'] = '-'
            
            metrics[solver_label]['min_duration'] = min(records['durations']) if records['durations'] else '-'
            metrics[solver_label]['avg_duration'] = sum(records['durations']) / len(records['durations']) if records['durations'] else '-'
            metrics[solver_label]['max_duration'] = max(records['durations']) if records['durations'] else '-'
            
            metrics[solver_label]['victories'] = records['victories']
            metrics[solver_label]['defeats'] = records['defeats']
        
        return metrics
    
    def generate_report(self):
        metrics = self.compute_metrics()
        
        print(f"\n{'='*120}")
        print(f" BULK ANALYSIS REPORT")
        if self.halted:
            print(f" Test halted (Partial data)")
        print(f"{'='*120}")
        print(f"Date: {datetime.now().strftime('%d/%m/%Y %H:%M:%S')}")
        print(f"Grids tested: {self.test_count}")
        print(f"Grid size: {self.grid_size}x{self.grid_size}")
        print(f"Base complexity: {self.base_difficulty}")
        if self.halted:
            print(f"Last run: Grid {self.active_grid_id} - {self.active_solver}")
        print(f"{'='*120}\n")
        
        print(f"{'Solver':<20} {'Victories':<12} {'Defeats':<12} {'Min.Mov':<12} {'Avg.Mov':<12} {'Max.Mov':<12}")
        print("-" * 120)
        
        for solver_label in sorted(metrics.keys()):
            data = metrics[solver_label]
            min_val = f"{data['min_sequences']:.0f}" if data['min_sequences'] != '-' else '-'
            avg_val = f"{data['avg_sequences']:.1f}" if data['avg_sequences'] != '-' else '-'
            max_val = f"{data['max_sequences']:.0f}" if data['max_sequences'] != '-' else '-'
            
            print(f"{solver_label:<20} {data['victories']:<12} {data['defeats']:<12} {min_val:<12} {avg_val:<12} {max_val:<12}")
        
        print("\n" + "-" * 120)
        print(f"{'Solver':<20} {'Min.Time':<15} {'Avg.Time':<15} {'Max.Time':<15}")
        print("-" * 120)
        
        for solver_label in sorted(metrics.keys()):
            data = metrics[solver_label]
            min_time = f"{data['min_duration']:.6f}s" if data['min_duration'] != '-' else '-'
            avg_time = f"{data['avg_duration']:.6f}s" if data['avg_duration'] != '-' else '-'
            max_time = f"{data['max_duration']:.6f}s" if data['max_duration'] != '-' else '-'
            
            print(f"{solver_label:<20} {min_time:<15} {avg_time:<15} {max_time:<15}")
        
        print("\n" + "="*120)
    
    def persist_outcomes(self, filename=None):
        if filename is None:
            timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
            status = "_interrupted" if self.halted else ""
            filename = f"analysis_{self.grid_size}x{self.grid_size}_{timestamp}{status}.json"
        
        filepath = OUTPUT_DIR / filename
        metrics = self.compute_metrics()
        
        report = {
            'timestamp': datetime.now().isoformat(),
            'configuration': {
                'test_count': self.test_count,
                'grid_size': self.grid_size,
                'base_difficulty': self.base_difficulty
            },
            'status': {
                'completed': not self.halted,
                'interrupted': self.halted,
                'last_solver': self.active_solver,
                'last_grid_id': self.active_grid_id
            },
            'metrics': metrics,
            'raw_outcomes': self.outcomes
        }
        
        with open(filepath, 'w', encoding='utf-8') as file:
            json.dump(report, file, indent=2, ensure_ascii=False)
        
        print(f"\nOutcomes saved in: test_results/{filename}")
        if self.halted:
            print(f"  Last run: Grid {self.active_grid_id} - {self.active_solver}")
        return str(filepath)
    
    def run_complete_analysis(self, persist=True):
        try:
            self.construct_test_grids()
            self.execute_analysis()
            self.generate_report()
            
            if persist:
                self.persist_outcomes()
            
            return True
        except KeyboardInterrupt:
            print("\nSaving accumulated data...")
            self.halted = True
            if persist:
                self.persist_outcomes()
            print("\nData saved successfully!")
            return False
        except Exception as error:
            print(f"\nError during analysis: {str(error)}")
            import traceback
            traceback.print_exc()
            if persist:
                self.persist_outcomes()
            return False
        finally:
            signal.signal(signal.SIGINT, signal.default_int_handler)

class IsolatedSolverAnalyzer:
    def __init__(self, solver_label, test_count=10, grid_size=5, base_difficulty=1):
        self.solver_label = solver_label
        self.test_count = test_count
        self.grid_size = grid_size
        self.base_difficulty = base_difficulty
        self.test_grids = []
        self.outcomes = []
        self.halted = False
        self.active_grid_id = None
        signal.signal(signal.SIGINT, self._halt_handler)
    
    def _halt_handler(self, signum, frame):
        self.halted = True
        print(f"\n\n{'='*80}")
        print(" Isolated test halted by user - Saving data...")
        print("="*80)
        raise KeyboardInterrupt("User interruption")
    
    def construct_test_grids(self):
        print(f"\n{'='*80}")
        print(f" Constructing {self.test_count} grids for {self.solver_label}")
        print(f"{'='*80}\n")
        
        self.test_grids = []
        for idx in range(1, self.test_count + 1):
            complexity = self.base_difficulty + (idx - 1)
            generator = BoardGenerator(self.grid_size, complexity)
            start_state = GameState(generator.grid, self.grid_size)
            
            self.test_grids.append({
                'id': idx,
                'grid': [row[:] for row in generator.grid],
                'state': start_state,
                'complexity': complexity,
                'active_lights': start_state.compute_active_count()
            })
            
            print(f"  Grid {idx:2d}: Complexity {complexity} | Active lights: {start_state.compute_active_count()}")
    
    def execute_isolated_analysis(self):
        print(f"\n{'='*80}")
        print(f" Executing isolated analysis for {self.solver_label}")
        print(f"{'='*80}\n")
        
        solver_map = {
            'BFS': BreadthExplorer(),
            'DFS': DepthExplorer(max_level=50, limit_seconds=10),
            'Hill Climber': HillClimber(),
            'Annealing Optimizer': AnnealingOptimizer(),
            'Path Finder': PathFinder(strategy='lights'),
            'Heuristic Search': HeuristicSearch(strategy='lights')
        }
        
        solver = solver_map.get(self.solver_label)
        if not solver:
            print(f"Solver {self.solver_label} not found!")
            return
        
        for grid_info in self.test_grids:
            if self.halted:
                break
            
            self.active_grid_id = grid_info['id']
            print(f"Grid {grid_info['id']}: ", end="", flush=True)
            
            try:
                eval_state = GameState(grid_info['grid'], self.grid_size)
                sequence, examined, duration = solver.execute(eval_state)
                
                outcome = {
                    'grid_id': grid_info['id'],
                    'complexity': grid_info['complexity'],
                    'success': sequence is not None,
                    'moves': len(sequence) if sequence else None,
                    'examined': examined,
                    'duration': duration
                }
                self.outcomes.append(outcome)
                
                if sequence:
                    print(f"Success | Moves: {len(sequence)} | Examined: {examined} | Duration: {duration:.4f}s")
                else:
                    print(f"Failed | Examined: {examined} | Duration: {duration:.4f}s")
                    
            except Exception as error:
                print(f"Error: {str(error)}")
                self.outcomes.append({
                    'grid_id': grid_info['id'],
                    'complexity': grid_info['complexity'],
                    'success': False,
                    'error': str(error)
                })
    
    def persist_outcomes(self):
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        status = "_interrupted" if self.halted else ""
        filename = f"isolated_{self.solver_label.replace(' ', '_')}_{self.grid_size}x{self.grid_size}_{timestamp}{status}.json"
        filepath = OUTPUT_DIR / filename
        
        report = {
            'timestamp': datetime.now().isoformat(),
            'solver': self.solver_label,
            'configuration': {
                'test_count': self.test_count,
                'grid_size': self.grid_size,
                'base_difficulty': self.base_difficulty
            },
            'status': {
                'completed': not self.halted,
                'interrupted': self.halted
            },
            'outcomes': self.outcomes
        }
        
        with open(filepath, 'w', encoding='utf-8') as file:
            json.dump(report, file, indent=2, ensure_ascii=False)
        
        print(f"\nOutcomes saved in: test_results/{filename}")
        return str(filepath)
    
    def run_complete_analysis(self, persist=True):
        try:
            self.construct_test_grids()
            self.execute_isolated_analysis()
            
            if persist:
                self.persist_outcomes()
            
            return True
        except KeyboardInterrupt:
            print("\nSaving data...")
            self.halted = True
            if persist:
                self.persist_outcomes()
            print("\nData saved!")
            return False
        finally:
            signal.signal(signal.SIGINT, signal.default_int_handler)

if __name__ == "__main__":
    analyzer = BulkAnalyzer(num_tests=10, board_size=5, initial_difficulty=1)
    analyzer.run_complete_analysis()
