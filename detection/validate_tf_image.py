"""
Used to validate if images in dataset folder are correct for TF2 model training
"""


from pathlib import Path
import imghdr

data_dir = "dataset"

img_type_accepted_by_tf = ["bmp", "gif", "jpeg", "png"]
for filepath in Path(data_dir).rglob("*"):
    img_type = imghdr.what(filepath)
    if img_type is None:
        print(f"{filepath} is not an image")
    elif img_type not in img_type_accepted_by_tf:
        print(f"{filepath} is a {img_type}, not accepted by TensorFlow")