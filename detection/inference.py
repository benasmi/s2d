import numpy as np
import json
import requests

label_map = {
    1: {'id': 1, 'name': 'actor'},
    2: {'id': 2, 'name': 'use_case'},
    3: {'id': 3, 'name': 'text'},
    4: {'id': 4, 'name': 'association'},
    5: {'id': 5, 'name': 'generalization'}
}


def inference(image, threshold, ignored_classes):
    image_np = np.array(image)
    detections = detect_fn(image_np)
    thresh_detections = threshold_detections(detections, threshold, ignored_classes)

    return thresh_detections, label_map


def detect_fn(img):
    img = np.expand_dims(img, 0)

    data = json.dumps({"signature_name": "serving_default", "instances": img.tolist()})
    headers = {"content-type": "application/json"}
    response = requests.post('http://localhost:8501/v1/models/s2d:predict', data=data, headers=headers)
    if response.status_code != 200:
        print('Error:', response.status_code, response.text)

    result = json.loads(response.text)
    return result['predictions'][0]


def threshold_detections(detections, threshold, ignored_classes):
    detections['detection_classes'] = np.array(detections["detection_classes"]).astype(np.int64)
    indices = list(filter(lambda idx: detections['detection_scores'][idx] >= threshold[detections['detection_classes'][idx]] and label_map[detections['detection_classes'][idx]]['name'] not in ignored_classes,
                          range(int(detections['num_detections']))))

    for (key, value) in detections.items():
        if key != 'num_detections':
            detections[key] = np.take(detections[key], indices, 0)
    return detections
