from PIL import Image
import numpy as np

def handler(event, context):
    image = Image.open("./large_image.jpg")
    image_array = np.array(image)
    processed_image = image_array ** 2  # Simulate a computationally heavy operation
    return {"status": "Success", "processed_image_shape": str(processed_image.shape)}
