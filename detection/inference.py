import os
import numpy as np
from PIL import Image
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

model_path = os.path.join(absolute_path, "model\saved_model")
detect_fn = tf.saved_model.load(model_path)

end_time = time.time()
elapsed_time = end_time - start_time
print('Done! Took {} seconds'.format(elapsed_time))

label_path = os.path.join(absolute_path, "model\label_map.pbtxt")
warnings.filterwarnings('ignore')  # Suppress Matplotlib warnings
category_index = label_map_util.create_category_index_from_labelmap(label_path, use_display_name=True)


def inference(path):
    print('Running inference for {}... '.format(path), end='')

    im = Image.open(path)
    im = im.convert("RGB")
    image_np = np.array(im)

    # Things to try:
    # Flip horizontally
    # image_np = np.fliplr(image_np).copy()

    # Convert image to grayscale
    # image_np = np.tile(
    #     np.mean(image_np, 2, keepdims=True), (1, 1, 3)).astype(np.uint8)

    # The input needs to be a tensor, convert it using `tf.convert_to_tensor`.
    input_tensor = tf.convert_to_tensor(image_np)
    # The model expects a batch of images, so add an axis with `tf.newaxis`.
    input_tensor = input_tensor[tf.newaxis, ...]
    # input_tensor = input_tensor[:, :, :, :3]  # <= add this line
    # input_tensor = np.expand_dims(image_np, 0)
    detections = detect_fn(input_tensor)

    # All outputs are batches tensors.
    # Convert to numpy arrays, and take index [0] to remove the batch dimension.
    # We're only interested in the first num_detections.
    num_detections = int(detections.pop('num_detections'))
    detections = {key: value[0, :num_detections].numpy()
                  for key, value in detections.items()}
    detections['num_detections'] = num_detections

    # detection_classes should be ints.
    detections['detection_classes'] = detections['detection_classes'].astype(np.int64)


    return image_np.copy(), detections


def plot_inference(img_numpy, detections):
    viz_utils.visualize_boxes_and_labels_on_image_array(
        img_numpy,
        detections['detection_boxes'],
        detections['detection_classes'],
        detections['detection_scores'],
        category_index,
        use_normalized_coordinates=True,
        max_boxes_to_draw=200,
        min_score_thresh=.2,
        agnostic_mode=False)

    plt.figure()
    plt.imshow(img_numpy)
    print('Done')
    print('Plotting')
    plt.show()
