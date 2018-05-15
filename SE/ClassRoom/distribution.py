from random import shuffle
from PeerReview.Logger import getLogger
from service import getClassRoomService, getDriveService, getSheetService
from mail import SendMessage
from keyConstants import *
from sheetUtility import writeGradingDetailsToSheet, extractFileId, createSheet, getStudentData, sortByUserId
from instructorUtility import getGradeFormsFolderId, getInstructorEmailList

log = getLogger("distribution")


def process(credentials, paramDic, courseId, courseName, courseWorkId, courseWorkName):
    """
    Performs the task of storing instructor's configuration and initiates the process of randomly distributing assignments for grading among students.
    :param credentials: Required identity parameter to connect to Google API services.
    :param paramDic: Configuration parameters dictionary
    :param courseId: Unique identifier of the course
    :param courseName: Course name
    :param courseWorkId: Unique identifier of an assignment in  a course.
    :param courseWorkName: Assignment name
    :return:
    """
    service = getClassRoomService(credentials)
    courseWorkGetResult = service.courses().courseWork().get(courseId=courseId, id=courseWorkId).execute()
    driveResourceLink = courseWorkGetResult[ASSIGNMENT_KEY][STUDENT_WORK_FOLDER_KEY][ALTERNATE_DRIVEFILE_LINK_KEY]
    studentData = getStudentData(credentials, courseId)
    gradingData = randomDistribute(credentials, paramDic, courseId, courseName, courseWorkId, courseWorkName,
                                   studentData)
    studentDataDic = sortByUserId(studentData)
    driveResourceLinkId = extractFileId(driveResourceLink)
    spreadsheetId = createSheet(credentials, driveResourceLinkId, ASSIGNMENT_DISTRIBUTION_FILE_KEY)
    sheetValueList = formatGradingDistributionData(studentDataDic, gradingData, paramDic)
    writeGradingDetailsToSheet(credentials, spreadsheetId, paramDic, sheetValueList)


def storeAssignmentDetails(credentials, courseId, courseWorkId, paramDic):
    """
    Writes instructor's configuration to
    :param credentials: Required identity parameter to connect to Google API services.
    :param courseId: Unique identifier of the course
    :param courseWorkId: Unique identifier of an assignment in  a course.
    :param paramDic: Configuration parameters dictionary of the courseWork
    :return: None
    """
    gradeFolderId = getGradeFormsFolderId(credentials, courseId)
    writeAssignmentDetails(credentials, paramDic, gradeFolderId, courseId, courseWorkId)


def writeAssignmentDetails(credentials, paramDic, driveResourceLinkId, courseId, courseWorkId):
    """
    Stores instructor's configuration into the configuration sheet
    :param credentials: Required identity parameter to connect to Google API services.
    :param paramDic: Configuration parameters dictionary
    :param driveResourceLinkId : Drive link to courseWork's drive folder.
    :param courseId: Unique identifier of the course
    :param courseWorkId: Unique identifier of an assignment in  a course.
    :return: None
    """
    try:
        spreadsheetId = createSheet(credentials, driveResourceLinkId,
                                    INSTRUCTOR_FORM_FILE_KEY + UNDERSCORE_KEY + courseWorkId)
        writeAssignmentDetailsToSheet(credentials, paramDic, spreadsheetId)
        log.info("Instructor's configuration for courseId %s and courseWorkId %s written.", courseId, courseWorkId)
    except Exception as ex:
        log.error("Error in writing instructor configuration to sheet for assignment %s", courseWorkId)
        log.error(str(ex))


def writeAssignmentDetailsToSheet(credentials, paramDic, spreadsheetId):
    """
    Writes the instructor's configuration into the sheet provided by :param spreadsheetId.
    :param credentials: Required identity parameter to connect to Google Sheet API service.
    :param paramDic: Assignment detail parameters to be written into the sheet
    :param spreadsheetId: Unique identifier of the sheet
    :return: None
    """
    # Finds the range of the column index in accordance with the number of configuration parameters.
    rangeEndIndex = chr(ASCII_A + len(paramDic) - 1)
    # Since parameters are going to be singular values, we need just 1 row for each configuration.
    range = SHEET_START_COLUMN + ROW_1 + ":" + rangeEndIndex + ROW_2
    requestBody = {RANGE_KEY: range, VALUES_KEY: [list(paramDic.keys()), list(paramDic.values())]}
    serviceSheet = getSheetService(credentials)
    serviceSheet.spreadsheets().values().update(spreadsheetId=spreadsheetId, range=range, body=requestBody,
                                                valueInputOption=SHEET_VALUE_INPUT_OPTION_RAW).execute()
    log.info("Instructor's configuration written to sheet %s ", spreadsheetId)


