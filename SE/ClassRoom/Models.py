from keyConstants import *
from service import getClassRoomService
from collections import OrderedDict
from PeerReview.Logger import getLogger
from sheetUtility import readAssignmentDetails
from instructorUtility import getGradeFormsFolderId
from OAuth.views import get_global_account_credentials
import json

log = getLogger("Models")


def isTeacher(credentials, course_id):
    try:
        service = getClassRoomService(credentials)
        service.courses().teachers().get(userId=ME_KEY, courseId=course_id).execute()
        checkGlobalAccount(service, courseId=course_id)
    except Exception as e:
        if (hasattr(e, "content") and json.loads(e.content)[ERROR_KEY][MESSAGE_KEY]) == NOT_INSTRUCTOR_ERROR_MESSAGE:
            log.debug("User is not an Instructor. %s", str(e))
            return False
    return True


def checkGlobalAccount(instructorService, courseId):
    globalService = getClassRoomService(get_global_account_credentials())
    log.info("Checking global account as instructor.")
    try:
        globalService.courses().teachers().get(courseId=courseId, userId=ME_KEY).execute()
        log.info("Global account is an instructor")
        return
    except Exception as e:
        addGlobalAccountAsInstructor(instructorService, globalService, courseId)
        log.info("Global account added as an instructor")


def addGlobalAccountAsInstructor(instructorService, globalService, courseId):
    try:
        globalAccountUserProfile = globalService.userProfiles().get(userId=ME_KEY).execute()
        globalAccountUserId = globalAccountUserProfile[ID_KEY]
        createInvitationBody = {COURSE_ID_KEY: courseId, USER_ID_KEY: globalAccountUserId, ROLE_KEY: TEACHER_ROLE_KEY}
        invitationCreateResponse = instructorService.invitations().create(body=createInvitationBody).execute()
        invitationId = invitationCreateResponse[ID_KEY]
        globalService.invitations().accept(id=invitationId).execute()
    except Exception as e:
        log.error("Exception thrown while creating global account : %s", str(e))


def formatAssignmentDetails(credentials, request, courseId):
    form_details = OrderedDict()
    for k in INSTRUCTOR_FORM_KEYS:
        if k in request.keys():
            form_details[k] = request[k]
        else:
            form_details[k] = ""
    number_questions = int(form_details['numberQuestions'])
    for i in range(1, number_questions + 1):
        form_details["q-" + str(i)] = request["q-" + str(i)]
    return form_details


def formatGradeDetails(req, count):
    form_details = {}
    for k in GRADE_FORM_KEYS:
        a = []
        for i in range(0, int(count)):
            key = k + str(i + 1)
            a.append(req[key] if key in req.keys() else "")
        form_details[k] = a
    return form_details


def getAssignmentDetails(courseId, assId):
    globalAccountCredentials = get_global_account_credentials()
    driveResourceLinkId = getGradeFormsFolderId(globalAccountCredentials, courseId)
    a = readAssignmentDetails(globalAccountCredentials, driveResourceLinkId, courseId, assId)
    return a


def updateGradingData(details, oldDetails, assId):
    if assId in oldDetails:
        oldDetails[assId][1] = details.get(GRADE_FORM_KEYS[0])
        oldDetails[assId][2] = details.get(GRADE_FORM_KEYS[1])
    return oldDetails
