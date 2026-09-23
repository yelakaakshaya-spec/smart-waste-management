from flask import Flask, render_template, request, jsonify
import torch
from torchvision import models, transforms
import torch.nn as nn
from PIL import Image
import os
import urllib.request

app = Flask(__name__)

MODEL_URL = "https://github.com/yelakaakshaya-spec/smart-waste-management/releases/download/v1.0/waste_model.pth"
MODEL_PATH = "waste_model.pth"

if not os.path.exists(MODEL_PATH):
    urllib.request.urlretrieve(MODEL_URL, MODEL_PATH)

model = models.resnet18(weights=None)
model.fc = nn.Linear(model.fc.in_features, 3)

model.load_state_dict(
    torch.load(MODEL_PATH, map_location="cpu")
)
model.eval()

classes = ["organic", "paper", "plastic"]

# -----------------------------
# Image preprocessing
# -----------------------------
transform = transforms.Compose([
    transforms.Resize((224, 224)),
    transforms.ToTensor(),
    transforms.Normalize(
        mean=[0.485, 0.456, 0.406],
        std=[0.229, 0.224, 0.225]
    )
])

# -----------------------------
# Recommendations
# -----------------------------
recommendations = {
    "organic": "Put it in the organic/biodegradable waste stream.",
    "paper": "Put it in the paper/recyclable waste stream.",
    "plastic": "Put it in the plastic/recyclable waste stream."
}

tips = {
    "organic": "Organic waste such as food and fruit can be composted.",
    "paper": "Keep paper clean and dry to make recycling easier.",
    "plastic": "Clean plastic containers before recycling."
}


# -----------------------------
# Home page
# -----------------------------
@app.route("/")
def home():
    return render_template("index.html")


# -----------------------------
# Prediction API
# -----------------------------
@app.route("/predict", methods=["POST"])
def predict():

    if "image" not in request.files:
        return jsonify({"error": "No image uploaded"}), 400

    file = request.files["image"]

    if file.filename == "":
        return jsonify({"error": "No image selected"}), 400

    try:
        image = Image.open(file).convert("RGB")

        input_image = transform(image).unsqueeze(0)

        with torch.no_grad():
            output = model(input_image)
            probabilities = torch.softmax(output, dim=1)
            confidence, predicted = torch.max(probabilities, 1)

        predicted_class = classes[predicted.item()]
        confidence_value = confidence.item() * 100

        return jsonify({
            "category": predicted_class,
            "confidence": round(confidence_value, 2),
            "recommendation": recommendations[predicted_class],
            "tip": tips[predicted_class]
        })

    except Exception as e:
        return jsonify({"error": str(e)}), 500


# -----------------------------
# Start server
# -----------------------------
if __name__ == "__main__":
    app.run(debug=True)
