import heapq
import time

class HeuristicSearch:
    def __init__(self, strategy='lights'):
        self.strategy = strategy
    
    def compute_heuristic(self, state):
        if self.strategy == 'manhattan':
            return state.compute_manhattan_metric()
        else:
            return state.compute_active_count()
    
    def execute(self, starting_state):
        begin_time = time.time()
        priority_queue = []
        sequence_counter = 0
        
        initial_score = self.compute_heuristic(starting_state)
        heapq.heappush(priority_queue, (initial_score, sequence_counter, starting_state, []))
        sequence_counter += 1
        
        processed = set()
        nodes_examined = 0
        
        while priority_queue:
            score, _, active_state, sequence = heapq.heappop(priority_queue)
            
            state_hash = tuple(tuple(line) for line in active_state.grid)
            if state_hash in processed:
                continue
            
            processed.add(state_hash)
            nodes_examined += 1
            
            if active_state.check_victory():
                finish_time = time.time() - begin_time
                return sequence, nodes_examined, finish_time
            
            neighbors = active_state.generate_neighbors()
            
            for next_state, move in neighbors:
                next_hash = tuple(tuple(line) for line in next_state.grid)
                
                if next_hash not in processed:
                    next_score = self.compute_heuristic(next_state)
                    updated_sequence = sequence + [move]
                    heapq.heappush(priority_queue, (next_score, sequence_counter, next_state, updated_sequence))
                    sequence_counter += 1
        
        finish_time = time.time() - begin_time
        return None, nodes_examined, finish_time
