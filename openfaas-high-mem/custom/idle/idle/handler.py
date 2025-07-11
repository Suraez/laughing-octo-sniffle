# Allocate and touch memory at import time
MEM_BLOCKS = []

def reserve_memory(mib):
    for _ in range(mib):
        block = bytearray(1024 * 1024)
        block[0] = 1
        MEM_BLOCKS.append(block)

# Reserve 500 MiB at startup
reserve_memory(2000)

def handle(event, context):
    return {
        "statusCode": 200,
        "body": f"Pre-allocated 500 MiB memory at startup."
    }
