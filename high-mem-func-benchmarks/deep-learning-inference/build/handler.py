import torch
import torch.nn as nn

class SimpleModel(nn.Module):
    def __init__(self):
        super(SimpleModel, self).__init__()
        self.fc = nn.Linear(1024, 1024)

    def forward(self, x):
        return self.fc(x)

def handler(event, context):
    model = SimpleModel()
    input_tensor = torch.randn(1024, 1024)
    output = model(input_tensor)
    return {"status": "Success", "output_shape": str(output.shape)}
