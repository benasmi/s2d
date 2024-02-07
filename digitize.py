import os
import uuid
import io
import matplotlib.pyplot as plt
import matplotlib.patches as patches
from PIL import Image
from scipy.spatial import distance
import box
from detection import inference
from keypoint import keypoint
from xmi import diagram_to_xmi
from ocr import cloud_vision_ocr
import matplotlib

matplotlib.use('TkAgg')

cloud_vision_enabled = True
debug_options = {
    'detection': True,
    'key_points': False,
    'post_kp': False,
}

plt.rcParams['figure.figsize'] = [12.0, 8.0]  # Adjust the values as needed


def get_closest_box(point, boxes, max_distance=None):
    if not boxes:
        return None, -1

    closest_b, min_distance = min(
        ((b, distance.euclidean(point, b.center)) for b in boxes),
        key=lambda x: x[1]
    )

    if max_distance is not None and min_distance > max_distance:
        return None, -1

    return closest_b, min_distance


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
    detections, category_index = inference.inference(image, threshold={
        1: 0.45,  # actor
        2: 0.70,  # use_case
        3: 0.60,  # text
        4: 0.20,  # association
        5: 0.20  # generalization
    }, ignored_classes=['text'])

    # Map to box items
    boxes = box.BoundingBoxes(image, detections, category_index)

    # Text blocks with Google Cloud vision
    text_blocks = cloud_vision_ocr.ocr(image)
    for text_block in text_blocks:
        boxes.add_box(image, text_block)

    # Plot inference
    if debug_options['detection']:
        visualise_boxes(image, boxes.boxes, "Initial inference")

    # Attach text to elements
    # ---> Set name to use_case elements
    for uc_b in boxes.filter_by('use_case'):
        t_b, _ = get_closest_box(uc_b.center, boxes.filter_by('text', used=False), max_distance=50)

        if t_b is not None:
            t_b.used = True
            if t_b.text.strip():
                uc_b.text = t_b.text

    # ---> Set actor names
    for act_b in boxes.filter_by('actor'):
        t_b, _ = get_closest_box(act_b.center_bottom, boxes.filter_by('text', used=False), max_distance=80)

        if t_b is not None:
            t_b.used = True
            act_b.text = t_b.text

    # ---> Set dotted line names
    for t_b in boxes.filter_by('text', used=False):
        nt_b, dist = get_closest_box(t_b.center, boxes.filter_by('association'), max_distance=120)

        if nt_b is None:
            continue

        # If no text is found but it's on association center (must be include or extend)
        if dist < 30 and t_b.text == '':
            t_b.text = '<<include>>'

        # If text starts with `<`, but ocr didn't parse it correctly
        if "<" in t_b.text.lower() and "ext" not in t_b.text.lower() and "inc" not in t_b.text.lower():
            t_b.text = '<<include>>'

        t_b.used = True
        nt_b.text = nt_b.text + "<--->" + t_b.text if nt_b.text is not None else t_b.text

        if "ext" in nt_b.text.lower() or "inc" in nt_b.text.lower():
            nt_b.label = "dotted_line"
            continue

    # Calculate key points
    for assoc in boxes.filter_by('association', 'dotted_line', 'generalization'):
        assoc.key_points = keypoint.calculate_key_points(image, assoc.crop(image), assoc,
                                                         debug=debug_options['key_points'])

        if debug_options['key_points']:
            visualise_boxes(image, [assoc], "Individual keypoint")

    boxes = remove_duplicate_associations(boxes)
    inference_plot = visualise_boxes(image, boxes.boxes, "Final inference")

    # Connect associations
    diagram = connect_associations(boxes)

    # Convert to XMI
    xmi = diagram_to_xmi.convert_to_xmi(diagram)

    return xmi, inference_plot


def remove_duplicate_associations(boxes):
    associations = boxes.filter_by('association', 'dotted_line', 'generalization')
    target_elements = boxes.filter_by('use_case', 'actor')

    removable_associations = []
    connections = {}
    for assoc in associations:
        start_kp_el, _ = get_closest_box(assoc.key_points.start, target_elements)
        end_kp_el, _ = get_closest_box(assoc.key_points.end, target_elements)
        connection_id = hash(start_kp_el.id) + hash(end_kp_el.id)
        current_association = connections.get(connection_id, None)
        if current_association is None:
            connections[connection_id] = assoc
        else:
            if boost_assoc_score(current_association, start_kp_el, end_kp_el) \
                    < boost_assoc_score(assoc, start_kp_el, end_kp_el):
                connections[connection_id] = assoc
                removable_associations.append(current_association.id)
            else:
                removable_associations.append(assoc.id)
    return boxes.remove_by_ids(removable_associations)


def boost_assoc_score(assoc, start_el, end_el):
    return assoc.score + 50 if start_el.label == end_el.label and assoc.label == 'generalization' else assoc.score


def connect_associations(boxes):
    # Connect association with elements
    diagram = {
        "name": "Generated UC Diagram",
        "elements": []
    }

    associations = boxes.filter_by('association', 'dotted_line', 'generalization')
    target_elements = boxes.filter_by('use_case', 'actor')

    for assoc in associations:
        start_kp_el, _ = get_closest_box(assoc.key_points.start, target_elements)
        end_kp_el, _ = get_closest_box(assoc.key_points.end, target_elements)

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

    return diagram


def visualise_boxes(image, boxes, title):
    fig, ax = plt.subplots()
    ax.imshow(image)

    class_color = {
        'text': '#27ae60',
        'association': '#9b59b6',
        'dotted_line': '#9b59b6',
        'use_case': '#3498db',
        'actor': '#2c3e50',
        'generalization': '#f1c40f'
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

    plt.title(title)
    plt.show()

    buffer = io.BytesIO()
    ax.figure.canvas.print_png(buffer)
    buffer.seek(0)  # Move the cursor to the beginning of the buffer

    return Image.open(buffer)


digitize("detection\demonstration\\demo13.png")
