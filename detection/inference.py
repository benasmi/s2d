import os
import numpy as np
import matplotlib.pyplot as plt
import warnings
import json
import requests
from object_detection.utils import label_map_util
from object_detection.utils import visualization_utils as viz_utils

import matplotlib

matplotlib.use('TkAgg')

absolute_path = os.path.dirname(__file__)


def inference(image, min_thresh):
    label_path = os.path.join(absolute_path, os.path.join("label_map.pbtxt"))
    warnings.filterwarnings('ignore')  # Suppress Matplotlib warnings
    category_index = label_map_util.create_category_index_from_labelmap(label_path, use_display_name=True)

    image_np = np.array(image)

    detections = detect_fn(image_np)

    detections['detection_classes'] = np.array(detections["detection_classes"]).astype(np.int64)
    indices = list(filter(lambda idx: detections['detection_scores'][idx] >= min_thresh,
                          range(int(detections['num_detections']))))

    for (key, value) in detections.items():
        if key != 'num_detections':
            detections[key] = np.take(detections[key], indices, 0)

    return image_np.copy(), detections, category_index


def detect_fn(img):
    img = np.expand_dims(img, 0)

    data = json.dumps({"signature_name": "serving_default", "instances": img.tolist()})
    headers = {"content-type": "application/json"}
    response = requests.post('http://localhost:8501/v1/models/s2d:predict', data=data, headers=headers)
    if response.status_code != 200:
        print('Error:', response.status_code, response.text)

    result = json.loads(response.text)
    return result['predictions'][0]


def plot_inference(img_numpy, detections, category_index):
    viz_utils.visualize_boxes_and_labels_on_image_array(
        img_numpy,
        detections['detection_boxes'],
        detections['detection_classes'],
        detections['detection_scores'],
        category_index,
        use_normalized_coordinates=True,
        max_boxes_to_draw=200,
        agnostic_mode=False)

    plt.figure()
    plt.imshow(img_numpy)
    print('Done')
    print('Plotting')
    plt.show(block=False)
    return img_numpy
