import requests
import concurrent.futures
import json
from base64 import b64encode

# OpenWhisk configuration
API_HOST = "http://172.17.0.1:3233"  # API Host from your Postman setup
ACTION_PATH = "/api/v1/namespaces/guest/actions/dli?blocking=true"  # Action path
AUTH_KEY = "MjNiYzQ2YjEtNzFmNi00ZWQ1LThjNTQtODE2YWE0ZjhjNTAyOjEyM3pPM3haQ0xyTU42djJCS0sxZFhZRnBYbFBrY2NPRnFtMTJDZEFzTWdSVTRWck5aOWx5R1ZDR3VNREdJd1A="  # Replace with your actual key
NUM_REQUESTS = 100  # Number of concurrent invocations

def invoke_action():
    """
    Function to invoke the OpenWhisk action using the provided API endpoint.
    :return: Response from the invocation.
    """
    url = f"{API_HOST}{ACTION_PATH}"
    headers = {
        "Content-Type": "application/json",
        "Authorization": f"Basic {AUTH_KEY}"  # Add Basic Authorization header
    }
    payload = {"model": "vgg16"}  # Update the payload as needed

    try:
        # Send POST request
        response = requests.post(url, headers=headers, data=json.dumps(payload))
        return response.status_code, response.json()
    except Exception as e:
        return "Error", str(e)

def main():
    # Use ThreadPoolExecutor to invoke actions concurrently
    with concurrent.futures.ThreadPoolExecutor(max_workers=NUM_REQUESTS) as executor:
        # Submit NUM_REQUESTS invocations
        futures = [executor.submit(invoke_action) for _ in range(NUM_REQUESTS)]
        
        # Wait for all futures to complete and collect results
        for future in concurrent.futures.as_completed(futures):
            status, response = future.result()
            print(f"Status: {status}, Response: {response}")

if __name__ == "__main__":
    main()
