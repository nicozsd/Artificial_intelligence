from collections import deque
import time

class BreadthExplorer:
    def execute(self, starting_state):
        begin_time = time.time()
        queue = deque([(starting_state, [])])
        processed = {starting_state}
        nodes_examined = 0
        
        while queue:
            active_state, sequence = queue.popleft()
            nodes_examined += 1
            
            if active_state.check_victory():
                finish_time = time.time() - begin_time
                return sequence, nodes_examined, finish_time
            
            for next_state, move in active_state.generate_neighbors():
                if next_state not in processed:
                    processed.add(next_state)
                    updated_sequence = sequence + [move]
                    queue.append((next_state, updated_sequence))
        
        finish_time = time.time() - begin_time
        return None, nodes_examined, finish_time
