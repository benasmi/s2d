import uuid


class KeyPoints:
    ext_px = 40

    def __init__(self, start, end):
        self.start = start
        self.end = end


class BoundingBox:
    def __init__(self, image, coordinates, label, score, text=None):
        width, height = image.size
        ymin, xmin, ymax, xmax = coordinates[0:4]

        self.id = uuid.uuid4().hex
        self.ymin = ymin * height
        self.ymax = ymax * height
        self.xmin = xmin * width
        self.xmax = xmax * width

        self.width = abs(self.xmin - self.xmax)
        self.height = abs(self.ymin - self.ymax)

        self.left_top = (xmin * width, ymin * height)
        self.left_bottom = (xmin * width, ymax * height)
        self.right_bottom = (xmax * width, ymax * height)
        self.right_top = (xmax * width, ymin * height)
        self.center = ((xmax * width + xmin * width) / 2, (ymax * height + ymin * height) / 2)
        self.center_bottom = ((xmax * width + xmin * width) / 2, (ymax * height))

        self.label = label
        self.score = score
        self.used = False
        self.text = text
        self.key_points = None

    def crop(self, image, padding=None):
        if padding is None:
            return image.crop((*self.left_top, *self.right_bottom))
        else:
            return image.crop((
                self.left_top[0] - padding,
                self.left_top[1] - padding,
                self.right_bottom[0] + padding,
                self.right_bottom[1] + padding
            ))


class BoundingBoxes:
    def __init__(self, image, detections, category_index):
        self.boxes = [
            BoundingBox(image, b, category_index[detection_class]['name'], score)
            for b, detection_class, score in zip(
                detections['detection_boxes'],
                detections['detection_classes'],
                detections['detection_scores']
            )
        ]

    def add_box(self, image, text_box):
        width, height = image.size

        xmin = text_box['bounding_box'][0].x / width
        ymin = text_box['bounding_box'][0].y / height

        xmax = text_box['bounding_box'][2].x / width
        ymax = text_box['bounding_box'][2].y / height

        self.boxes.append(
            BoundingBox(image, [ymin, xmin, ymax, xmax], "text", text_box['confidence'], text_box['text']))

    def remove_by_ids(self, ids):
        self.boxes = list(filter(lambda x: x.id not in ids, self.boxes))
        return self

    def filter_by(self, *labels, used=None, custom_filter=None):
        filter_func = lambda x: (x.label in labels) \
                                and (x.used is used if used is not None else True) \
                                and (custom_filter(x) if custom_filter else True)
        return list(filter(filter_func, self.boxes))
