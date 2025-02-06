import requests
import concurrent.futures
import json
import random

# OpenWhisk configuration
API_HOST = "http://172.17.0.1:3233"  # API Host
AUTH_KEY = "MjNiYzQ2YjEtNzFmNi00ZWQ1LThjNTQtODE2YWE0ZjhjNTAyOjEyM3pPM3haQ0xyTU42djJCS0sxZFhZRnBYbFBrY2NPRnFtMTJDZEFzTWdSVTRWck5aOWx5R1ZDR3VNREdJd1A="  # Replace with your actual key

# Actions and their payloads
ACTIONS = {
    "dli": {"model": "vgg16"},
    "ip": {"model": "resnet50"},
    "ma": {"model": "mobilenet"}, 
    "vp": {"model": "inceptionv3"}
}

NUM_USERS = 500  # Total number of users
USERS_PER_ACTION = NUM_USERS // len(ACTIONS)  # Distribute users evenly across actions
MAX_WORKERS = 50  # Number of threads for parallelism

def invoke_action(action_name, payload):
    """
    Function to invoke an OpenWhisk action.
    :param action_name: Name of the action to invoke.
    :param payload: JSON payload for the action.
    :return: Response from the invocation.
    """
    url = f"{API_HOST}/api/v1/namespaces/guest/actions/{action_name}"
    headers = {
        "Content-Type": "application/json",
        "Authorization": f"Basic {AUTH_KEY}"  # Add Basic Authorization header
    }

    try:
        # Send POST request
        response = requests.post(url, headers=headers, data=json.dumps(payload))
        return response.status_code, response.json()
    except Exception as e:
        return "Error", str(e)

def main():
    # Create a randomized invocation list for all users
    invocations = []
    for action_name, payload in ACTIONS.items():
        invocations.extend([(action_name, payload)] * USERS_PER_ACTION)
    random.shuffle(invocations)  # Randomize the order of invocations

    # Use ThreadPoolExecutor to invoke actions in parallel
    with concurrent.futures.ThreadPoolExecutor(max_workers=MAX_WORKERS) as executor:
        # Submit invocations for all users
        futures = [executor.submit(invoke_action, action_name, payload) for action_name, payload in invocations]
        
        # Wait for all futures to complete and collect results
        for future in concurrent.futures.as_completed(futures):
            status, response = future.result()
            print(f"Status: {status}, Response: {response}")

if __name__ == "__main__":
    main()
