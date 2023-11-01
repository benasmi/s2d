import os
import json
import uuid
import matplotlib.pyplot as plt
from PIL import Image
from scipy.spatial import distance
from box import BoundingBox
from detection import inference
from keypoint import keypoint
from xmi import diagram_to_xmi
from ocr import ocr

debug = True


def get_closest_box_to_point(point, boxes):
    if not boxes:
        return None, float('inf')

    closest_b, min_distance = min(
        ((b, distance.euclidean(point, b.center)) for b in boxes),
        key=lambda x: x[1]
    )
    return closest_b, min_distance


# Read image
script_dir = os.path.dirname(__file__)  # <-- absolute dir the script is in
rel_path = "detection\data\images\PA24.png"
abs_file_path = os.path.join(script_dir, rel_path)
image = Image.open(abs_file_path)
image = image.convert("RGB")

# Do inference
print('Running inference for {}... '.format(abs_file_path), end='')
img_for_plot, detections, category_index = inference.inference(image, min_thresh=.5)

# Plot inference
inference.plot_inference(img_for_plot, detections)

# Map to box items

boxes = [
    BoundingBox(image, b, category_index[detection_class]['name'], score)
    for b, detection_class, score in zip(
        detections['detection_boxes'],
        detections['detection_classes'],
        detections['detection_scores']
    )
]

# Digitize text for 'text' boxes
for b in boxes:
    if b.label == 'text':
        img_res = b.crop(image)
        b.text = ocr.image_to_string(img_res)

        if "extension points\n" in b.text:
            b.used = True

# Attach text to elements

# ---> Set name to use_case elements
use_case_boxes = list(filter(lambda x: x.label == 'use_case', boxes))

for uc_b in use_case_boxes:
    t_b, t_b_distance = get_closest_box_to_point(
        uc_b.center,
        list(filter(lambda x: x.label == 'text' and not x.used, boxes))
    )

    t_b.used = True
    uc_b.text = t_b.text

# ---> Set actor names
actor_boxes = list(filter(lambda x: (x.label == 'actor') and x.text is None, boxes))

for act_b in actor_boxes:
    t_b, t_b_distance = get_closest_box_to_point(
        act_b.center,
        list(filter(lambda x: x.label == 'text' and not x.used, boxes))
    )

    if t_b_distance > 80:
        continue

    t_b.used = True
    act_b.text = t_b.text

# ---> Set dotted line names
text_boxes = list(filter(lambda x: x.label == 'text' and not x.used, boxes))
dotted_line_boxes = list(filter(lambda x: x.label == 'dotted_line', boxes))

for t_b in text_boxes:
    nt_b, nt_b_distance = get_closest_box_to_point(t_b.center, dotted_line_boxes)

    t_b.used = True
    if nt_b.text is None:
        nt_b.text = t_b.text
    else:
        nt_b.text = nt_b.text + "<--->" + t_b.text

# Calculate key points
associations = list(
    filter(lambda x: x.label == 'generalization' or x.label == 'dotted_line' or x.label == 'line', boxes))

for assoc in associations:
    assoc_image = assoc.crop(image)
    assoc.key_points = keypoint.calculate_key_points(assoc_image, assoc)


# Connect association with elements
def gen_json(el):
    return {
        'id': el.id,
        'type': 'association' if el.label == 'line' else el.label,
        'name': el.text
    }


def get_or_create_element(diagram, el):
    items = list(filter(lambda x: x['id'] == el.id, diagram['elements']))
    return items[0] if len(items) > 0 else gen_json(el)


diagram = {
    "name": "Generated UC Diagram",
    "elements": []
}

associations = list(
    filter(lambda x: x.label == 'generalization' or x.label == 'dotted_line' or x.label == 'line', boxes))
target_elements = list(
    filter(lambda x: x.label == 'use_case' or x.label == 'actor', boxes))

for assoc in associations:
    start_kp_el, start_dist = get_closest_box_to_point(assoc.key_points.start, target_elements)
    end_kp_el, end_dist = get_closest_box_to_point(assoc.key_points.end, target_elements)

    start_kp_el_json = get_or_create_element(diagram, start_kp_el)
    end_kp_el_json = get_or_create_element(diagram, end_kp_el)

    if assoc.label == 'dotted_line' and "include" in assoc.text:
        start_kp_el_json['include'] = {
            'type': 'include',
            'ref': end_kp_el.id
        }
    elif assoc.label == 'dotted_line' and "extend" in assoc.text:
        extensions = list(filter(lambda x: "extend" not in x, assoc.text.split("<--->")))
        extension = extensions[0] if len(extensions) >= 1 else "Default_extension"

        extend_id = uuid.uuid4().hex
        extension_id = uuid.uuid4().hex

        start_kp_el_json['extend_to'] = {
            "type": 'extend',
            "ref": end_kp_el.id,
            "extend_id": extend_id,
            "extension_id": extension_id,
        }

        end_kp_el_json['extend_from'] = {
            "type": "extension_point",
            "extend_id": extend_id,
            "extension_id": extension_id,
            "name": extension
        }
    elif assoc.label == 'generalization':
        end_kp_el_json['generalization'] = {
            "type": "generalization",
            "ref": start_kp_el.id
        }
    else:
        assoc_el_json = gen_json(assoc)
        assoc_el_json['start'] = start_kp_el.id
        assoc_el_json['end'] = end_kp_el.id
        diagram['elements'].append(assoc_el_json)

    existing_ids = list(map(lambda x: x['id'], diagram['elements']))
    if start_kp_el.id not in existing_ids:
        diagram['elements'].append(start_kp_el_json)

    if end_kp_el.id not in existing_ids:
        diagram['elements'].append(end_kp_el_json)

    diagram['elements'] = [el if el['id'] is not start_kp_el.id else start_kp_el_json for el in diagram['elements']]
    diagram['elements'] = [el if el['id'] is not end_kp_el.id else end_kp_el_json for el in diagram['elements']]

diagram_json = json.dumps(diagram)
print("Diagram json", diagram_json)

# Convert to XMI
xmi = diagram_to_xmi.convert_to_xmi(diagram)

if debug:
    print("Xmi", xmi)
    plt.show()
