import torch
import torch.nn as nn
import torch.optim as optim
from torch.utils.data import DataLoader
from torchvision import datasets, transforms, models
# -----------------------------
# Settings
# -----------------------------

DATASET_PATH = "vision/SquareDataset"
MODEL_SAVE_PATH = "vision/chess_piece_model.pth"

BATCH_SIZE = 64
EPOCHS = 10
LEARNING_RATE = 0.0001

device = torch.device("cuda" if torch.cuda.is_available() else "cpu")

# -----------------------------
# Image preprocessing
# -----------------------------

transform = transforms.Compose([
    transforms.Resize((224, 224)),   # required for ResNet
    transforms.ToTensor()
])

# -----------------------------
# Load dataset
# -----------------------------

dataset = datasets.ImageFolder(DATASET_PATH, transform=transform)

train_loader = DataLoader(
    dataset,
    batch_size=BATCH_SIZE,
    shuffle=True,
    num_workers=4
)

num_classes = len(dataset.classes)

print("Classes:", dataset.classes)
print("Total samples:", len(dataset))

# -----------------------------
# Model (ResNet18)
# -----------------------------

model = models.resnet18(pretrained=True)

# replace final layer
model.fc = nn.Linear(model.fc.in_features, num_classes)

model = model.to(device)

# -----------------------------
# Loss + Optimizer
# -----------------------------

criterion = nn.CrossEntropyLoss()
optimizer = optim.Adam(model.parameters(), lr=LEARNING_RATE)

# -----------------------------
# Training Loop
# -----------------------------

for epoch in range(EPOCHS):

    model.train()

    running_loss = 0

    for images, labels in train_loader:

        images = images.to(device)
        labels = labels.to(device)

        optimizer.zero_grad()

        outputs = model(images)

        loss = criterion(outputs, labels)

        loss.backward()

        optimizer.step()

        running_loss += loss.item()

    avg_loss = running_loss / len(train_loader)

    print(f"Epoch {epoch+1}/{EPOCHS}  Loss: {avg_loss:.4f}")

# -----------------------------
# Save model
# -----------------------------

torch.save(model.state_dict(), MODEL_SAVE_PATH)

print("Model saved to:", MODEL_SAVE_PATH)