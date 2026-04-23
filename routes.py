from flask import Flask, request, jsonify
from flask_cors import CORS
import torch
import torch.nn as nn
from PIL import Image
import io
import torchvision.transforms as transforms
import json

app = Flask(__name__)
CORS(app)

with open("class_map.json", "r") as f:
    class_map = json.load(f)


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


model = SuperNet(num_classes=len(class_map))
model.load_state_dict(torch.load("super_modellino.pth"))
model.eval()


def transform_image(image_bytes):
    transform = transforms.Compose([
        transforms.Grayscale(num_output_channels=1),
        transforms.Resize((32, 32)),
        transforms.ToTensor(),
        transforms.Normalize((0.5,), (0.5,))
    ])
    image = Image.open(io.BytesIO(image_bytes))
    return transform(image).unsqueeze(0)


@app.route('/prediction', methods=['POST'])
def predict():
    if 'file' not in request.files:
        return jsonify({'error': 'No file'}), 400

    file = request.files['file']
    img_bytes = file.read()

    debug_img = Image.open(io.BytesIO(img_bytes)).convert('L').resize((32, 32))
    debug_img.save("debug_vista_modello.png")

    tensor = transform_image(img_bytes)

    with torch.no_grad():
        outputs = model(tensor)
        _, predicted = torch.max(outputs, 1)
        prediction_label = class_map[int(predicted[0])]

    return jsonify({'prediction': prediction_label})


if __name__ == '__main__':
    app.run(port=3000)