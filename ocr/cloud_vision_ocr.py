import hashlib
import pickle
from google.cloud import vision
from io import BytesIO
import os

client = vision.ImageAnnotatorClient()
ignored_segments = ['ㅈ']

def ocr(image, acceptable_confidence=0.45):
    img_hash = image_to_md5(image)
    root_dir = os.path.dirname(os.path.abspath(__file__))
    cache_dir = os.path.join(root_dir, ".cache")
    cache_path = os.path.join(cache_dir, str(img_hash) + ".pkl")

    response = None
    if os.path.exists(cache_path):
        with open(cache_path, 'rb') as file:
            response = pickle.load(file)

    if response is None:
        image_bytes = BytesIO()
        image.save(image_bytes, format='JPEG')
        image = vision.Image(content=image_bytes.getvalue())
        response = client.document_text_detection(image=image)

        with open(cache_path, 'wb') as file:
            pickle.dump(response, file)

    if response.error.message:
        raise Exception(
            "{}\nFor more info on error messages, check: "
            "https://cloud.google.com/apis/design/errors".format(response.error.message)
        )
    blocks = [result for page in response.full_text_annotation.pages for result in process_page(page)]
    return filter(lambda block: block['confidence'] >= acceptable_confidence, blocks)

def get_word_text(word):
    return "".join([symbol.text for symbol in word.symbols])


def process_paragraph(paragraph):
    return [get_word_text(word) for word in paragraph.words]


def process_block(block):
    segments = [segment for paragraph in block.paragraphs for segment in process_paragraph(paragraph)]
    segments = list(filter(lambda segment: segment not in ignored_segments, segments))
    return {
        'confidence': block.confidence,
        'bounding_box': block.bounding_box.vertices,
        'segments': segments,
        'text': " ".join(segments)
    }


def process_page(page):
    return [block_response for block in page.blocks for block_response in [process_block(block)]]


def image_to_md5(image):
    md5 = hashlib.md5()
    md5.update(image.tobytes())
    return md5.hexdigest()
