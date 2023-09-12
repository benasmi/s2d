import os
import sys
from detection import inference

# Read file path
script_dir = os.path.dirname(__file__)  # <-- absolute dir the script is in
rel_path = sys.argv[1]
abs_file_path = os.path.join(script_dir, rel_path)

# Do inference
inference.inference(abs_file_path)

