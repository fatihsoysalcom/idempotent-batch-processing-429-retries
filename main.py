import random
import time
import requests
from flask import Flask, request, jsonify
import threading

app = Flask(__name__)

# --- Simulated Server-side State ---
# Stores processed batch IDs to ensure idempotency
processed_batches = {}
# A simple counter to see how many times processing logic was *actually* executed
processing_execution_count = {}

# --- Server-side Endpoint ---
@app.route('/process_batch', methods=['POST'])
def process_batch():
    batch_id = request.json.get('batch_id')
    data = request.json.get('data')

    if not batch_id or not data:
        return jsonify({"error": "batch_id and data are required"}), 400

    # 1. Idempotency Check: Has this batch ID been successfully processed before?
    # This is the core mechanism to prevent duplicate processing even if the client retries.
    if batch_id in processed_batches:
        print(f"[SERVER] Batch {batch_id} already processed. Returning success (idempotent).")
        return jsonify({
            "status": "success",
            "message": "Batch already processed (idempotent)",
            "data": processed_batches[batch_id]
        }), 200

    # 2. Simulate actual processing (e.g., database transaction)
    print(f"[SERVER] Processing batch {batch_id} with data: {data}...")
    # Increment execution count for demonstration purposes
    processing_execution_count[batch_id] = processing_execution_count.get(batch_id, 0) + 1
    time.sleep(0.1) # Simulate some work

    # Store the result *before* potential rate limit error. This simulates the scenario
    # where the server successfully completes its work but fails to send the response.
    processed_batches[batch_id] = data
    print(f"[SERVER] Batch {batch_id} processing complete and saved to 'DB'.")

    # 3. Simulate Rate Limiting (HTTP 429) *after* successful processing
    # This is the crucial part described in the article: server succeeded, but response fails.
    if random.random() < 0.4: # 40% chance of 429
        print(f"[SERVER] Simulating HTTP 429 error for batch {batch_id} after processing!")
        return jsonify({"error": "Too Many Requests (simulated rate limit)"}), 429

    # 4. Return success if no rate limit error occurred
    print(f"[SERVER] Successfully responded for batch {batch_id}.")
    return jsonify({
        "status": "success",
        "message": "Batch processed successfully",
        "data": data
    }), 200

# --- Client-side Logic ---
def run_client_simulation():
    print("\n--- Client Simulation Started ---")
    batch_id = "batch_abc_123"
    batch_data = {"items": [1, 2, 3], "user": "test_user"}
    max_retries = 3
    retry_delay_seconds = 1

    for attempt in range(max_retries + 1):
        print(f"\n[CLIENT] Attempt {attempt + 1} for batch {batch_id}...")
        try:
            response = requests.post(
                'http://127.0.0.1:5000/process_batch',
                json={'batch_id': batch_id, 'data': batch_data}
            )

            if response.status_code == 200:
                print(f"[CLIENT] Batch {batch_id} successfully processed (status 200). Response: {response.json()}")
                break # Exit retry loop on success
            elif response.status_code == 429:
                if attempt < max_retries:
                    print(f"[CLIENT] Received 429 Too Many Requests. Retrying in {retry_delay_seconds}s...")
                    time.sleep(retry_delay_seconds)
                else:
                    print(f"[CLIENT] Received 429 Too Many Requests. Max retries reached.")
                    break
            else:
                print(f"[CLIENT] Unexpected error: {response.status_code} - {response.json()}")
                break
        except requests.exceptions.ConnectionError as e:
            print(f"[CLIENT] Connection error: {e}. Is the server running? Retrying in {retry_delay_seconds}s...")
            time.sleep(retry_delay_seconds)
        except Exception as e:
            print(f"[CLIENT] An unexpected client error occurred: {e}")
            break
    else:
        print(f"[CLIENT] Failed to process batch {batch_id} after {max_retries + 1} attempts.")

    print("\n--- Client Simulation Finished ---")
    print("\n--- Server-side Final State ---")
    print(f"Processed Batches (Idempotent Store): {processed_batches}")
    print(f"Actual Processing Logic Executions: {processing_execution_count}")
    print("Expected: 'processing_execution_count' for 'batch_abc_123' should be 1, even with retries.")

if __name__ == '__main__':
    # Start Flask server in a separate thread
    def run_flask_app():
        app.run(port=5000, debug=False, use_reloader=False)

    print("Starting Flask server in a separate thread...")
    server_thread = threading.Thread(target=run_flask_app)
    server_thread.daemon = True # Allow main program to exit even if thread is still running
    server_thread.start()

    # Give the server a moment to start up
    time.sleep(2) # Wait for the server to initialize

    run_client_simulation()

    print("\nServer thread will terminate when the main script exits.")
