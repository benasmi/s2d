import numpy as np

from box import KeyPoints

extend_kp_px = 40
mid_point_kp_thresh = 40


def calculate_key_points(image, box, debug=False):
    if debug:
        image.show()

    width, height = image.size

    if width <= mid_point_kp_thresh:
        return calculate_low_width_key_points(image, box)

    if height <= mid_point_kp_thresh:
        return calculate_low_height_key_points(image, box)

    return calculate_box_key_points(image, box)


def apply_threshold(img):
    img = img.convert('L')
    img = img.point(lambda p: 255 if p > 180 else 0)
    img = img.convert('1')
    return img


def pixels(image):
    thresh_image = apply_threshold(image)
    np_image = np.array(thresh_image).flatten()
    return np.count_nonzero(np_image == False)


def calculate_box_key_points(image, box):
    width, height = image.size
    crop_size = 20
    bottom_left_box = pixels(image.crop((0, height - crop_size, crop_size, height)))
    top_right_box = pixels(image.crop((width - crop_size, 0, width, crop_size)))
    bl_tr_aggregate = bottom_left_box + top_right_box

    bottom_right_box = pixels(image.crop((width - crop_size, height - crop_size, width, height)))
    top_left_box = pixels(image.crop((0, 0, crop_size, crop_size)))
    br_tl_aggregate = bottom_right_box + top_left_box

    # line from bottom left to top right
    if bl_tr_aggregate > br_tl_aggregate:
        bl_kp = (box.xmin, box.ymax)
        tr_kp = (box.xmax, box.ymin)
        return KeyPoints(tr_kp, bl_kp) if bottom_left_box > top_right_box else bottom_left_box > top_right_box
    else:  # line from top left to bottom left
        br_kp = (box.xmax, box.ymax)
        tl_kp = (box.xmin, box.ymin)
        return KeyPoints(br_kp, tl_kp) if top_left_box > bottom_right_box else KeyPoints(tl_kp, br_kp)


def calculate_low_width_key_points(image, box):
    width, height = image.size

    mp_x = (box.xmin + box.xmax) / 2
    keypoint = (mp_x, box.ymin), (mp_x, box.ymax)
    extended_keypoint = (mp_x, box.ymin - extend_kp_px), (mp_x, box.ymax + extend_kp_px)

    # todo: implement
    bottom_box = image.crop(0, height - 40, width, height)
    top_box = image.crop(0, 0, width, 40)

    return keypoint, extended_keypoint


def calculate_low_height_key_points(image, box):
    width, height = image.size
    mp_y = (box.ymin + box.ymax) / 2
    l_kp = (box.xmin, mp_y)
    r_kp = (box.xmax, mp_y)

    left_box = image.crop((0, 0, 40, height))
    right_box = image.crop((width - 40, 0, width, height))

    return KeyPoints(r_kp, l_kp) if pixels(left_box) > pixels(right_box) else KeyPoints(l_kp, r_kp)
