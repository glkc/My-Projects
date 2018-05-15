import easygui
import GetPoints
import Utils
import numpy

CAM_INT_MAT = [[2266.4, 0, 1992.4],
               [0, 2281.6, 1513.3],
               [0, 0, 1]]


class Authenticate:
    def __init__(self):
        img = getImagePaths()
        authenticateFeed(img)


def getImagePaths():
    easygui.msgbox('Select Image to be authenticated in the dialog that appears next. '
                   'Click OK', title="Follow Instructions")
    return easygui.fileopenbox().split('.', 1)[0]


def authenticateFeed(img1):
    easygui.msgbox('Select the two PoleTop Points, followed by PoleBase Points, followed by PoleShadowEnd Points.'
                   ' Click OK', title="Follow Instructions")
    points1 = GetPoints.GetPoints(img1).getPoints()
    poleTopPoints = [points1[0], points1[1]]
    poleBasePoints = [points1[2], points1[3]]
    shadowPoints = [points1[4], points1[5]]
    vZInf = Utils.getPointInfinity(poleTopPoints[0], poleBasePoints[0], poleBasePoints[0], poleBasePoints[1])
    vShadesInf = Utils.getPointsInfinity(poleBasePoints, shadowPoints)
    vShadePointsInf = Utils.getPointsInfinity(poleBasePoints, shadowPoints, baseLine=True)

    CAM_IAC = numpy.dot(numpy.transpose(numpy.linalg.inv(CAM_INT_MAT)), numpy.linalg.inv(CAM_INT_MAT))
    altitudeAnglesCam = Utils.getAltitudeAngles(vZInf, vShadesInf, vShadePointsInf, CAM_IAC)
    hour1 = altitudeAnglesCam[1] / 180.0
    hour2 = altitudeAnglesCam[0] / 180.0
    userValues = getUserInput()
    userValues[:] = [float(x) for x in userValues]
    print hour1 * (userValues[2] - userValues[1]) + userValues[1]
    print hour2 * (userValues[2] - userValues[1]) + userValues[1]


def getUserInput():
    msg = "Enter Data of Feed Location & Time To Authenticate"
    title = "Feed Authentication"
    fieldNames = Constants.INPUT_FIELDS
    fieldValues = []  # we start with blanks for the values
    fieldValues = easygui.multenterbox(msg, title, fieldNames)
    while 1:
        # make sure that none of the fields was left blank
        errmsg = ""
        for i in range(len(fieldNames)):
            if fieldValues[i].strip() == "":
                errmsg += ('"%s" is a required field.\n\n' % fieldNames[i])
        if errmsg == "":
            break  # no problems found
        fieldValues = easygui.multenterbox(errmsg, title, fieldNames, fieldValues)
    print "User Input:", fieldValues
    return fieldValues


class Constants:
    INPUT_FIELDS = ["Time Hour of picture (in 24 hr)", "Sun Rise Hour (in 24 hr)", "Sun Set Hour(in 24 hr)"]


if __name__ == '__main__':
    Authenticate()
