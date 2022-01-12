import torch
from torch import nn, optim
from torch.utils.data import Dataset, DataLoader
from torchvision import models, transforms
from torchvision.datasets import ImageFolder
print("start program")
net = models.vgg16(pretrained=True)

mlp = nn.Sequential(
    nn.Linear(1000,200),
    nn.ReLU(),
    nn.BatchNorm1d(200),
    nn.Dropout(0.5),
    nn.Linear(200,20)
)

model = nn.Sequential(
    net,
    mlp
)

model.load_state_dict(torch.load("./miraizaka_vgg.pth"))

print("model loaded successfully")

imgs = ImageFolder(
    "./tmp",
    transform=transforms.Compose([
        transforms.Resize(299),
        transforms.CenterCrop(299),
        transforms.ToTensor()
    ])
)

loader = DataLoader(imgs)
print("data loaded successfully")
print(loader)

def eval(net,loader,device="cpu"):
    net.eval()
    for x,y in loader:
        x = x.to(device)
        y = y.to(device)
        # with torch.no_grad():
        y_pred = net(x)
        print(y_pred)
        idx = torch.argmax(y_pred[0])
        print(idx.item())

eval(model,loader)