from PIL import Image
import pytesseract

def img_path_to_string(path):
    return pytesseract.image_to_string(Image.open(path))


def image_to_string(image):
    return pytesseract.image_to_string(image).strip()