import cv2
import easyocr
import numpy as np
import pytesseract
from PIL import Image

easyocr_reader = easyocr.Reader(['en'])

def ocr(image):
    if isinstance(image, str):
        image = Image.open(image)

    np_img = np.array(image)
    scale_factor = 1.5
    upscaled_image = cv2.resize(np_img, None, fx=scale_factor, fy=scale_factor,
                                interpolation=cv2.INTER_LINEAR)

    images = [
        lambda: image,
        lambda: upscaled_image,
        lambda: cv2.cvtColor(upscaled_image, cv2.COLOR_BGR2GRAY),
        lambda: cv2.cvtColor(np_img, cv2.COLOR_BGR2GRAY)
    ]

    return perform_ocr(images, tesseract_ocr)


def perform_ocr(images, ocr_fn):
    for img in images:
        text = ocr_fn(img())
        if text.strip():
            return text
    return ''


def easy_ocr(img):
    result = easyocr_reader.readtext(img)
    collected_text = [element[1] for element in result]
    return ' '.join(collected_text)


def tesseract_ocr(img):
    return pytesseract.image_to_string(img).strip()

