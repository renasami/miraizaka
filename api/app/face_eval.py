import torch
from torch import nn, optim
from torch.utils.data import Dataset, DataLoader
from torchvision import models, transforms
from torchvision.datasets import ImageFolder
import statistics
# print("start program")
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

# print("model loaded successfully")
# print("data loaded successfully")
# print(loader)

def eval(folder:str,net=model,device="cpu"):
    imgs = ImageFolder(
    folder,
    transform=transforms.Compose([
        transforms.Resize(299),
        transforms.CenterCrop(299),
        transforms.ToTensor()
        ])
    )   
    loader = DataLoader(imgs)
    net.eval()
    result = []
    for x,y in loader:
        x = x.to(device)
        y = y.to(device)
        # with torch.no_grad():
        y_pred = net(x)
        print(y_pred)
        idx = torch.argmax(y_pred[0])
        # print(idx.item())
        result.append(idx.item())
    response = statistics.mode(result)
    print(response)
    return response
# eval("./tmp")