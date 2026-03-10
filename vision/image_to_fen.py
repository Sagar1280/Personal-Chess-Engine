import numpy as np
import cv2
from .predict import predict_fen


def detect_board(image_bytes):

    # convert bytes → numpy image
    nparr = np.frombuffer(image_bytes, np.uint8)
    img = cv2.imdecode(nparr, cv2.IMREAD_COLOR)

    img = cv2.cvtColor(img, cv2.COLOR_BGR2RGB) 

    fen = predict_fen(img)

    return fen