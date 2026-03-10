import torch
import torch.nn as nn
from torchvision import models
import torchvision.transforms as transforms
from PIL import Image
import numpy as np

device = torch.device("cuda" if torch.cuda.is_available() else "cpu")

model = models.resnet18(weights=None)
model.fc = nn.Linear(model.fc.in_features, 13)
model.load_state_dict(torch.load("vision/chess_piece_model.pth", map_location=device))
model = model.to(device)
model.eval()

transform = transforms.Compose([
    transforms.Resize((64,64)),
    transforms.ToTensor()
])

classes = [
'b','k','n','p','q','r',
'empty',
'B','K','N','P','Q','R'
]


def predict_fen(img):

    h, w, _ = img.shape
    square_h = h // 8
    square_w = w // 8

    fen_rows = []

    for r in range(8):

        fen_row = ""
        empty_count = 0

        for c in range(8):

            square = img[
                r*square_h:(r+1)*square_h,
                c*square_w:(c+1)*square_w
            ]

            square = Image.fromarray(square)
            
            tensor = transform(square)          # convert to tensor
            tensor = tensor.unsqueeze(0).to(device)

            with torch.no_grad():
                output = model(tensor)
                pred = int(torch.argmax(output,dim=1).item())

            piece = classes[pred]

            if piece == "empty":
                empty_count += 1
            else:

                if empty_count > 0:
                    fen_row += str(empty_count)
                    empty_count = 0

                fen_row += piece

        if empty_count > 0:
            fen_row += str(empty_count)

        fen_rows.append(fen_row)

    fen = "/".join(fen_rows) + " w KQkq - 0 1"
    
    return fen