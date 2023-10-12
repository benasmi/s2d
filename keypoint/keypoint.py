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

    return calculate_box_key_points(image, box)


def apply_threshold(img):
    img = img.convert('L')
    img = img.point(lambda p: 255 if p > bin_thresh else 0)
    img = img.convert('1')
    return img


def get_true_pixel_values(image):
    return sum(np.array(apply_threshold(image)).flatten())


def determine_start_end(box):
    return box.label == 'generalization' or box.label == 'dotted_line'


def calculate_box_key_points(image, box):
    width, height = image.size

    bottom_left_box = get_true_pixel_values(image.crop((0, height - 40, 40, height)))
    top_right_box = get_true_pixel_values(image.crop((width - 40, 0, width, 40)))
    bl_tr_aggregate = bottom_left_box + top_right_box

    bottom_right_box = get_true_pixel_values(image.crop((width - 40, height - 40, width, height)))
    top_left_box = get_true_pixel_values(image.crop((0, 0, 40, 40)))
    br_tl_aggregate = bottom_right_box + top_left_box

    # line from bottom left to top right
    if bl_tr_aggregate < br_tl_aggregate:
        type = "bottom_left_top_right"
        bl_kp = (box.xmin, box.ymin)
        tr_kp = (box.xmax, box.ymax)
        if not determine_start_end(box):
            return KeyPoints(bl_kp, tr_kp, type)
        else:
            if bottom_left_box < top_right_box:
                return KeyPoints(bl_kp, tr_kp, type)
            else:
                return KeyPoints(tr_kp, bl_kp, type)
    else:  # line from top left to bottom left
        type = "top_left_bottom_right"
        br_kp = (box.xmax, box.ymax)
        tl_kp = (box.xmin, box.ymin)
        if not determine_start_end(box):
            return KeyPoints(br_kp, tl_kp, type)
        else:
            if top_left_box < bottom_right_box:
                return KeyPoints(tl_kp, br_kp, type)
            else:
                return KeyPoints(br_kp, tl_kp, type)


def calculate_low_width_key_points(image, box):
    width, height = image.size

    mp_x = (box.xmin + box.xmax) / 2
    keypoint = (mp_x, box.ymin), (mp_x, box.ymax)
    extended_keypoint = (mp_x, box.ymin - extend_kp_px), (mp_x, box.ymax + extend_kp_px)

    if not determine_start_end(box):
        return keypoint, extended_keypoint

    # todo: implement
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

    left_box = image.crop((0, 0, 40, height))
    right_box = image.crop((width - 40, 0, width, height))

    if debug:
        left_box.show()
        right_box.show()

    if get_true_pixel_values(left_box) < get_true_pixel_values(right_box):
        return KeyPoints(r_kp, l_kp, "low_height")
    else:
        return KeyPoints(l_kp, r_kp, "low_height")
