from PIL import Image
import pytesseract
import cv2
import numpy as np
import matplotlib.pyplot as plt

def img_path_to_string(path):
    return pytesseract.image_to_string(Image.open(path))


def image_to_string(image):
    gray = cv2.cvtColor(np.array(image), cv2.COLOR_BGR2GRAY)
    text = pytesseract.image_to_string(gray).strip()

    return text