import os

import matplotlib.pyplot as plt

from detection import inference


def collect_boxes(detections, categories):
    boxes = []
    for i in range(len(detections['detection_scores'])):
        box = DetectionBox(
            detections['detection_boxes'][i],
            categories[detections['detection_classes'][i]]['name'],
            detections['detection_scores'][i]
        )
        boxes.append(box)
    return boxes


class DetectionBox:
    def __init__(self, coordinates, label, score):
        ymin, xmin, ymax, xmax = coordinates[0], coordinates[1], coordinates[2], coordinates[3]
        self.coordinates = [
            (xmin, ymin),
            (xmin, ymax),
            (xmax, ymin),
            (xmax, ymax),
            ((xmax + xmin) / 2, (ymax + ymin) / 2)
        ]

        self.label = label
        self.score = score
        self.used = False
        self.text = None


# Read image
script_dir = os.path.dirname(__file__)  # <-- absolute dir the script is in
rel_path = "detection\data\images\PA12.png"
abs_file_path = os.path.join(script_dir, rel_path)

# Do inference
img, detections, category_index = inference.inference(abs_file_path, min_thresh=.2)

# Plot inference
inference.plot_inference(img, detections)

# Map to box items
boxes = collect_boxes(detections, category_index)
print(boxes)

plt.show()
