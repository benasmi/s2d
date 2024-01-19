import os
import uuid

import matplotlib.pyplot as plt
import matplotlib.patches as patches
from PIL import Image
from scipy.spatial import distance

import box
from detection import inference
from keypoint import keypoint
from xmi import diagram_to_xmi
from ocr import ocr

debug = True


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

    # Do inference
    img_for_plot, detections, category_index = inference.inference(image, min_thresh=.5)

    # Map to box items
    boxes = box.BoundingBoxes(image, detections, category_index)

    # Plot inference
    visualise_boxes(image, boxes)

    # Digitize text for 'text' boxes
    for b in boxes.filter_by('text', 'use_case'):
        pad = 4 if b.label == 'text' else None
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
            uc_b.text = t_b.text

    # ---> Set actor names
    for act_b in boxes.filter_by('actor'):
        t_b = get_closest_box(act_b.center, boxes.filter_by('text', used=False), max_distance=80)

        if t_b is not None:
            t_b.used = True
            act_b.text = t_b.text

    # ---> Set dotted line names
    for t_b in boxes.filter_by('text', used=False):
        nt_b = get_closest_box(t_b.center, boxes.filter_by('association'), max_distance=70)

        if nt_b is None:
            continue

        t_b.used = True
        nt_b.text = nt_b.text + "<--->" + t_b.text if nt_b.text is not None else t_b.text

        if "extend" in nt_b.text or "include" in nt_b.text:
            nt_b.label = "dotted_line"
            print(nt_b.label)

    # Calculate key points
    for assoc in boxes.filter_by('association', 'dotted_line'):
        assoc.key_points = keypoint.calculate_key_points(assoc.crop(image), assoc)

    visualise_boxes(image, boxes)

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
    for b in boxes.boxes:
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


digitize("./detection/data/images/PA (22).png")