import time

def handle(event, context):
    try:
        # Allocate ~26 GiB of memory
        a = bytearray(26 * 1024 * 1024 * 1024)

        # Hold memory for 30 seconds
        time.sleep(30)

        return {
            "statusCode": 200,
            "body": "Allocated 26 GiB of memory and held it for 30 seconds."
        }

    except MemoryError:
        return {
            "statusCode": 500,
            "body": "Memory allocation failed: not enough memory available."
        }
