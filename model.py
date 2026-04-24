from os.path import exists

import torch
import torch.nn as nn
import torch.optim as optim
from torchvision import datasets, transforms
from torch.utils.data import DataLoader, Dataset, ConcatDataset
import pandas as pd
from PIL import Image
import os
import json
import kagglehub


class HASYDataset(Dataset):
    def __init__(self, csv_file, img_dir, transform=None):
        self.df = pd.read_csv(csv_file)
        self.img_dir = img_dir
        self.transform = transform

        self.classes = sorted(self.df['latex'].unique())
        self.class_to_idx = {cls: i for i, cls in enumerate(self.classes)}

    def __len__(self):
        return len(self.df)

    def __getitem__(self, idx):
        img_name = os.path.join(self.img_dir, self.df.iloc[idx, 0])
        image = Image.open(img_name).convert('L')

        label_name = self.df.iloc[idx, 2]
        label = self.class_to_idx[label_name]

        if self.transform:
            image = self.transform(image)
        return image, label

class OffsetDataset(Dataset):
    def __init__(self, dataset, offset):
        self.dataset = dataset
        self.offset = offset
    def __len__(self):
        return len(self.dataset)
    def __getitem__(self, i):
        img, label = self.dataset[i]
        return img, label + self.offset

class SuperNet(nn.Module):
    def __init__(self, num_classes):
        super(SuperNet, self).__init__()
        self.features = nn.Sequential(
            nn.Conv2d(1, 32, 3, padding=1), nn.ReLU(),
            nn.MaxPool2d(2, 2),
            nn.Conv2d(32, 64, 3, padding=1), nn.ReLU(),
            nn.MaxPool2d(2, 2)
        )
        self.classifier = nn.Sequential(
            nn.Flatten(),
            nn.Linear(64 * 8 * 8, 512),
            nn.ReLU(),
            nn.Dropout(0.3),
            nn.Linear(512, num_classes)
        )
    def forward(self, x):
        return self.classifier(self.features(x))

try:
    if exists("model/modellino.pth"):
        print("Modellino già esistente")
        exit(0)

    transform_emnist = transforms.Compose([
        transforms.Resize((32, 32)),
        transforms.ToTensor(),
        lambda x: x.transpose(1, 2),
        transforms.Normalize((0.5,), (0.5,))
    ])

    transform_hasy = transforms.Compose([
        transforms.Resize((32, 32)),
        transforms.ToTensor(),
        lambda x: 1.0 - x,
        transforms.Normalize((0.5,), (0.5,))
    ])

    print("Scaricamento dataset HASYv2 tramite KaggleHub...")
    path = kagglehub.dataset_download("guru001/hasyv2")
    hasy_csv = os.path.join(path, "hasy-data-labels.csv")
    hasy_img_dir = path

    emnist_train = datasets.EMNIST(root='./data', split='balanced', train=True, download=True, transform=transform_emnist)
    emnist_classes = "0123456789ABCDEFGHIJKLMNOPQRSTUVWXYZabdefghnqrt"

    hasy_train = HASYDataset(csv_file=hasy_csv, img_dir=hasy_img_dir, transform=transform_hasy)

    full_class_map = list(emnist_classes) + hasy_train.classes
    num_total_classes = len(full_class_map)

    combined_dataset = ConcatDataset([
        emnist_train,
        OffsetDataset(hasy_train, len(emnist_classes))
    ])

    train_loader = DataLoader(combined_dataset, batch_size=128, shuffle=True)

    device = torch.device("cuda" if torch.cuda.is_available() else "cpu")
    model = SuperNet(num_classes=num_total_classes).to(device)

    criterion = nn.CrossEntropyLoss()
    optimizer = optim.Adam(model.parameters(), lr=0.001)

    print(f"Inizio addestramento su {num_total_classes} classi usando {device}...")
    for epoch in range(10):
        running_loss = 0.0
        i = 0
        for images, labels in train_loader:
            images, labels = images.to(device), labels.to(device)
            optimizer.zero_grad()
            outputs = model(images)
            loss = criterion(outputs, labels)
            loss.backward()
            optimizer.step()
            running_loss += loss.item()
            i+=1
            if i%100 == 0: print(f"Allenamento sull'immagine numero {i - 100} / {i}")
        print(f"Epoca {epoch+1} - Loss: {running_loss/len(train_loader):.4f}\n\n")

    torch.save(model.state_dict(), "model/modellino.pth")
    with open("model/class_map.json", "w") as f:
        json.dump(full_class_map, f)

    print("\n\nProcesso completato.")

except Exception as e:
    print("\n\nProbabile chiusura => ")
    exit(1)