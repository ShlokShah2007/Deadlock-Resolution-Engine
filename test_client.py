import time
import requests

BASE_URL = "http://127.0.0.1:8000"

def run_demo():
    print("--- Resetting Engine State ---")
    requests.delete(f"{BASE_URL}/reset")
    time.sleep(0.5)

    # Sequence of requests forming a deadlock: Tx1 -> Tx2 -> Tx3 -> Tx1
    events = [
        {"requester": "Tx1", "holder": "Tx2"},
        {"requester": "Tx2", "holder": "Tx3"},
        {"requester": "Tx3", "holder": "Tx1"}  # This triggers the deadlock
    ]

    for event in events:
        print(f"\nSending Request: {event['requester']} is waiting for {event['holder']}")
        response = requests.post(f"{BASE_URL}/request-lock", json=event)
        data = response.json()
        
        print(f"Server Response Message: {data.get('message')}")
        print(f"Current Wait-For Graph: {data.get('current_graph')}")
        
        if data.get("deadlock_detected"):
            print(f"🚨 [ALERT] Deadlock caught! Aborted victims: {data.get('aborted_victims')}")
        
        time.sleep(1)

if __name__ == "__main__":
    print("Starting Automated Deadlock Simulation Client...")
    try:
        run_demo()
    except requests.exceptions.ConnectionError:
        print("\n❌ Error: Could not connect to the API server. Make sure 'python -m uvicorn app:app --reload' is running!")