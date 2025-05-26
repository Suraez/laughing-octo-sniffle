import numpy as np
import time
import json

def matmul(n):
    A = np.random.rand(n, n)
    B = np.random.rand(n, n)
    start = time.time()
    C = np.matmul(A, B)
    latency = time.time() - start
    return latency

def handle(event, context):
    try:
        n = 86400  # Hardcoded matrix size
        latency = matmul(n)

        return {
            "statusCode": 200,
            "body": json.dumps({
                "matrix_size": n,
                "latency_sec": latency
            })
        }

    except Exception as e:
        return {
            "statusCode": 500,
            "body": f"Error: {str(e)}"
        }
