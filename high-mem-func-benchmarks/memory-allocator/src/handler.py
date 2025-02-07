def handler(event, context):
    data = []
    for _ in range(100):
        data.append(bytearray(50 * 1024 * 1024))  # Allocate 50 MB chunks
    return {"status": "Success", "memory_allocated_MB": len(data) * 50}
