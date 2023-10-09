import os
from detection import inference
from ocr import ocr
from PIL import Image

import matplotlib.pyplot as plt
class DetectionBox:
    def __init__(self, image, coordinates, label, score):
        width, height = image.size
        ymin, xmin, ymax, xmax = coordinates[0:4]

        self.normalized_coordinates = [
            (xmin, ymin),
            (xmin, ymax),
            (xmax, ymin),
            (xmax, ymax),
            ((xmax + xmin) / 2, (ymax + ymin) / 2)
        ]

        self.coordinates = [
            (xmin * width, ymin * height),
            (xmin * width, ymax * height),
            (xmax * width, ymin * height),
            (xmax * width, ymax * height),
            ((xmax * width + xmin * width ) / 2, (ymax * height + ymin * height) / 2)
        ]
        self.label = label
        self.score = score
        self.used = False
        self.text = None


def collect_boxes(image, detections, categories):
    boxes = []
    for i in range(len(detections['detection_scores'])):
        box = DetectionBox(
            image,
            detections['detection_boxes'][i],
            categories[detections['detection_classes'][i]]['name'],
            detections['detection_scores'][i]
        )
        boxes.append(box)
    return boxes


# Read image
script_dir = os.path.dirname(__file__)  # <-- absolute dir the script is in
rel_path = "detection\data\images\PA12.png"
abs_file_path = os.path.join(script_dir, rel_path)
image = Image.open(abs_file_path)
image = image.convert("RGB")

# Do inference
print('Running inference for {}... '.format(abs_file_path), end='')
img_for_plot, detections, category_index = inference.inference(image, min_thresh=.2)

# Plot inference
inference.plot_inference(img_for_plot, detections)

# Map to box items
boxes = collect_boxes(image, detections, category_index)

# Digitize text for 'text' boxes
width, height = image.size
print(width, height)
for b in boxes:
    if b.label == 'text':
        lt_coords = b.coordinates[0]
        br_coords = b.coordinates[3]

        img_res = image.crop((lt_coords[0], lt_coords[1], br_coords[0], br_coords[1]))
        img_res.show()
        print(ocr.image_to_string(img_res))

plt.show()
