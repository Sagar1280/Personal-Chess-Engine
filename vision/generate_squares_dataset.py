import os
import cv2

input_folder = "Dataset/train"
output_folder = "SquareDataset"

os.makedirs(output_folder, exist_ok=True)

def filename_to_fen(filename):
    name = filename.split(".")[0]
    return name.replace("-", "/")

def fen_to_labels(fen):

    labels = []

    for row in fen.split("/"):
        for c in row:

            if c.isdigit():
                labels.extend(["empty"] * int(c))
            else:
                labels.append(c)

    return labels


def split_board(img):

    h, w = img.shape[:2]

    square_h = h // 8
    square_w = w // 8

    squares = []

    for r in range(8):
        for c in range(8):

            y1 = r * square_h
            y2 = (r+1) * square_h

            x1 = c * square_w
            x2 = (c+1) * square_w

            square = img[y1:y2, x1:x2]

            squares.append(square)

    return squares


count = 0

for file in os.listdir(input_folder):

    path = os.path.join(input_folder, file)

    img = cv2.imread(path)

    fen = filename_to_fen(file)

    labels = fen_to_labels(fen)

    squares = split_board(img)

    for i in range(64):

        label = labels[i]

        label_dir = os.path.join(output_folder, label)

        os.makedirs(label_dir, exist_ok=True)

        cv2.imwrite(
            os.path.join(label_dir, f"{count}_{i}.png"),
            squares[i]
        )

    count += 1

print("Dataset generation complete")