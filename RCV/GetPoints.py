import cv2
import numpy

CAM_INT_MAT = numpy.array([[1028.493526679914, 0, 185.268469102152],
                           [0, 1035.200296486220, 116.519704037070],
                           [0, 0, 1]], dtype=numpy.float64)
DIST_COEFFS = [0.364994764321032, -7.046301689666628]


class GetPoints:
    def __init__(self, imgPath):
        self.penPoints = []
        self.imgPath = imgPath
        self.img = None

    def getPoints(self):
        self.getImages()
        # self.undistortPoints()
        self.penPoints[:] = [x + (1,) for x in self.penPoints]
        return self.penPoints

    def getImages(self):
        self.img = cv2.imread(self.imgPath + '.jpg')
        cv2.namedWindow(Constants.IMAGE_1, cv2.WINDOW_NORMAL)
        cv2.setMouseCallback(Constants.IMAGE_1, self.getPointsOnImage)
        self.showImage(Constants.IMAGE_1, self.img)
        cv2.imwrite(self.imgPath.split('.jpg', 1)[0] + '_Points.jpg', self.img)

    def getPointsOnImage(self, event, x, y, flags, param):
        if event == cv2.EVENT_LBUTTONDOWN:
            self.penPoints.append((x, y))
            cv2.circle(self.img, (x, y), 10, (255, 0, 255), -1)

    def undistortPoints(self):
        self.penPoints = numpy.array(numpy.transpose(self.penPoints)).astype('float32')
        self.penPoints = cv2.undistortPoints(self.penPoints, CAM_INT_MAT, DIST_COEFFS)

    @staticmethod
    def showImage(imageName, data):
        while True:
            cv2.imshow(imageName, data)
            key = cv2.waitKey(1) & 0xFF
            if key == ord("b"):
                break


class Constants:
    IMAGE_1 = "Image with pen"
