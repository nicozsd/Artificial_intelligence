import time

class DepthExplorer:
    def __init__(self, max_level=20, limit_seconds=600):
        self.max_level = max_level
        self.limit_seconds = limit_seconds
    
    def execute(self, starting_state):
        begin_time = time.time()
        stack = [(starting_state, [])]
        processed = set()
        nodes_examined = 0
        
        while stack:
            active_state, sequence = stack.pop()
            duration = time.time() - begin_time
            if duration > self.limit_seconds:
                return None, nodes_examined, duration
            
            if len(sequence) > self.max_level:
                continue
            
            state_hash = tuple(tuple(line) for line in active_state.grid)
            if state_hash in processed:
                continue
            
            processed.add(state_hash)
            nodes_examined += 1
            
            if active_state.check_victory():
                finish_time = time.time() - begin_time
                return sequence, nodes_examined, finish_time
            
            neighbors = active_state.generate_neighbors()
            for next_state, move in reversed(neighbors):
                updated_sequence = sequence + [move]
                stack.append((next_state, updated_sequence))
        
        finish_time = time.time() - begin_time
        return None, nodes_examined, finish_time
