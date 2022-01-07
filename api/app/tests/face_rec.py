import torch
from torch import nn
from PIL import Image
from torchvision import transforms,models
from torch.autograd import Variable

print("start program")

test_img = "./1a001.png"
loader = transforms.Compose([transforms.Resize(299),
      transforms.CenterCrop(299),
      transforms.ToTensor()])
vgg = models.vgg16(pretrained=True)
mlp = nn.Sequential(
    nn.Linear(1000,200),
    nn.ReLU(),
    nn.BatchNorm1d(200),
    nn.Dropout(0.5),
    nn.Linear(200,20)
)
model = nn.Sequential(
    vgg,
    mlp
)
model = model.load_state_dict(torch.load("./miraizaka_vgg.pth"))

# model.eval()


def img_loader(path):
    img = Image.open(path)
    img = loader(img)
    img = Variable(img, requires_grad=True)
    img = img.unsqueeze(0)
    return img

m = nn.Softmax(dim=1)
img = img_loader(test_img)
print(m(model(img)))


#python face_rec.py