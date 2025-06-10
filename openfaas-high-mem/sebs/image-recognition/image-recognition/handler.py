import torch
from torchvision import models, transforms
from PIL import Image
import os

# Load the model only once
model = models.resnet50(pretrained=True)
model.eval()

# Define the image preprocessing steps
preprocess = transforms.Compose([
    transforms.Resize(256),
    transforms.CenterCrop(224),
    transforms.ToTensor(),
])

# This will run every time the function is invoked
def handle(event, context):
    # Path to the hardcoded image file
    image_path = os.path.join(os.path.dirname(__file__), 'test.jpg')
    
    # Open and preprocess the image
    image = Image.open(image_path).convert('RGB')
    tensor = preprocess(image).unsqueeze(0)
    
    # Run inference
    with torch.no_grad():
        output = model(tensor)
    top_class = output.argmax().item()
    
    return {
        "statusCode": 200,
        "body": f"Predicted class index: {top_class}"
    }
