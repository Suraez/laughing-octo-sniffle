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

preprocess = transforms.Compose([
    transforms.Resize(256),
    transforms.CenterCrop(224),
    transforms.ToTensor(),
    transforms.Normalize(
        mean=[0.485, 0.456, 0.406], 
        std=[0.229, 0.224, 0.225]
    ),
])

LABELS_URL = "https://raw.githubusercontent.com/pytorch/hub/master/imagenet_classes.txt"
labels = requests.get(LABELS_URL).text.splitlines()

def handler(params):
    try:
        if "image_url" not in params:
            return {"statusCode": 400, "body": "Missing required parameter: image_url"}

        url = params["image_url"]
        resp = requests.get(url, headers={"User-Agent": "Mozilla/5.0"})
        resp.raise_for_status()

        if "image" not in resp.headers.get("Content-Type", ""):
            return {"statusCode": 400, "body": f"URL did not return an image, got: {resp.headers.get('Content-Type')}"}

        image = Image.open(io.BytesIO(resp.content)).convert("RGB")
        input_tensor = preprocess(image).unsqueeze(0).to(device)

        with torch.no_grad():
            output = model(input_tensor)
            probabilities = torch.nn.functional.softmax(output[0], dim=0)

        top5_prob, top5_catid = torch.topk(probabilities, 5)
        results = [
            {"label": labels[catid], "probability": float(prob)}
            for prob, catid in zip(top5_prob, top5_catid)
        ]

        return {"statusCode": 200, "body": results}

    except Exception as e:
        return {"statusCode": 500, "body": str(e)}
