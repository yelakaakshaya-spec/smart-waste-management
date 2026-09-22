import torch
from torchvision import datasets, transforms

print("PyTorch is ready!")

data_path = "dataset"
classes = ["organic", "paper", "plastic"]

transform = transforms.Compose([
    transforms.Resize((224, 224)),

    transforms.RandomHorizontalFlip(),
    transforms.RandomRotation(10),
    transforms.ColorJitter(
        brightness=0.2,
        contrast=0.2
    ),

    transforms.ToTensor(),

    transforms.Normalize(
        mean=[0.485, 0.456, 0.406],
        std=[0.229, 0.224, 0.225]
    )
])

dataset = datasets.ImageFolder(
    data_path,
    transform=transform
)

print("Classes:", dataset.classes)
print("Number of images:", len(dataset))
from torch.utils.data import random_split

train_size = int(0.8 * len(dataset))
test_size = len(dataset) - train_size

generator = torch.Generator().manual_seed(42)

train_dataset, test_dataset = random_split(
    dataset,
    [train_size, test_size],
    generator=generator
)

print("Training images:", len(train_dataset))
print("Testing images:", len(test_dataset))
from torchvision import models
import torch.nn as nn

model = models.resnet18(weights="DEFAULT")

model.fc = nn.Linear(
    model.fc.in_features,
    3
)

print(model)
from torch.utils.data import DataLoader

train_loader = DataLoader(
    train_dataset,
    batch_size=4,
    shuffle=True
)

test_loader = DataLoader(
    test_dataset,
    batch_size=4,
    shuffle=False
)

print("DataLoaders created!")
# Loss function
criterion = nn.CrossEntropyLoss()

# Optimizer
optimizer = torch.optim.Adam(
    model.fc.parameters(),
    lr=0.001
)

print("Training setup ready!")
# Train the model
epochs = 5

for epoch in range(epochs):

    model.train()
    running_loss = 0.0

    for images, labels in train_loader:

        # Clear old gradients
        optimizer.zero_grad()

        # Make predictions
        outputs = model(images)

        # Calculate error
        loss = criterion(outputs, labels)

        # Learn from the error
        loss.backward()

        # Update the model
        optimizer.step()

        running_loss += loss.item()

    print(
        f"Epoch [{epoch + 1}/{epochs}], "
        f"Loss: {running_loss / len(train_loader):.4f}"
    )

print("Training completed!")
torch.save(model.state_dict(), "waste_model.pth")
# -----------------------------
# Test model accuracy
# -----------------------------

model.eval()

correct = 0
total = 0

with torch.no_grad():

    for images, labels in test_loader:

        outputs = model(images)

        _, predicted = torch.max(outputs, 1)

        total += labels.size(0)

        correct += (predicted == labels).sum().item()

accuracy = 100 * correct / total

print(f"Test Accuracy: {accuracy:.2f}%")
# -----------------------------
# Confusion Matrix
# -----------------------------

confusion_matrix = [
    [0, 0, 0],
    [0, 0, 0],
    [0, 0, 0]
]

model.eval()

with torch.no_grad():

    for images, labels in test_loader:

        outputs = model(images)

        _, predicted = torch.max(outputs, 1)

        for actual, prediction in zip(labels, predicted):

            confusion_matrix[actual.item()][prediction.item()] += 1

print("\nConfusion Matrix:")
print("                 Predicted")
print("              Organic Paper Plastic")

for i, row in enumerate(confusion_matrix):

    print(classes[i].capitalize(), row)
print("Model saved successfully!")