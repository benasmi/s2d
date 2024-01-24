from google.cloud import vision
from io import BytesIO

client = vision.ImageAnnotatorClient()
acceptable_confidence = 65

def ocr(image):
    image_bytes = BytesIO()
    image.save(image_bytes, format='JPEG')

    image = vision.Image(content=image_bytes.getvalue())
    response = client.document_text_detection(image=image)

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
    return {
        'confidence': block.confidence,
        'bounding_box': block.bounding_box.vertices,
        'segments': segments,
        'text': " ".join(segments)
    }


def process_page(page):
    return [block_response for block in page.blocks for block_response in [process_block(block)]]
