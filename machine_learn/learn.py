import torch
from torch import nn, optim
from torch.utils.data import Dataset, DataLoader, TensorDataset
import tqdm
from sklearn.model_selection import train_test_split

from torchvision import models
from torchvision.datasets import ImageFolder
from torchvision import transforms
print(torch.__version__)
net = models.vgg16(pretrained=True)

class Identity(nn.Module):
    def __init__(self):
        super(Identity, self).__init__()
        
    def forward(self,x):
        return x

mlp = nn.Sequential(
    nn.Linear(1000,200),
    nn.ReLU(),
    nn.BatchNorm1d(200),
    nn.Dropout(0.5),
    nn.Linear(200,20)
)

net = nn.Sequential(
    net,
    mlp
)
img = ImageFolder(
    "./face",
    transform=transforms.Compose([
      transforms.Resize(299),
      transforms.CenterCrop(299),
      transforms.ToTensor()]    
))


train, test = train_test_split(img, test_size=0.3)

train_loader = DataLoader(
    train,batch_size = 5 , shuffle=True)
test_loader = DataLoader(
    test,batch_size=5,shuffle=False)
print(len(train),len(test))
print(train_loader)

def eval_net(net, data_loader, device="cpu"):
    # DropoutやBatchNormを無効化
    net.eval()
    ys = []
    ypreds = []
    for x, y in data_loader:
        # toメソッドで計算を実行するデバイスに転送する
        x = x.to(device)
        y = y.to(device)
        # 確率が最大のクラスを予測(リスト2.14参照)
        # ここではforward（推論）の計算だけなので自動微分に
        # 必要な処理はoffにして余計な計算を省く
        with torch.no_grad():
            _, y_pred = net(x).max(1)
        ys.append(y)
        ypreds.append(y_pred)
    # ミニバッチごとの予測結果などを1つにまとめる
    ys = torch.cat(ys)
    ypreds = torch.cat(ypreds)
    # 予測精度を計算
    acc = (ys == ypreds).float().sum() / len(ys)
    return acc.item()

def train_net(net, train_loader, test_loader,
              only_fc=True,
              optimizer_cls=optim.Adam,
              loss_fn=nn.CrossEntropyLoss(),
              n_iter=10, device="cpu"):
    train_losses = []
    train_acc = []
    val_acc = []
    if only_fc:
        # 最後の線形層のパラメータのみを、
        # optimizerに渡す
        optimizer = optimizer_cls(net.parameters())
    else:
        optimizer = optimizer_cls(net.parameters())
    for epoch in range(n_iter):
        running_loss = 0.0
        # ネットワークを訓練モードにする
        net.train()
        n = 0
        n_acc = 0
        # 非常に時間がかかるのでtqdmを使用してプログレスバーを出す
        for i, (xx, yy) in tqdm.tqdm(enumerate(train_loader),
            total=len(train_loader)):
            xx = xx.to(device)
            yy = yy.to(device)
            
            h = net(xx)
            loss = loss_fn(h, yy)
            optimizer.zero_grad()
            loss.backward()
            optimizer.step()
            running_loss += loss.item()
            n += len(xx)
            _, y_pred = h.max(1)
            n_acc += (yy == y_pred).float().sum().item()
        train_losses.append(running_loss / i)
        # 訓練データの予測精度
        train_acc.append(n_acc / n)
        # 検証データの予測精度
        val_acc.append(eval_net(net, test_loader, device))
        # このepochでの結果を表示
        print(epoch, train_losses[-1], train_acc[-1],
              val_acc[-1], flush=True)

train_net(net, train_loader, test_loader, n_iter=20, device="cpu")

torch.save(net.state_dict(), "./miraizaka_vgg.pth")
