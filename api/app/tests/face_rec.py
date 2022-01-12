import torch
from torch import nn
from PIL import Image
from torchvision import transforms,models
from torch.autograd import Variable
from torchvision.datasets import ImageFolder
from torch.utils.data import DataLoader
import cv2
from PIL import Image
from torch.autograd import Variable

print("start program")


# loader = transforms.Compose([
#       transforms.Resize(299),
#       transforms.CenterCrop(299),
#       transforms.ToTensor(),
#       transforms.Normalize([0.5], [0.5])
#     ])


def img_loader(path):
    img = Image.open(path)
    # img = loader(img)
    # img = Variable(img, requires_grad=True)
    # img = img.unsqueeze(0)
    return img

# img = img_loader(test_img)
# print(img)
# print(model(loader))

def read(img_file,transform):
    image = cv2.imread(img_file, cv2.COLOR_BGR2GRAY)
    # 稀に31x32の画像サイズが含まれているので補正
    image = cv2.resize(image, (32, 32))

    image = transform(image)
    return image

def main():
    device = torch.device("cpu")
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
    #!重要
    model.load_state_dict(torch.load("./miraizaka_vgg.pth"))
    print("model loaded")
    # print(model)
    model.eval()
    #!重要ここまで
    test_img = Image.open("./1a001.png")
    cv2_data = read("./1a001.png",transform=transforms.Compose([
        transforms.ToTensor(),
        transforms.Normalize([0.485, ], [0.229, ])
    ]))

    print(test_img)
    test_img.convert("1")
    print(test_img.mode)
    print("img loaded")
    process = transforms.Compose([
        transforms.Resize(256),
        transforms.CenterCrop(224),
        transforms.ToTensor(),
        transforms.Normalize(
            (0.5), (0.5)
        )
    ])
    data = process(test_img)
    print('img shaped')
    print(data.shape)
    torch.Size([3, 224, 224])
    data = data.unsqueeze_(0)
    print(data)
    data.to("cpu")
    # data = data.view(64,3,3,3)
    output = model(data)
    pred = output.argmax(dim=1,keepdim=True)
    print(pred[0].item())
#python face_rec.py

main()