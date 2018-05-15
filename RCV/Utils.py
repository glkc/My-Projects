import numpy
import ImageData
import math


def getData(img1, img2, img3):
    img1Data = ImageData.ImageData(img1)
    img2Data = ImageData.ImageData(img2)
    img3Data = ImageData.ImageData(img3)
    return img1Data, img2Data, img3Data


def getPointInfinity(l1p1, l1p2, l2p1, l2p2):
    l1 = numpy.cross(l1p1, l1p2)
    l2 = numpy.cross(l2p1, l2p2)
    p = numpy.cross(l1, l2)
    return p / p[2]


def getPointsInfinity(basePoints, shadowPoints, baseLine=False):
    pInf = []
    if not baseLine:
        for i in range(0, len(shadowPoints) / 2):
            pole1Shade = numpy.cross(basePoints[0], shadowPoints[2 * i])
            pole2Shade = numpy.cross(basePoints[1], shadowPoints[2 * i + 1])
            p = numpy.cross(pole1Shade, pole2Shade)
            pInf.append(numpy.divide(p, p[2]).tolist())
    else:
        poleBase = numpy.cross(basePoints[0], basePoints[1])
        for i in range(0, len(shadowPoints) / 2):
            shadeLine = numpy.cross(shadowPoints[2 * i], shadowPoints[2 * i + 1])
            p = numpy.cross(poleBase, shadeLine)
            pInf.append(numpy.divide(p, p[2]).tolist())
    return pInf


def distance(p1, p2):
    return math.sqrt(math.pow(p2[0] - p1[0], 2) + math.pow(p2[1] - p1[1], 2) + math.pow(p2[2] - p1[2], 2))


def getAltitudeAngles(points1, points2, points3, CAM_IAC=None):
    angles1 = []
    angles2 = []
    if CAM_IAC is None:
        pole1Length = distance(points1[0], points2[0])
        pole2Length = distance(points1[1], points2[1])
        for i in range(0, len(points3) / 2):
            angles1.append(math.atan2(pole1Length, distance(points2[0], points3[2 * i])))
            angles2.append(math.atan2(pole2Length, distance(points2[1], points3[2 * i + 1])))
    else:
        for i in range(0, len(points3)):
            angles1.append(math.acos(getValueForAngle(points2[i], CAM_IAC, points3[i])))
            angles2.append(math.asin(getValueForAngle(points1, CAM_IAC, points3[i])))
    # angles1 = numpy.divide(numpy.add(angles1, angles2), 2)
    print "Altitudes - " + str(map(lambda x: math.degrees(x), angles1))
    print "Altitudes - " + str(map(lambda x: math.degrees(x), angles2))
    return angles1


def getAzimuthAngles(points1, points2, points3, CAM_IAC):
    angles1 = []
    angles2 = []
    for i in range(0, len(points3)):
        angles1.append(math.acos(round(getValueForAngle(points3[i], CAM_IAC, points2), 5)))
        angles2.append(math.asin(round(getValueForAngle(points3[i], CAM_IAC, points1), 5)))
    # angles1 = numpy.divide(numpy.add(angles1, angles2), 2)
    print "Azimuths - " + str(map(lambda x: math.degrees(x), angles1))
    print "Azimuths - " + str(map(lambda x: math.degrees(x), angles2))
    return angles1


def getRho(altitude, azimuth):
    rho1 = cosCos(altitude[1], altitude[0], azimuth[1], azimuth[0])
    rho2 = cosSin(altitude[1], altitude[0], azimuth[1], azimuth[0])
    rho3 = cosCos(altitude[1], altitude[2], azimuth[1], azimuth[2])
    rho4 = cosCos(altitude[1], altitude[2], azimuth[1], azimuth[2])
    return rho1, rho2, rho3, rho4


def cosCos(ang1, ang2, ang3, ang4):
    a = math.cos(ang1) * math.cos(ang3) - math.cos(ang2) * math.cos(ang4)
    b = math.sin(ang1) - math.sin(ang2)
    return a / b


def cosSin(ang1, ang2, ang3, ang4):
    a = math.cos(ang1) * math.sin(ang3) - math.cos(ang2) * math.sin(ang4)
    b = math.sin(ang1) - math.sin(ang2)
    return a / b


def getValueForAngle(p1, w, p2):
    a = getValue(p1, w, p2)
    b = getValue(p1, w, p1)
    c = getValue(p2, w, p2)
    return a / (math.sqrt(b) * math.sqrt(c))


def getValue(p1, w, p2):
    a = numpy.dot(numpy.transpose(p1), w)
    return numpy.dot(a, p2)