def getStudentSubmissionList(service, courseId, courseWorkId):
    """
    Returns the list of student submissions
    :param service: Parameter to access Google Classroom service
    :param courseId: Unique identifier of the course
    :param courseWorkId: Unique identifier of an assignment in  a course.
    :return: A list of student submission
    """
    studentSubmissionListResponse = service.courses().courseWork().studentSubmissions().list(courseId=courseId,
                                                                                             courseWorkId=courseWorkId).execute()
    studentSubmissionList = studentSubmissionListResponse.get(STUDENT_SUBMISSIONS_KEY)
    log.info("Student StudentSubmission list generated for assignment : %s", courseWorkId)
    return studentSubmissionList


def getDistributionData(service, courseId, courseWorkId):
    """
    Generates distribution data for grading random assignment distribution among students
    :param service: Parameter to access Google Classroom service
    :param courseId: Unique identifier of a course
    :param courseWorkId: Unique identifier of an assignment in  a course.
    :return: A tuple containing a list of userIds of all the students and a dictionary with student submissions identified by their userId.
    """
    studentSubmissionList = getStudentSubmissionList(service, courseId, courseWorkId)
    updateStudentSubmissionList = [d for d in studentSubmissionList if ATTACHMENTS_KEY in d[ASSIGNMENT_SUBMISSION_KEY]]
    userIdList = [unicode(d[USER_ID_KEY]) for d in updateStudentSubmissionList]
    log.info("Userid list generated for course %s and courseWork %s", courseId, courseWorkId)
    studentSubmissionsDic = {}
    for studentSubmission in updateStudentSubmissionList:
        studentSubmissionsDic[studentSubmission[USER_ID_KEY]] = studentSubmission
    log.info("Data for random distribution generated for courseId %s and courseWorkdId %s", courseId, courseWorkId)
    return (userIdList, studentSubmissionsDic)


def randomDistribute(credentials, paramDic, courseId, courseName, courseWorkId, courseWorkName, studentData):
    """
    Randomly distibutes the assignment among students for grading
    :param credentials: Required identity parameter to connect to Google Sheet API service.
    :param paramDic: Configuration parameter dictionary
    :param courseId: Unique identifier of a course
    :param courseName: Course name
    :param courseWorkId: Unique identifier of an assignment in  a course.
    :param courseWorkName: Assignment name
    :param studentData : Dictionary containing student information identified by student's userId
    :return: Dictionary containing randomly distributed assignments among students.
    """
    try:
        service = getClassRoomService(credentials)
        (userIdList, studentSubmissionsDic) = getDistributionData(service, courseId, courseWorkId)
        shuffle(userIdList)
        randomIndexDic = randomize(len(userIdList), int(paramDic[NO_GRADERS]))
        assignmentListDic = {}
        studentEmailList = []
        for key in randomIndexDic.keys():
            keySubList = []
            userId = userIdList[key]
            emailId = studentData[userId].get(PROFILE_KEY)[EMAIL_ADDRESS_KEY]
            serviceDrive = getDriveService(credentials)
            for index in randomIndexDic[key]:
                attachments = studentSubmissionsDic[userIdList[index]][ASSIGNMENT_SUBMISSION_KEY][ATTACHMENTS_KEY]
                assignmentEmailId = studentData[userIdList[index]][PROFILE_KEY][EMAIL_ADDRESS_KEY]
                driveLink = ""
                for attachment in attachments:
                    if DRIVEFILE_KEY in attachment:
                        link = attachment[DRIVEFILE_KEY][ALTERNATE_DRIVEFILE_LINK_KEY]
                    elif LINK_KEY in attachment:
                        link = attachment[LINK_KEY][URL_KEY]
                    grantPermissions(serviceDrive, link, emailId)
                    driveLink += link + ","
                tuple = (userIdList[index], assignmentEmailId, driveLink[:-1])
                keySubList.append(tuple)
            assignmentListDic[userId] = keySubList
            studentEmailList.append(emailId)
        instructorEmailList = getInstructorEmailList(service, courseId)
        sendMail(credentials, studentEmailList, instructorEmailList, paramDic['message'], courseName, courseWorkName)
        log.info("Distribution of assignment among students successful for courseId %s and courseWorkdId %s", courseId,
                 courseWorkId)
        return assignmentListDic
    except Exception as ex:
        log.error("Unable to distribute assignment among students %s", str(ex))


