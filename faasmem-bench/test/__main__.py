import torch
import torch.nn as nn

class SimpleModel(nn.Module):
    def __init__(self):
        super(SimpleModel, self).__init__()
        self.fc = nn.Linear(10, 2)

    def forward(self, x):
        return self.fc(x)

def main(params):
    model = SimpleModel()
    model.load_state_dict(torch.load('simple_model.pth'))
    model.eval()

    # Dummy inference
    with torch.no_grad():
        input_tensor = torch.randn(1, 10)
        output = model(input_tensor)
    
    result = output.numpy().tolist()

    return {"inference_result": result}
