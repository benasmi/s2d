import os

import matplotlib.pyplot as plt
from PIL import Image
from scipy.spatial import distance
from box import BoundingBox
from detection import inference
from keypoint import keypoint
from ocr import ocr


def crop_box_from_image(box, image):
    lt_coords = box.coordinates[0]
    br_coords = box.coordinates[3]

    return image.crop((lt_coords[0], lt_coords[1], br_coords[0], br_coords[1]))


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
boxes = []
for i in range(len(detections['detection_scores'])):
    box = BoundingBox(
        image,
        detections['detection_boxes'][i],
        category_index[detections['detection_classes'][i]]['name'],
        detections['detection_scores'][i]
    )
    boxes.append(box)

# Digitize text for 'text' boxes
for b in boxes:
    if b.label == 'text':
        img_res = crop_box_from_image(b, image)
        b.text = ocr.image_to_string(img_res)

# Attach text to elements

# ---> Set name to use_case elements
use_case_boxes = list(filter(lambda x: x.label == 'use_case', boxes))
text_boxes = list(filter(lambda x: x.label == 'text' and x.used == False, boxes))

for uc_b in use_case_boxes:
    target_t_b = None
    min_distance = float('inf')
    for t_b in text_boxes:
        if t_b.used is True:
            continue
        euc_distance = distance.euclidean(uc_b.coordinates[4], t_b.coordinates[4])
        if euc_distance < min_distance:
            min_distance = euc_distance
            target_t_b = t_b
    target_t_b.used = True
    uc_b.text = target_t_b.text

# ---> Set dotted_line type and extension + actor names
text_boxes = list(filter(lambda x: x.label == 'text' and x.used == False, boxes))
non_text_boxes = list(filter(lambda x: (x.label == 'dotted_line' or x.label == 'actor') and x.text is None, boxes))

for t_b in text_boxes:
    target_nt_b = None
    min_distance = float('inf')
    for nt_b in non_text_boxes:
        euc_distance = distance.euclidean(t_b.coordinates[4], nt_b.coordinates[4])
        if euc_distance < min_distance:
            min_distance = euc_distance
            target_nt_b = nt_b

    t_b.used = True
    if target_nt_b.text is None:
        target_nt_b.text = t_b.text
    else:
        target_nt_b.text = target_nt_b.text + "<--->" + t_b.text

# Calculate key points
associations = list(
    filter(lambda x: x.label == 'generalization' or x.label == 'dotted_line' or x.label == 'line', boxes))

for assoc in associations:
    assoc_image = crop_box_from_image(assoc, image)
    assoc.key_points = keypoint.calculate_key_points(assoc_image, assoc)

plt.show()
