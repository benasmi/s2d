import uuid


class KeyPoints:
    ext_px = 40

    def __init__(self, start, end, type):
        self.start = start
        self.end = end
        self.type = type


class BoundingBox:
    def __init__(self, image, coordinates, label, score):
        width, height = image.size
        ymin, xmin, ymax, xmax = coordinates[0:4]

        self.id = uuid.uuid4().hex
        self.ymin = ymin * height
        self.ymax = ymax * height
        self.xmin = xmin * width
        self.xmax = xmax * width

        self.left_top = (xmin * width, ymin * height)
        self.left_bottom = (xmin * width, ymax * height)
        self.right_bottom = (xmax * width, ymax * height)
        self.right_top = (xmax * width, ymin * height)
        self.center = ((xmax * width + xmin * width) / 2, (ymax * height + ymin * height) / 2)

        self.label = label
        self.score = score
        self.used = False
        self.text = None
        self.key_points = None

    def crop(self, image):
        return image.crop((*self.left_top, *self.right_bottom))
