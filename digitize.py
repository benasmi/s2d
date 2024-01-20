import os
import uuid
import numpy as np
import matplotlib.pyplot as plt
import matplotlib.patches as patches
from PIL import Image
from scipy.spatial import distance

import box
from detection import inference
from keypoint import keypoint
from xmi import diagram_to_xmi
from ocr import ocr

debug_options = {
    'detection': True,
    'key_points': True,
    'post_kp': True,
}

plt.rcParams['figure.figsize'] = [12.0, 8.0]  # Adjust the values as needed


def get_closest_box(point, boxes, max_distance=None):
    if not boxes:
        return None

    closest_b, min_distance = min(
        ((b, distance.euclidean(point, b.center)) for b in boxes),
        key=lambda x: x[1]
    )

    if max_distance is not None and min_distance > max_distance:
        return None

    return closest_b


def gen_json(el):
    return {
        'id': el.id,
        'type': el.label,
        'name': el.text
    }


def get_or_create_element(diagram, el):
    items = list(filter(lambda x: x['id'] == el.id, diagram['elements']))
    return items[0] if len(items) > 0 else gen_json(el)


def digitize(path):
    # Read image
    script_dir = os.path.dirname(__file__)  # <-- absolute dir the script is in
    abs_file_path = os.path.join(script_dir, path)
    image = Image.open(abs_file_path)
    image = image.convert("RGB")
    img_for_plot = np.array(image)

    # Do inference
    detections, category_index = inference.inference(image, threshold={
        1: 0.6,  # actor
        2: 0.7,  # use_case
        3: 0.6,  # text
        4: 0.25  # association
    })

    # Map to box items
    boxes = box.BoundingBoxes(image, detections, category_index)

    # Plot inference
    if debug_options['detection']:
        visualise_boxes(image, boxes.boxes)

    '''
    Digitize text for 'text' and 'use_case' boxes.
    Sometimes 'text' or 'use_case' boxes are not digitized by OCR,
    thus additionally trying to digitize both boxes 
    highly increases chance of successful `use_case` name resolving 
    '''
    for b in boxes.filter_by('text', 'use_case'):
        pad = 3 if b.label == 'text' else None

        img_res = b.crop(image, padding=pad)
        b.text = ocr.image_to_string(img_res)
        if b.label == 'text':
            b.used = "extension points\n" in b.text

    # Attach text to elements
    # ---> Set name to use_case elements
    for uc_b in boxes.filter_by('use_case'):
        t_b = get_closest_box(uc_b.center, boxes.filter_by('text', used=False), max_distance=50)

        if t_b is not None:
            t_b.used = True
            if t_b.text.strip():
                uc_b.text = t_b.text

    # ---> Set actor names
    for act_b in boxes.filter_by('actor'):
        t_b = get_closest_box(act_b.center, boxes.filter_by('text', used=False), max_distance=80)

        if t_b is not None:
            t_b.used = True
            act_b.text = t_b.text

    # ---> Set dotted line names
    for t_b in boxes.filter_by('text', used=False):
        nt_b = get_closest_box(t_b.center, boxes.filter_by('association'), max_distance=120)

        if nt_b is None:
            continue

        t_b.used = True
        nt_b.text = nt_b.text + "<--->" + t_b.text if nt_b.text is not None else t_b.text

        if "ext" in nt_b.text.lower() or "inc" in nt_b.text.lower():
            nt_b.label = "dotted_line"

    # Calculate key points
    for assoc in boxes.filter_by('association', 'dotted_line'):
        assoc.key_points = keypoint.calculate_key_points(image, assoc.crop(image), assoc,
                                                         debug=debug_options['key_points'])

        if debug_options['key_points']:
            visualise_boxes(image, [assoc])

    visualise_boxes(image, boxes.boxes)

    # Connect association with elements
    diagram = {
        "name": "Generated UC Diagram",
        "elements": []
    }

    associations = boxes.filter_by('association', 'dotted_line')
    target_elements = boxes.filter_by('use_case', 'actor')

    for assoc in associations:
        start_kp_el = get_closest_box(assoc.key_points.start, target_elements)
        end_kp_el = get_closest_box(assoc.key_points.end, target_elements)

        start_kp_el_json = get_or_create_element(diagram, start_kp_el)
        end_kp_el_json = get_or_create_element(diagram, end_kp_el)

        if assoc.label == 'dotted_line' and "inc" in assoc.text.lower():
            if 'include' not in start_kp_el_json:
                start_kp_el_json['include'] = []
            start_kp_el_json['include'].append({
                'type': 'include',
                'ref': end_kp_el.id
            })
        elif assoc.label == 'dotted_line' and "ext" in assoc.text.lower():
            extensions = list(filter(lambda x: "ext" not in x, assoc.text.lower().split("<--->")))
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

    existing_ids = list(map(lambda x: x['id'], diagram['elements']))
    for target_el in boxes.filter_by('use_case', 'actor'):
        if target_el.id not in existing_ids:
            diagram['elements'].append(gen_json(target_el))
    # Convert to XMI
    xmi = diagram_to_xmi.convert_to_xmi(diagram)

    return xmi, img_for_plot


def visualise_boxes(image, boxes):
    fig, ax = plt.subplots()
    ax.imshow(image)

    class_color = {
        'text': '#27ae60',
        'association': '#9b59b6',
        'dotted_line': '#9b59b6',
        'use_case': '#3498db',
        'actor': '#2c3e50'
    }
    for b in boxes:
        c = class_color[b.label]
        x, y = b.left_top

        rect = patches.Rectangle((x, y), b.width, b.height, linewidth=2, edgecolor=c, facecolor='none')
        ax.add_patch(rect)
        ax.text(x, y + 2, b.label + ' ' + str(int(b.score * 100)) + '%', color=c, verticalalignment='top', size=8,
                weight='bold')

        if b.key_points is not None:
            ax.scatter(b.key_points.start[0], b.key_points.start[1], c="red", s=20)
            ax.scatter(b.key_points.end[0], b.key_points.end[1], c="orange", s=20)

    plt.show()


digitize("detection/data/images/PA7.png")
