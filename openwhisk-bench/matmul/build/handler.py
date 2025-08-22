import numpy as np
import time

def matmul(n):
    A = np.random.rand(n, n)
    B = np.random.rand(n, n)
    start = time.time()
    C = np.matmul(A, B)
    latency = time.time() - start
    return latency

def handler(event, context=None):
    try:
        n = int(event.get("body", 100))  # Default to 100 if not provided
        result = matmul(n)
        return {
            "statusCode": 200,
            "body": {
                "latency": result,
                "message": f"Matrix multiplication of size {n}x{n} completed in {result:.4f} seconds."
            }
        }
    except Exception as e:
        return {
            "statusCode": 500,
            "error": str(e)
        }


if __name__ == "__main__":
    print(handler(None))