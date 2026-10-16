from fastapi import FastAPI, HTTPException
from pydantic import BaseModel
from typing import Dict, List, Set

app = FastAPI(
    title="Database Concurrency & Deadlock Resolution Engine",
    description="An API-driven graph engine for detecting and resolving deadlocks using Wait-For Graphs."
)

class DeadlockEngine:
    def __init__(self):
        # Adjacency list: Transaction ID -> Set of Transaction IDs it is waiting for
        self.wfg: Dict[str, Set[str]] = {}

    def add_edge(self, requester: str, holder: str):
        if requester == holder:
            raise HTTPException(status_code=400, detail="A transaction cannot wait for itself.")
        if requester not in self.wfg:
            self.wfg[requester] = set()
        self.wfg[requester].add(holder)
        
        if holder not in self.wfg:
            self.wfg[holder] = set()

    def remove_transaction(self, tx_id: str):
        if tx_id in self.wfg:
            del self.wfg[tx_id]
        for node in self.wfg:
            self.wfg[node].discard(tx_id)

    def find_cycle(self):
        """
        Custom Depth-First Search (DFS) for cycle detection.
        Node states: 0 = Unvisited, 1 = Visiting (in current stack), 2 = Visited
        """
        visited = {node: 0 for node in self.wfg}
        path = []

        def dfs(node):
            visited[node] = 1
            path.append(node)

            for neighbor in self.wfg.get(node, set()):
                if visited.get(neighbor, 0) == 1:
                    cycle_start_index = path.index(neighbor)
                    return path[cycle_start_index:]
                elif visited.get(neighbor, 0) == 0:
                    result = dfs(neighbor)
                    if result:
                        return result

            path.pop()
            visited[node] = 2
            return None

        for node in list(self.wfg.keys()):
            if visited[node] == 0:
                cycle = dfs(node)
                if cycle:
                    return cycle
        return None

    def check_and_resolve(self):
        """Continuously checks for cycles and automatically aborts a victim transaction if a deadlock occurs."""
        aborted_victims = []
        while True:
            cycle = self.find_cycle()
            if not cycle:
                break
            victim = cycle[-1]  # Choose the last node in the cycle as the victim
            self.remove_transaction(victim)
            aborted_victims.append(victim)
        return aborted_victims, cycle

# Initialize global engine instance
engine = DeadlockEngine()

# Pydantic model for request validation
class LockRequest(BaseModel):
    requester: str
    holder: str

@app.post("/request-lock")
def request_lock(req: LockRequest):
    """
    Endpoint to simulate a transaction requesting a lock. 
    Automatically builds the graph and triggers deadlock resolution if a cycle is formed.
    """
    try:
        engine.add_edge(req.requester, req.holder)
        
        # Check if this request caused a deadlock
        aborted, cycle = engine.check_and_resolve()
        
        response_data = {
            "status": "success",
            "message": f"Lock request registered: {req.requester} waiting for {req.holder}",
            "current_graph": {k: list(v) for k, v in engine.wfg.items()}
        }
        
        if aborted:
            response_data["deadlock_detected"] = True
            response_data["aborted_victims"] = aborted
            response_data["message"] += f" | DEADLOCK! Aborted transactions: {aborted}"
        else:
            response_data["deadlock_detected"] = False
            
        return response_data

    except Exception as e:
        raise HTTPException(status_code=400, detail=str(e))

@app.get("/graph")
def get_graph_state():
    """Returns the current state of the Wait-For Graph."""
    return {
        "graph": {k: list(v) for k, v in engine.wfg.items()}
    }

@app.delete("/reset")
def reset_engine():
    """Resets the graph state."""
    global engine
    engine = DeadlockEngine()
    return {"message": "Engine reset successfully."}