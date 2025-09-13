import io
import torch
import torchvision.transforms as transforms
from torchvision import models
from PIL import Image
import requests

# Load model once at cold start
device = torch.device("cpu")
model = models.densenet201(pretrained=True)
model.eval()

# Preprocessing pipeline
preprocess = transforms.Compose([
    transforms.Resize(256),
    transforms.CenterCrop(224),
    transforms.ToTensor(),
    transforms.Normalize(
        mean=[0.485, 0.456, 0.406], 
        std=[0.229, 0.224, 0.225]
    ),
])

# Load ImageNet labels once
LABELS_URL = "https://raw.githubusercontent.com/pytorch/hub/master/imagenet_classes.txt"
labels = requests.get(LABELS_URL).text.splitlines()

# Hard-coded image URL (no CLI param required)
HARDCODED_IMAGE_URL = "https://upload.wikimedia.org/wikipedia/commons/9/9a/Pug_600.jpg"

def handler(event, context=None):
    try:
        # Always use the hardcoded URL
        response = requests.get(HARDCODED_IMAGE_URL, headers={"User-Agent": "Mozilla/5.0"})
        response.raise_for_status()

        if "image" not in response.headers.get("Content-Type", ""):
            return {
                "statusCode": 400,
                "body": f"Hardcoded URL did not return an image, got: {response.headers.get('Content-Type')}"
            }

        # Open and normalize image
        image = Image.open(io.BytesIO(response.content)).convert("RGB")

        # Preprocess + batchify
        input_tensor = preprocess(image).unsqueeze(0).to(device)

        # Run inference
        with torch.no_grad():
            output = model(input_tensor)
            probabilities = torch.nn.functional.softmax(output[0], dim=0)

        # Top-5 predictions
        top5_prob, top5_catid = torch.topk(probabilities, 5)
        results = [
            {"label": labels[catid], "probability": float(prob)}
            for prob, catid in zip(top5_prob, top5_catid)
        ]

        return {
            "statusCode": 200,
            "body": results
        }

    except Exception as e:
        return {
            "statusCode": 500,
            "body": str(e)
        }
