import os
from detection import inference
from PIL import Image

import matplotlib.pyplot as plt
class DetectionBox:
    def __init__(self, coordinates, label, score):
        ymin, xmin, ymax, xmax = coordinates[0:4]
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
boxes = collect_boxes(detections, category_index)

# Digitize text for 'text' boxes
width, height = image.size
print(width, height)
img_res = image.crop((398, 110, 539, 142))
img_res.show()

'''
0 = {tuple: 2} (0.40301743, 0.37154207)
1 = {tuple: 2} (0.40301743, 0.51299286)
2 = {tuple: 2} (0.5440891, 0.37154207)
3 = {tuple: 2} (0.5440891, 0.51299286)
'''
plt.show()
