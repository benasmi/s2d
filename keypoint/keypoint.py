import numpy as np

from box import KeyPoints

extend_kp_px = 40
mid_point_kp_thresh = 40
bin_thresh = 180
debug = True


def calculate_key_points(image, box):
    if debug:
        image.show()

    width, height = image.size

    if width <= mid_point_kp_thresh:
        return calculate_low_width_key_points(image, box)

    if height <= mid_point_kp_thresh:
        return calculate_low_height_key_points(image, box)

    image.show()
    print(image.size)
    print("test")


def determine_start_end(box):
    return box.label == 'generalization' or box.label == 'dotted_line'


def apply_threshold(img):
    img = img.convert('L')
    img = img.point(lambda p: 255 if p > bin_thresh else 0)
    img = img.convert('1')
    return img


def calculate_low_width_key_points(image, box):
    width, height = image.size

    mp_x = (box.xmin + box.xmax) / 2
    keypoint = (mp_x, box.ymin), (mp_x, box.ymax)
    extended_keypoint = (mp_x, box.ymin - extend_kp_px), (mp_x, box.ymax + extend_kp_px)

    if not determine_start_end(box):
        return keypoint, extended_keypoint

    bottom_box = image.crop(0, height - 40, width, height)
    top_box = image.crop(0, 0, width, 40)

    return keypoint, extended_keypoint


def calculate_low_height_key_points(image, box):
    width, height = image.size

    mp_y = (box.ymin + box.ymax) / 2
    l_kp = (box.xmin, mp_y)
    r_kp = (box.xmax, mp_y)

    if not determine_start_end(box):
        return KeyPoints(l_kp, r_kp, "low_height")

    left_box = apply_threshold(image.crop((0, 0, 40, height)))
    right_box = apply_threshold(image.crop((width - 40, 0, width, height)))

    if debug:
        left_box.show()
        right_box.show()

    if sum(np.array(left_box).flatten()) < sum(np.array(right_box).flatten()):
        return KeyPoints(r_kp, l_kp, "low_height")
    else:
        return KeyPoints(l_kp, r_kp, "low_height")
