import os
import json
import matplotlib.pyplot as plt
from PIL import Image
from scipy.spatial import distance
from box import BoundingBox
from detection import inference
from keypoint import keypoint
from xmi import diagram_to_xmi
from ocr import ocr

debug = False


def crop_box_from_image(box, image):
    lt_coords = box.coordinates[0]
    br_coords = box.coordinates[3]

    return image.crop((lt_coords[0], lt_coords[1], br_coords[0], br_coords[1]))


def get_closest_box_to_point(point, boxes):
    closest_b = None
    min_distance = float('inf')

    for b in boxes:
        euc_distance = distance.euclidean(point, b.coordinates[4])
        if euc_distance < min_distance:
            min_distance = euc_distance
            closest_b = b

    return closest_b


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

for uc_b in use_case_boxes:
    t_b = get_closest_box_to_point(
        uc_b.coordinates[4],
        list(filter(lambda x: x.label == 'text' and not x.used, boxes))
    )

    t_b.used = True
    uc_b.text = t_b.text

# ---> Set dotted_line type and extension + actor names
text_boxes = list(filter(lambda x: x.label == 'text' and x.used == False, boxes))
non_text_boxes = list(filter(lambda x: (x.label == 'dotted_line' or x.label == 'actor') and x.text is None, boxes))

for t_b in text_boxes:
    nt_b = get_closest_box_to_point(t_b.coordinates[4], non_text_boxes)

    t_b.used = True
    if nt_b.text is None:
        nt_b.text = t_b.text
    else:
        nt_b.text = nt_b.text + "<--->" + t_b.text

# Calculate key points
associations = list(
    filter(lambda x: x.label == 'generalization' or x.label == 'dotted_line' or x.label == 'line', boxes))

for assoc in associations:
    assoc_image = crop_box_from_image(assoc, image)
    assoc.key_points = keypoint.calculate_key_points(assoc_image, assoc)


# Connect association with elements
def gen_el_json(el):
    return {
        'id': el.id,
        'type': el.label,
        'name': el.text
    }


diagram = {
    "name": "Generated UC Diagram",
    "elements": []
}

associations = list(
    filter(lambda x: x.label == 'generalization' or x.label == 'dotted_line' or x.label == 'line', boxes))
target_elements = list(
    filter(lambda x: x.label == 'use_case' or x.label == 'actor', boxes))

for assoc in associations:
    start_kp = assoc.key_points.start
    end_kp = assoc.key_points.end

    start_kp_el = get_closest_box_to_point(start_kp, target_elements)
    end_kp_el = get_closest_box_to_point(end_kp, target_elements)

    start_kp_el_json = gen_el_json(start_kp_el)
    end_kp_el_json = gen_el_json(end_kp_el)

    if assoc.label == 'dotted_line' and "include" in assoc.text:
        start_kp_el_json['include'] = {
            'type': 'include',
            'ref': end_kp_el.id
        }
    elif assoc.label == 'dotted_line' and "extend" in assoc.text:
        print("implement")
    elif assoc.label == 'generalization':
        print("implement")

    diagram['elements'].append(start_kp_el_json)
    diagram['elements'].append(end_kp_el_json)

if debug:
    diagram_json = json.dumps(diagram)
    print("Diagram json", diagram_json)

# Convert to XMI
xmi = diagram_to_xmi.convert_to_xmi(diagram)

if debug:
    print("Xmi", xmi)
    plt.show()
