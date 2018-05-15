import Localization
import easygui
import cv2


class Authenticate:
    def __init__(self):
        option = selectVideoOrPics()
        videoPath = None
        if option == Constants.UPLOAD_OPTIONS[1]:
            videoPath = convertVideoToFrames()
        imgs = getImagePaths(videoPath)
        authenticateFeed(imgs[0].encode('utf-8'), imgs[1].encode('utf-8'), imgs[2].encode('utf-8'))
        # authenticateFeed(0, 0, 0)


def selectVideoOrPics():
    msg = "Are you Uploading Pictures or Video. Select the option below."
    choices = Constants.UPLOAD_OPTIONS
    return easygui.buttonbox(msg, choices=choices)


def convertVideoToFrames():
    easygui.msgbox('Select Video feed to be authenticated in the dialog that appears next. Click OK',
                   title="Follow Instructions")
    path = easygui.fileopenbox()
    videoFeed = cv2.VideoCapture(path.encode('utf-8'))
    i = 0
    while True:
        ret, frame = videoFeed.read()
        if ret:
            cv2.imshow('frame', frame)
            if cv2.waitKey(30) & 0xFF == ord('q'):
                break
            cv2.imwrite(path.encode('utf-8').split('.', 1)[0] + '\Frame' + str(i) + '.jpg', frame)
            i += 1
        else:
            break
    videoFeed.release()
    return path.encode('utf-8').split('.', 1)[0]


def getImagePaths(video=None):
    if video is not None:
        easygui.msgbox('Select Images from ' + video + ' Click OK', title="Follow Instructions")
    imgs = []
    for i in range(1, 4):
        easygui.msgbox('Select Image-' + str(i) +
                       ' of the sequence of frames to be authenticated in the dialog that appears next. Click OK',
                       title="Follow Instructions")
        imgs.append(easygui.fileopenbox().split('.jpg', 1)[0])
    return imgs


def authenticateFeed(i1, i2, i3):
    lat, longitude, day, hour = Localization.Localization(i1, i2, i3)
    userValues = getUserInput()
    userValues[:] = [float(x) for x in userValues]
    print longitude - userValues[7], hour * (userValues[6] - userValues[5]) + userValues[5]


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
    print "Reply was:", fieldValues
    return fieldValues


class Constants:
    UPLOAD_OPTIONS = ["Pictures", "Video"]
    INPUT_FIELDS = ["Lat", "Long", "Month", "Day", "Time Hour (in 24 hr)", "Sun Rise Hour (in 24 hr)",
                    "Sun Set Hour(in 24 hr)", "GHA (http://www.celnav.de/longterm.htm)"]


if __name__ == '__main__':
    Authenticate()
