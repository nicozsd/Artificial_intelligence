import time
import random
import math

class HillClimber:
    def execute(self, starting_state):
        begin_time = time.time()
        active_state = starting_state
        sequence = []
        nodes_examined = 0
        
        while True:
            nodes_examined += 1
            
            if active_state.check_victory():
                finish_time = time.time() - begin_time
                return sequence, nodes_examined, finish_time
            
            neighbors = active_state.generate_neighbors()
            optimal_state = None
            optimal_move = None
            optimal_score = active_state.compute_active_count()
            
            for next_state, move in neighbors:
                evaluation = next_state.compute_active_count()
                if evaluation < optimal_score:
                    optimal_state = next_state
                    optimal_move = move
                    optimal_score = evaluation
            
            if optimal_state is None:
                finish_time = time.time() - begin_time
                return None, nodes_examined, finish_time
            
            active_state = optimal_state
            sequence.append(optimal_move)


class AnnealingOptimizer:
    def __init__(self, start_temp=100, decay_factor=0.98, steps_per_temp=100, max_steps=50000):
        self.start_temp = start_temp
        self.decay_factor = decay_factor
        self.steps_per_temp = steps_per_temp
        self.max_steps = max_steps
    
    def execute(self, starting_state):
        begin_time = time.time()
        active_state = starting_state
        optimal_state = starting_state
        optimal_sequence = []
        active_sequence = []
        nodes_examined = 0
        temperature = self.start_temp
        iteration_count = 0
        
        while temperature > 0.01 and iteration_count < self.max_steps:
            for _ in range(self.steps_per_temp):
                iteration_count += 1
                nodes_examined += 1
                
                if active_state.check_victory():
                    finish_time = time.time() - begin_time
                    return active_sequence, nodes_examined, finish_time
                
                if optimal_state.check_victory():
                    finish_time = time.time() - begin_time
                    return optimal_sequence, nodes_examined, finish_time
                
                neighbors = active_state.generate_neighbors()
                next_state, move = random.choice(neighbors)
                
                active_quality = active_state.compute_active_count()
                next_quality = next_state.compute_active_count()
                quality_delta = next_quality - active_quality
                
                if quality_delta < 0 or random.random() < math.exp(-quality_delta / max(temperature, 0.01)):
                    active_state = next_state
                    active_sequence.append(move)
                    
                    if active_state.compute_active_count() < optimal_state.compute_active_count():
                        optimal_state = active_state
                        optimal_sequence = active_sequence.copy()
                
                if iteration_count >= self.max_steps:
                    break
            
            temperature *= self.decay_factor
        
        if optimal_state.check_victory():
            finish_time = time.time() - begin_time
            return optimal_sequence, nodes_examined, finish_time
        
        finish_time = time.time() - begin_time
        return None, nodes_examined, finish_time
