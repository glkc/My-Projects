import numpy
import GetPoints
import Utils
import easygui

CAM_INT_MAT = [[1028.493526679914, 0, 185.268469102152],
               [0, 1035.200296486220, 116.519704037070],
               [0, 0, 1]]


class ImageData:
    def __init__(self, path):
        self.img = None
        self.altitudeAngle = None
        self.azimuthAngle = None
        self.getData(path)

    def getData(self, path):
        easygui.msgbox('Select the two PoleTop Points, followed by PoleBase Points, followed by PoleShadowEnd Points.'
                       ' Click OK', title="Follow Instructions")
        points = GetPoints.GetPoints(path).getPoints()
        poleTopPoints = [points[0], points[1]]
        poleBasePoints = [points[2], points[3]]
        shadowPoints = [points[4], points[5]]
        # print self.poleTopPoints, self.poleBasePoints, self.shadowPoints

        vZInf = Utils.getPointInfinity(poleTopPoints[0], poleBasePoints[0], poleBasePoints[0], poleBasePoints[1])
        vShadesInf = Utils.getPointsInfinity(poleBasePoints, shadowPoints)
        vShadePointsInf = Utils.getPointsInfinity(poleBasePoints, shadowPoints, baseLine=True)

        CAM_IAC = numpy.dot(numpy.transpose(numpy.linalg.inv(CAM_INT_MAT)), numpy.linalg.inv(CAM_INT_MAT))
        self.altitudeAngle = Utils.getAltitudeAngles(vZInf, vShadesInf, vShadePointsInf, CAM_IAC)[0]

        vx = vShadePointsInf[0]
        vy = numpy.cross(numpy.dot(CAM_IAC, vx), numpy.dot(CAM_IAC, vZInf))
        self.azimuthAngle = Utils.getAzimuthAngles(vy / vy[2], vx, vShadesInf, CAM_IAC)[0]
