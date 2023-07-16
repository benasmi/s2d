import cv2

# read input image
img = cv2.imread('data/line2.JPG')

# convert the image to grayscale
gray = cv2.cvtColor(img, cv2.COLOR_BGR2GRAY)

# Initiate SIFT object with default values
sift = cv2.SIFT_create()

# find the keypoints on image (grayscale)
kp = sift.detect(gray, None)

print(kp)
# draw keypoints in image
img2 = cv2.drawKeypoints(gray, kp, None, flags=0)

# display the image with keypoints drawn on it
cv2.imshow("Keypoints", img2)
cv2.waitKey(0)
cv2.destroyAllWindows()
