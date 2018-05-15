from PeerReview.Logger import getLogger
from service import getClassRoomService, getDriveService, getSheetService
from keyConstants import *
from collections import OrderedDict
from OAuth.views import get_global_account_credentials
from sheetUtility import readAssignmentDetails, readStudentDataFromSheet, writeGradesToSheet, extractFileId
from instructorUtility import getGradeFormsFolderId

log = getLogger("studentUtility")


def fetchStudentGradingData(credentials, courseId, courseWorkId):
    """
    Fetches grading data in the form a dictionary to be displayed on the grading portal.
    :param credentials: Required identity parameter to connect to Google API services.
    :param courseId: Unique identifier of the course
    :param courseWorkId: Unique identifier of the courseWork
    :return: a dictionary of grading data and assignment details
    """
    data = {}
    try:
        globalAccountCredentials = get_global_account_credentials()
        driveResourceLink = getCourseDriveResourceLink(globalAccountCredentials, courseId, courseWorkId)
        driveResourceLinkId = getGradeFormsFolderId(globalAccountCredentials, courseId)
        assignmentDetails = readAssignmentDetails(globalAccountCredentials, driveResourceLinkId, courseId, courseWorkId)
        userProfileId = getUserProfileId(credentials)
        (index, spreadsheetId, valuesList) = readStudentDataFromSheet(globalAccountCredentials, userProfileId, courseId,
                                                                      driveResourceLink, assignmentDetails)
        studentGradingDetail = generateStudentDisplayDic(valuesList, assignmentDetails)
        data[NO_GRADERS] = assignmentDetails[NO_GRADERS]
        data[NO_QUESTIONS] = assignmentDetails[NO_QUESTIONS]
        data[GRADING_DATA] = studentGradingDetail
        data[STUDENT_INDEX] = index
        data[SHEET_ID_KEY] = spreadsheetId
        log.info("Grading details fetched : %s", str(data))
    except Exception as e:
        log.error("Unable to fetch student grading data information, %s", str(e))
    return data


def generateStudentDisplayDic(valuesList, assignmentDetails):
    """
    Generates a dictionary of userId and driveLink to be displayed on student grading page
    :param valuesList: List of rows fetched from sheet
    :param assignmentDetails: Assigment details
    :return: Dictionary containing driveLinks and corresponding grades identified by userId of the student to be graded.
    """
    studentGradingDetail = OrderedDict()
    number_questions = int(assignmentDetails[NO_QUESTIONS])
    for i in range(int(assignmentDetails[NO_GRADERS])):
        marksList = [""] * number_questions
        justificationList = [""] * number_questions
        studentDetailList = []
        row = valuesList[i]
        # Check if grading assignment is not available for student
        if (len(row) <= SUBMISSION_START_SHEET_INDEX):
            continue
        # Check if scores and justifications are there in the sheet
        if (len(row) > MARKS_START_SHEET_INDEX):
            # Check if only scores are there
            if (len(row) <= (MARKS_START_SHEET_INDEX + number_questions)):
                marksList[:len(row) - MARKS_START_SHEET_INDEX] = row[MARKS_START_SHEET_INDEX:]
            # Check if either score or justification is in sheet
            else:
                marksList[:number_questions] = row[MARKS_START_SHEET_INDEX:MARKS_START_SHEET_INDEX + number_questions]
                justificationList[:len(row) - MARKS_START_SHEET_INDEX -
                                   number_questions] = row[MARKS_START_SHEET_INDEX + number_questions:]
        studentDetailList.append(row[ASSIGNMENT_LINK_SHEET_INDEX])
        studentDetailList.append(marksList)
        studentDetailList.append(justificationList)
        studentGradingDetail[row[3]] = studentDetailList
    log.info("Student grading details : %s", str(studentGradingDetail))
    return studentGradingDetail


def getUserProfileId(credentials):
    """
    Returns the classroom based identifier of the user.
    :param credentials: Required identity parameter to connect to Google ClassRoom API services.
    :return: Unique user google classroom identifier.
    """
    service = getClassRoomService(credentials)
    userProfileResult = service.userProfiles().get(userId=ME_KEY).execute()
    userProfileId = userProfileResult[ID_KEY]
    log.info("User Profile Id %s", userProfileId)
    return userProfileId


def getCourseDriveResourceLink(globalAccountCredentials, courseId, courseWorkId):
    """
    Returns the drive resource link for the course
    :param globalAccountCredentials: Required identity parameter to connect to Google ClassRoom API services.
    :param courseId: Unique identifier of the course
    :param courseWorkId: Unique identifier of the courseWork
    :return: Drive Resource link for the course.
    """
    globalAccountService = getClassRoomService(globalAccountCredentials)
    courseWorkDetail = globalAccountService.courses().courseWork().get(courseId=courseId, id=courseWorkId).execute()
    # FIXME: if no student has submitted for any, there won't be a assignment folder
    driveResourceLink = courseWorkDetail[ASSIGNMENT_KEY][STUDENT_WORK_FOLDER_KEY][ALTERNATE_DRIVEFILE_LINK_KEY]
    log.info("Drive Resource Link %s", driveResourceLink)
    return driveResourceLink


def updateStudentAssignmentGradeData(index, number_graders, number_questions, spreadsheetId, gradingData):
    """
    Updates the grades of assigned grading assignment as provided by the student
    :param index: Index of the student in the overall student list
    :param number_graders: Number of grading assignments graded by each student
    :param number_questions: Number of questions per assignment
    :param spreadsheetId: Spreadsheet Id of the sheet.
    :param gradingData: Updates marks and justification data
    :return: None
    """
    global_credentials = get_global_account_credentials()
    sheetValueList = []
    for key in gradingData.keys():
        assignmentGradeList = []
        assignmentGradeList.extend(gradingData[key][1])  # Marks List
        assignmentGradeList.extend(gradingData[key][2])  # Justification List
        sheetValueList.append(assignmentGradeList)
    writeGradesToSheet(index, global_credentials, spreadsheetId, number_graders, number_questions, sheetValueList)
