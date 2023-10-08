import os
from detection import inference

# Read image
script_dir = os.path.dirname(__file__)  # <-- absolute dir the script is in
rel_path = "detection\data\images\PA12.png"
abs_file_path = os.path.join(script_dir, rel_path)

# Do inference
img, detections = inference.inference(abs_file_path, min_thresh=.2)

# Plot inference
inference.plot_inference(img, detections)


