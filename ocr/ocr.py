from PIL import Image

import pytesseract

pytesseract.pytesseract.tesseract_cmd = r'tesseract/tesseract.exe'


def image_to_string(path):
    return pytesseract.image_to_string(Image.open(path))


print(image_to_string("data/img4.JPG"))
