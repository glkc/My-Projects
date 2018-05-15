import cv2
import numpy
import easygui
import GetPoints

#
# CAM_INT_MAT = numpy.array([[10284.93526679914, 0, 1852.68469102152],
#                            [0, 10352.00296486220, 1165.19704037070],
#                            [0, 0, 1]], dtype=numpy.float32)
# DIST_COEFFS = numpy.array([0.364994764321032, -7.046301689666628, 0, 0], dtype=numpy.float32)
#
# poleTopPoints = [[[1337, 655]], [[1742, 1029]]]
# poleBasePoints = [[[1317, 1198]], [[1715, 1434]]]
# shadowPoints = [[[2067, 1239]], [[2291, 1465]], [[2088, 1244]], [[2305, 1472]], [[2165, 1250]], [[2369, 1474]]]
#
#
# def undistortPoints(penPoints):
#     penPoints = numpy.array(numpy.transpose(penPoints), dtype=numpy.float32)
#     print cv2.undistortPoints(penPoints, CAM_INT_MAT, DIST_COEFFS)
#
#
# undistortPoints(poleTopPoints)
# undistortPoints(poleBasePoints)
# undistortPoints(shadowPoints)

img1 = easygui.fileopenbox().split('.jpg', 1)[0]
print GetPoints.GetPoints(img1).getPoints()
