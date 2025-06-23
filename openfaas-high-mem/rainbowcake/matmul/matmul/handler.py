import numpy as np
import time

def matmul(n):
    A = np.random.rand(n, n)
    B = np.random.rand(n, n)

    start = time.time()
    C = np.matmul(A, B)
    latency = time.time() - start
    return latency

def handle(event, context):
    n = int(event.body)
    result = matmul(n)
    return {
        "statusCode": 200,
        "body": str(result)
    }
