import torch
from torch import nn
from PIL import Image
from torchvision import transforms,models
from torch.autograd import Variable

print("start program")

test_img = "./1a001.png"
loader = transforms.Compose([
    transforms.Resize(299),
      transforms.CenterCrop(299),
      transforms.ToTensor(),
      transforms.Normalize(mean=[0.484,0.456,0.406],std=[0.229,0.224,0.225])
    ])
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


net = model.load_state_dict(torch.load("./miraizaka_vgg.pth"))
print(type(model))
model.eval()


def img_loader(path):
    img = Image.open(path)
    img.thumbnail(500,500)
    img = loader(img)
    # img = Variable(img, requires_grad=True)
    img = img.unsqueeze(0)
    return img

m = nn.Softmax(dim=1)
img = img_loader(test_img)
print(model(img))


#python face_rec.py