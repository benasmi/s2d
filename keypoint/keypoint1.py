import cv2 as cv
import numpy as np
from matplotlib import pyplot as plt

img = cv.imread('data/line3.JPG', cv.IMREAD_GRAYSCALE)
assert img is not None, "file could not be read, check with os.path.exists()"
ret, thresh1 = cv.threshold(img, 127, 255, cv.THRESH_BINARY)

print(thresh1)
titles = ['Original', 'BINARY']
images = [img, thresh1]

for i in range(2):
    print(i)
    plt.subplot(1, 2, i + 1)
    plt.imshow(images[i], 'gray', vmin=0, vmax=255)
    plt.title(titles[i])
    plt.xticks([]), plt.yticks([])
plt.show()