def randomize(num_assignments, num_graders_per_assignment):
    """
    Distribution of random indexes
    :param num_assignments: Total number of assignments
    :param num_graders_per_assignment: Number of assignments per grader or Number of graders per assignment
    :return: A dictionary of random indexes.
    """
    result = {}
    for i in range(0, num_assignments):
        assigned_graders = []
        for j in range(0, num_graders_per_assignment):
            assigned_graders.append((i + j + 1) % num_assignments)
        result[i] = assigned_graders
    log.info("Randomize distribution of assignments.")
    return result


def grantPermissions(serviceDrive, link, emailId):
    """
    Grant view permissions to a drive resource to the given student
    :param serviceDrive: Parameter to access Google Drive service
    :param link: Google drive resource link
    :param emailId: Email-Id of the student to be given the access
    :return: None
    """
    try:
        fileId = extractFileId(link)
        permissionBody = {ROLE_KEY: PERMISSION_ROLE_READER, TYPE_KEY: PERMISSION_TYPE_USER, EMAIL_ADDRESS_KEY: emailId}
        serviceDrive.permissions().create(fileId=fileId, body=permissionBody, sendNotificationEmail=False).execute()
        log.info("Permission granted to user : " + emailId)
    except Exception as ex:
        log.error("Error in granting permission to the students. %s", str(ex))


def formatGradingDistributionData(studentDataDic, gradingData, assignmentDetailDic):
    """
    Format the grading data into rows to be inserted into the sheet
    :param studentDataDic: A dictionary of student data identified by student's user id
    :param gradingData: Dictionary containing the grading distribution details indexed by student's userId
    :param assignmentDetailDic: Assignment detail parameters
    :return: A list of rows containing distributed grading data.
    """
    number_questions = int(assignmentDetailDic[NO_QUESTIONS])
    number_graders = int(assignmentDetailDic[NO_GRADERS])
    headerList = GRADING_SHEET_HEADER
    for question in range(number_questions):
        headerList.append('Question' + str(question + 1))
    for question in range(number_questions):
        headerList.append('Justification' + str(question + 1))
    sheetValueList = [headerList]
    for userId in studentDataDic.keys():
        if userId in gradingData:
            for gradingDetail in gradingData[userId]:
                valueList1 = [SHEET_BLANK_CELL] * (len(headerList))
                valueList1[0] = userId
                valueList1[1] = studentDataDic[userId][PROFILE_KEY][NAME_KEY][FULL_NAME_KEY]
                valueList1[2] = studentDataDic[userId][PROFILE_KEY][EMAIL_ADDRESS_KEY]
                valueList1[3] = gradingDetail[0]
                valueList1[4] = gradingDetail[1]
                valueList1[5] = gradingDetail[2]
                sheetValueList.append(valueList1)
        else:
            for i in range(number_graders):
                valueList1 = [SHEET_BLANK_CELL] * (len(headerList))
                valueList1[0] = userId
                valueList1[1] = studentDataDic[userId][PROFILE_KEY][NAME_KEY][FULL_NAME_KEY]
                valueList1[2] = studentDataDic[userId][PROFILE_KEY][EMAIL_ADDRESS_KEY]
                sheetValueList.append(valueList1)
    log.info("Formatting grading distribution data successful.")
    return sheetValueList


def sendMail(credentials, studentEmailList, instructorEmailList, emailMessage, courseName, courseWorkName):
    """
    Method to send email to all the instructors with students as BCC.
    :param credentials: Required identity parameter to connect to Google Mail API service.
    :param studentEmailList: List of student Email Id.
    :param instructorEmailList: List of Instructor's email Id
    :param emailMessage: Email Message to be added in the mail
    :param courseName: Course name
    :param courseWorkName: Course Work name
    :return: None
    """
    bcc = ",".join(studentEmailList)
    to = ",".join(instructorEmailList)
    # TODO: Change sender.
    sender = ME_KEY
    subject = courseName + " : " + courseWorkName + " grading assignment"
    msgHtml = emailMessage
    msgPlain = " "
    SendMessage(credentials, sender, to, bcc, subject, msgHtml, msgPlain)
