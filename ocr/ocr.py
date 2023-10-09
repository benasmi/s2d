from PIL import Image
import os
import pytesseract

absolute_path = os.path.dirname(__file__)
tes_path = os.path.join(absolute_path, "tesseract\\tesseract.exe")

pytesseract.pytesseract.tesseract_cmd = tes_path


def img_path_to_string(path):
    return pytesseract.image_to_string(Image.open(path))


def image_to_string(image):
    return pytesseract.image_to_string(image)
