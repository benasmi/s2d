import os
import numpy as np
import matplotlib.pyplot as plt
import warnings
import tensorflow as tf
import time

from object_detection.utils import label_map_util
from object_detection.utils import visualization_utils as viz_utils

import matplotlib

os.environ['TF_CPP_MIN_LOG_LEVEL'] = '2'  # Suppress TensorFlow logging (1)

tf.get_logger().setLevel('ERROR')  # Suppress TensorFlow logging (2)

# Enable GPU dynamic memory allocation
gpus = tf.config.experimental.list_physical_devices('GPU')
for gpu in gpus:
    tf.config.experimental.set_memory_growth(gpu, True)

matplotlib.use('TkAgg')

print('Loading model...', end='')
start_time = time.time()

# Load saved model and build the detection function
absolute_path = os.path.dirname(__file__)

model_path = os.path.join(absolute_path, "model", "saved_model")
detect_fn = tf.saved_model.load(model_path)

end_time = time.time()
elapsed_time = end_time - start_time
print('Done! Took {} seconds'.format(elapsed_time))

label_path = os.path.join(absolute_path, os.path.join("model", "label_map.pbtxt"))
warnings.filterwarnings('ignore')  # Suppress Matplotlib warnings
category_index = label_map_util.create_category_index_from_labelmap(label_path, use_display_name=True)


def inference(image, min_thresh):
    image_np = np.array(image)

    input_tensor = tf.convert_to_tensor(image_np)
    input_tensor = input_tensor[tf.newaxis, ...]

    detections = detect_fn(input_tensor)

    num_detections = int(detections.pop('num_detections'))
    detections = {key: value[0, :num_detections].numpy()
                  for key, value in detections.items()}
    detections['num_detections'] = num_detections
    detections['detection_classes'] = detections['detection_classes'].astype(np.int64)

    indices = list(filter(lambda idx: detections['detection_scores'][idx] >= min_thresh,
                          range(detections['num_detections'])))

    for (key, value) in detections.items():
        if key != 'num_detections':
            detections[key] = np.take(detections[key], indices, 0)

    return image_np.copy(), detections, category_index


def plot_inference(img_numpy, detections):
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
