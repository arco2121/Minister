import os
import json
import torch
import torch.nn as nn
import torch.optim as optim
from torchvision import datasets, transforms
from torch.utils.data import DataLoader, Dataset, ConcatDataset
import pandas as pd
from PIL import Image
import kagglehub
from os.path import exists

BATCH_SIZE = 256
EPOCHS = 30
LEARNING_RATE = 0.001
MODEL_PATH = "model/modellino.pth"
CLASS_MAP_PATH = "model/class_map.json"

def transpose_img(x):
    return x.transpose(1, 2)

def invert_img(x):
    return 1.0 - x


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
        # .convert('L') carica già in scala di grigi risparmiando memoria
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


def train_model():
    if not os.path.exists("model"):
        os.makedirs("model")

    if exists(MODEL_PATH):
        print("Modellino già esistente. Salto l'addestramento.")
        return

    transform_emnist = transforms.Compose([
        transforms.Resize((32, 32)),
        transforms.ToTensor(),
        transforms.Lambda(transpose_img),
        transforms.Normalize((0.5,), (0.5,))
    ])

    transform_hasy = transforms.Compose([
        transforms.Resize((32, 32)),
        transforms.ToTensor(),
        transforms.Lambda(invert_img),
        transforms.Normalize((0.5,), (0.5,))
    ])

    print("\nScaricamento dataset...")
    path = kagglehub.dataset_download("guru001/hasyv2")
    hasy_csv = os.path.join(path, "hasy-data-labels.csv")

    emnist_train = datasets.EMNIST(root='./data', split='balanced', train=True, download=True,
                                   transform=transform_emnist)
    emnist_classes = "0123456789ABCDEFGHIJKLMNOPQRSTUVWXYZabdefghnqrt"

    hasy_train = HASYDataset(csv_file=hasy_csv, img_dir=path, transform=transform_hasy)

    full_class_map = list(emnist_classes) + hasy_train.classes
    num_total_classes = len(full_class_map)

    combined_dataset = ConcatDataset([
        emnist_train,
        OffsetDataset(hasy_train, len(emnist_classes))
    ])

    train_loader = DataLoader(
        combined_dataset,
        batch_size=BATCH_SIZE,
        shuffle=True,
        num_workers=0,
        pin_memory=True
    )

    device = torch.device("cuda" if torch.cuda.is_available() else "cpu")
    model = SuperNet(num_classes=num_total_classes).to(device)

    use_amp = torch.cuda.is_available()
    scaler = torch.amp.GradScaler('cuda', enabled=use_amp)

    criterion = nn.CrossEntropyLoss()
    optimizer = optim.Adam(model.parameters(), lr=LEARNING_RATE)

    print(f"Inizio addestramento su {num_total_classes} classi usando {device}...")

    model.train()
    for epoch in range(EPOCHS):
        running_loss = 0.0
        for i, (images, labels) in enumerate(train_loader):
            images, labels = images.to(device, non_blocking=True), labels.to(device, non_blocking=True)
            optimizer.zero_grad(set_to_none=True)

            with torch.amp.autocast('cuda', enabled=use_amp):
                outputs = model(images)
                loss = criterion(outputs, labels)

            if use_amp:
                scaler.scale(loss).backward()
                scaler.step(optimizer)
                scaler.update()
            else:
                loss.backward()
                optimizer.step()

            running_loss += loss.item()

            if i % 200 == 0:
                print(f"Epoca [{epoch + 1}/{EPOCHS}] Step [{i}/{len(train_loader)}] Loss: {loss.item():.4f}")

        print(f"✅ Epoca {epoch + 1} completata. Average Loss: {running_loss / len(train_loader):.4f}")

    torch.save(model.state_dict(), MODEL_PATH)
    with open(CLASS_MAP_PATH, "w") as f:
        json.dump(full_class_map, f)
    print("\nModello salvato con successo!")

if __name__ == "__main__":
    try:
        train_model()
    except Exception as e:
        print(f"Errore critico: {e}")
        exit(1)