import cv2 as cv

img = cv.imread('data/line3.JPG', cv.IMREAD_GRAYSCALE)
assert img is not None, "file could not be read, check with os.path.exists()"
ret, thresh1 = cv.threshold(img, 127, 255, cv.THRESH_BINARY)
