from datetime import datetime
from service import getClassRoomService, getDriveService
from PeerReview.Logger import getLogger
from keyConstants import *
from mail import SendMessage

log = getLogger("instructorUtility")


def createAssignment(credentials, courseId, assignmentDetails):
    """
    Creates google classroom coursework using the details given by the instructor
    :param credentials: Required identity parameter to connect to Google API services.
    :param courseId: Unique identifier of the course
    :param assignmentDetails: Assignment Details as provided by instructor
    :return: None
    """
    try:
        assignmentDeadline = assignmentDetails[ASSIGNMENT_DEADLINE_KEY]
        assignmentLink = assignmentDetails[ASSIGNMENT_LINK_KEY]
        assignmentTitle = assignmentDetails[ASSIGNMENT_NAME_KEY]
        requestBody = createRequestBodyForAssignmentCreation(assignmentDeadline, assignmentLink, assignmentTitle)
        classroomService = getClassRoomService(credentials)
        courseWorkCreateResponse = classroomService.courses().courseWork().create(courseId=courseId,
                                                                                  body=requestBody).execute()
        return courseWorkCreateResponse[ID_KEY]
    except Exception as e:
        raise type(e)("Failed to create courseWork " + e.message)


def createRequestBodyForAssignmentCreation(assignmentDeadline, assignmentLink, assignmentTitle):
    """
    Create request body to be passed for assignment creation
    :param assignmentDeadline: Deadline of the assignment
    :param assignmentLink: Link to the assignment details
    :param assignmentTitle: Title of the assignment
    :return: request body dictionary for assignment creation
    """
    materialsBody = []
    materialsDict = {}
    materialsLinkDict = {}
    materialsLinkDict[URL_KEY] = assignmentLink
    materialsLinkDict[TITLE_KEY] = assignmentTitle
    materialsDict[LINK_KEY] = materialsLinkDict
    materialsBody.append(materialsDict)
    dt = datetime.strptime(assignmentDeadline, DATE_FORMAT_KEY)
    dueDateBody = {}
    dueDateBody[DAY_KEY] = dt.day
    dueDateBody[MONTH_KEY] = dt.month
    dueDateBody[YEAR_KEY] = dt.year
    dueTimeBody = {}
    dueTimeBody[HOURS_KEY] = dt.hour
    dueTimeBody[MINUTES_KEY] = dt.minute
    requestBody = {MATERIALS_KEY: materialsBody, TITLE_KEY: assignmentTitle, STATE_KEY: PUBLISHED_STATE_KEY,
                   WORK_TYPE_KEY: ASSIGNMENT_WORK_TYPE_KEY, ASSOCIATED_WITH_DEVELOPER_KEY: True,
                   DUE_DATE_KEY: dueDateBody, DUE_TIME_KEY: dueTimeBody}
    return requestBody


def getGradeFormsFolderId(credentials, courseId):
    """
    Fetches the drive id of the gradeForms folder which contains all the instructor configuration for courseWorks
    :param credentials: Required identity parameter to connect to Google API services.
    :param courseId: Unique identifier of the course
    :return: Unique drive id of the 'gradeForms' folder
    """
    classroomService = getClassRoomService(credentials)
    courseDetails = classroomService.courses().get(id=courseId).execute()
    courseDriveLinkId = courseDetails[TEACHER_FOLDER_KEY][ID_KEY]
    driveService = getDriveService(credentials)
    query = getQueryToSearchInDrive(GRADE_FORMS_FOLDER_KEY, courseDriveLinkId, FOLDER_MIME_TYPE_KEY)
    searchFileResult = driveService.files().list(q=query).execute()
    if len(searchFileResult.get(FILES_KEY)) == 0:
        return createFormsFolder(driveService, courseDriveLinkId)
    else:
        return searchFileResult.get(FILES_KEY)[0][ID_KEY]


def createFormsFolder(driveService, courseDriveLinkId):
    """
    Generates 'gradeForms' folder if it is not already there/
    :param driveService: Parameter to access Google Drive service
    :param courseDriveLinkId: Unique identifier of the course drive folder
    :return: Unique drive Id of the 'gradeForms' folder
    """
    requestBody = {MIME_TYPE_KEY: FOLDER_MIME_TYPE_KEY, NAME_KEY: GRADE_FORMS_FOLDER_KEY,
                   PARENTS_KEY: [courseDriveLinkId]}
    createFolderResponse = driveService.files().create(body=requestBody).execute()
    return createFolderResponse[ID_KEY]


def updateCourseWorkDeadline(credentials, courseId, courseName, courseWorkId, assignmentDetails):
    """
    Updates the course Work deadline. It also attempts to update the courseWork deadline on classroom, on failure of which an email is sent to all the instructors.
    :param credentials: Required identity parameter to connect to Google API services.
    :param courseId: Unique identifier of the course
    :param courseName: Name of the course
    :param courseWorkId: Unique identifier of the courseWork of the course
    :param assignmentDetails: Updated assignment details dictionary
    :return: None
    """
    classroomService = getClassRoomService(credentials)
    try:
        assignmentDeadline = assignmentDetails[ASSIGNMENT_DEADLINE_KEY]
        dt = datetime.strptime(assignmentDeadline, DATE_FORMAT_KEY)
        dueDateBody = {}
        dueDateBody[DAY_KEY] = dt.day
        dueDateBody[MONTH_KEY] = dt.month
        dueDateBody[YEAR_KEY] = dt.year
        dueTimeBody = {}
        dueTimeBody[HOURS_KEY] = dt.hour
        dueTimeBody[MINUTES_KEY] = dt.minute
        requestBody = {DUE_DATE_KEY: dueDateBody, DUE_TIME_KEY: dueTimeBody}
        patchResponse = classroomService.courses().courseWork().patch(courseId=courseId, id=courseWorkId,
                                                                      updateMask=DUE_DATE_KEY + "," + DUE_TIME_KEY,
                                                                      body=requestBody).execute()
        log.info("Updated course work deadline for course %s and courseWork %s", courseId, courseWorkId)
    except Exception as e:
        instructorEmailList = getInstructorEmailList(classroomService, courseId)
        to = ",".join(instructorEmailList)
        bcc = ""
        sender = ME_KEY
        subject = "Cannot update the assignment Deadline for " + courseName + " " + assignmentDetails[
            ASSIGNMENT_NAME_KEY] + courseWorkId
        msgHtml = ASSIGNMENT_DEADLINE_UPDATE_FAIL_MSG
        msgPlain = " "
        SendMessage(credentials, sender, to, bcc, subject, msgHtml, msgPlain)


def getInstructorEmailList(service, courseId):
    """
    Returns the all the instructor's emailId
    :param service: Parameter to access Google Classroom service
    :param courseId: Unique identifier of the course
    :return: A list of email Ids of all the instructors
    """
    instructorsListResponse = service.courses().teachers().list(courseId=courseId).execute()
    instructorsListResponse = instructorsListResponse.get(TEACHERS_KEY)
    instructorsEmailList = []
    for instructorInfo in instructorsListResponse:
        instructorsEmailList.append(instructorInfo[PROFILE_KEY][EMAIL_ADDRESS_KEY])
    log.info("Instructor email list generated.")
    return instructorsEmailList
