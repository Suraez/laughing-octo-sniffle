import torch
import torch.nn as nn

class SimpleModel(nn.Module):
    def __init__(self):
        super(SimpleModel, self).__init__()
        self.fc = nn.Linear(10, 2)

    def forward(self, x):
        return self.fc(x)

# Save model (run once)
if __name__ == "__main__":
    model = SimpleModel()
    torch.save(model.state_dict(), 'simple_model.pth')
