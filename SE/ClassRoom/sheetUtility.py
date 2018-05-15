from PeerReview.Logger import getLogger
import collections
from service import getClassRoomService, getDriveService, getSheetService
from keyConstants import *
import datetime
import time

log = getLogger("sheetUtility")


def sortByUserId(studentDataDic):
    """
    Returns dictionary sorted in ascending order of userId
    :param studentDataDic: Dictionary needed to be sorted
    :return: Sorted ordered dictionary
    """
    return collections.OrderedDict(sorted(studentDataDic.items()))


def extractFileId(link):
    """
    Extracts the fileId from the link.
    Ex1 : https://drive.google.com/open?id=0B5zk5e6DF4OBUW1BYmkxNzNaa3M , fileId =0B5zk5e6DF4OBUW1BYmkxNzNaa3M
    Ex2 : https://drive.google.com/drive/folders/0B5zk5e6DF4OBfnQ4ZlJKNGNvdkNqbmY1V01jT2t5M1kzbzV1ZFBnTTRTeXNUdE0wQ3plNnM, fileId = 0B5zk5e6DF4OBfnQ4ZlJKNGNvdkNqbmY1V01jT2t5M1kzbzV1ZFBnTTRTeXNUdE0wQ3plNnM
    :param link: Drive link
    :return: Corresponding fileId
    """
    index = link.find('id=')
    if index != -1:
        fileId = link[index + 3:]
    else:
        index = link.rfind('/')
        fileId = link[index + 1:]
    return fileId


def findSheet(serviceDrive, driveResourceFileId, sheetName):
    """
    Searches the given sheet and returns the sheet Id
    :param serviceDrive: Parameter to access Google Drive service
    :param driveResourceFileId: File Id of the drive folder where to search for that sheet
    :param sheetName: Sheet name to be searched.
    :return: spreadsheetId if sheet found or none if not found
    """
    query = getQueryToSearchInDrive(sheetName, driveResourceFileId, SPREADSHEET_MIME_TYPE_KEY)
    searchFileResult = serviceDrive.files().list(q=query).execute()
    if len(searchFileResult.get('files')) == 0:
        return None
    else:
        return searchFileResult.get('files')[0]['id']


def createSheet(credentials, driveResourceFileId, sheetName):
    """
    Returns the sheet Id generated in the courseWork's drive folder.
    :param credentials: Required identity parameter to connect to Google Drive API service.
    :param driveResourceFileId: Unique Identifier of a drive link to courseWork's drive folder.
    :return: Spreadsheet Id of the sheet.
    """
    serviceDrive = getDriveService(credentials)
    result = findSheet(serviceDrive, driveResourceFileId, sheetName)
    if result == None:
        bodyCreateFile = {u'mimeType': u'application/vnd.google-apps.spreadsheet', NAME_KEY: unicode(sheetName),
                          u'parents': [driveResourceFileId]}
        createFileResult = serviceDrive.files().create(body=bodyCreateFile).execute()
        spreadsheetId = createFileResult.get(ID_KEY)
    else:
        spreadsheetId = result
    log.info("Spreadsheet ID of the file : %s", spreadsheetId)
    return spreadsheetId


def writeGradingDetailsToSheet(credentials, spreadsheetId, assignmentDetailDic, sheetValueList):
    """
    Writes the initial grading data like student information and corressponding assignment assigned into the assignment grading sheet
    :param credentials: Required identity parameter to connect to Google Sheet API service.
    :param spreadsheetId: Unique identifier of the sheet
    :param assignmentDetailDic: Assignment detail parameters
    :param sheetValueList : List of rows to be added
    :return: None
    """
    try:
        number_questions = int(assignmentDetailDic[NO_QUESTIONS])
        number_graders = int(assignmentDetailDic[NO_GRADERS])
        # 71 as we will start from G as first 6 columns are fixed.
        # Twice the number of questions - One for marks and another for justification
        rangeEndIndex = chr(ASCII_G + 2 * number_questions)
        # Since data is going to be multiples values, we need to calculate number of rows too.
        number_rows = len(sheetValueList)
        rangeSheet = SHEET_START_COLUMN + ROW_1 + ":" + rangeEndIndex + str(number_rows)
        requestBody = {RANGE_KEY: rangeSheet, VALUES_KEY: sheetValueList}
        serviceSheet = getSheetService(credentials)
        serviceSheet.spreadsheets().values().update(spreadsheetId=spreadsheetId, range=rangeSheet, body=requestBody,
                                                    valueInputOption=SHEET_VALUE_INPUT_OPTION_RAW).execute()
        log.info("Grading data written to sheet %s ", spreadsheetId)
    except Exception as ex:
        log.error("Failed to write grading data to sheet %s", spreadsheetId)
        log.error(str(ex))


def getStudentData(credentials, courseId):
    """
    Returns the student data dictionary
    :param credentials: Required identity parameter to connect to Google Drive API service.
    :param courseId: Unique identifier of the course
    :return: A dictionary of student data identified by student's user id.
    """
    service = getClassRoomService(credentials)
    studentListResponse = service.courses().students().list(courseId=courseId).execute()
    log.info("Student list response generated for course %s", courseId)
    studentListResponse = studentListResponse.get(STUDENTS_KEY)
    studentData = {}
    for studentInfo in studentListResponse:
        studentData[unicode(studentInfo[USER_ID_KEY])] = studentInfo
    return studentData


def readAssignmentDetails(credentials, driveResourceLinkId, courseId, courseWorkId):
    """
    Fetches the assignment details from the assignment folder in the classroom drive
    :param credentials: Required identity parameter to connect to Google Drive API service.
    :param driveResourceLinkId: Unique identifier of the Drive link to courseWork's drive folder.
    :param courseId: Unique identifier of the course.
    :param courseWorkId: Unique identifier of the courseWork of a given course
    :return: Dictionary with assignment details
    """
    result = findSheet(getDriveService(credentials), driveResourceLinkId,
                       INSTRUCTOR_FORM_FILE_KEY + UNDERSCORE_KEY + courseWorkId)
    assignmentDetails = {}
    if result == None:
        log.info("Unable to retrieve instructorForm details")
        classroomService = getClassRoomService(credentials)
        courseWorkDetails = classroomService.courses().courseWork().get(courseId=courseId, id=courseWorkId).execute()
        if DUE_DATE_KEY in courseWorkDetails:
            courseWorkDueDate = courseWorkDetails[DUE_DATE_KEY]
            date = datetime.date(courseWorkDueDate[YEAR_KEY], courseWorkDueDate[MONTH_KEY], courseWorkDueDate[DAY_KEY])
            time = datetime.time(hour=DEFAULT_HOUR, minute=DEFAULT_MINUTE)
            if DUE_TIME_KEY in courseWorkDetails:
                courseWorkDueTime = courseWorkDetails[DUE_TIME_KEY]
                time = time.replace(hour=courseWorkDueTime[HOURS_KEY], minute=courseWorkDueTime[MINUTES_KEY])
            dt = datetime.datetime.combine(date, time)
            assignmentDeadline = dt.strftime(DATE_FORMAT_KEY)
            assignmentDetails[ASSIGNMENT_DEADLINE_KEY] = assignmentDeadline
        assignmentDetails[ASSIGNMENT_NAME_KEY] = courseWorkDetails[TITLE_KEY]
        if MATERIALS_KEY in courseWorkDetails:
            link = ""
            for material in courseWorkDetails[MATERIALS_KEY]:
                if YOUTUBE_VIDEO_KEY in material:
                    link += material[YOUTUBE_VIDEO_KEY][ALTERNATE_LINK_KEY]
                elif DRIVEFILE_KEY in material:
                    link += material[DRIVEFILE_KEY][DRIVEFILE_KEY][ALTERNATE_LINK_KEY]
                elif LINK_KEY in material:
                    link += material[LINK_KEY][URL_KEY]
                link += ","
            assignmentDetails[ASSIGNMENT_LINK_KEY] = link[:-1]
        return assignmentDetails
    else:
        spreadsheetId = result
    serviceSheet = getSheetService(credentials)
    rangeSheet = SHEET_START_COLUMN + ROW_1 + ":" + SHEET_END_COLUMN + ROW_2
    assignmentReadResponse = serviceSheet.spreadsheets().values().get(spreadsheetId=spreadsheetId,
                                                                      range=rangeSheet).execute()
    valuesList = assignmentReadResponse[VALUES_KEY]
    assignmentDetails = dict(zip(valuesList[0], valuesList[1]))
    return assignmentDetails


def readStudentDataFromSheet(globalAccountCredentials, userProfileId, courseId, driveResourceLink, assignmentDetails):
    """
    Reads student grading information from the assignment distribution sheet.
    :param globalAccountCredentials: Required identity parameter to connect to Google API services.
    :param userProfileId: Unique user google classroom identifier.
    :param courseId: Unique identifier of the course
    :param driveResourceLink: Drive Resource link for the course.
    :param assignmentDetails: Dictionary with assignment details
    :return: List of row values read from the assignment distribution sheet.
    """
    driveResourceFileId = extractFileId(driveResourceLink)
    serviceDrive = getDriveService(globalAccountCredentials)
    result = findSheet(serviceDrive, driveResourceFileId, ASSIGNMENT_DISTRIBUTION_FILE_KEY)
    if result == None:
        log.error("Spreadsheet not found. No grading data available")
        return []
    else:
        spreadsheetId = result
        studentDataDic = getStudentData(globalAccountCredentials, courseId)
        studentDataDic = sortByUserId(studentDataDic)
        index = list(studentDataDic.keys()).index(userProfileId)
        rangeSheet = calculateRange(index, int(assignmentDetails[NO_GRADERS]), int(assignmentDetails[NO_QUESTIONS]),
                                    SHEET_START_COLUMN)
        serviceSheet = getSheetService(globalAccountCredentials)
        gradeReadResponse = serviceSheet.spreadsheets().values().get(spreadsheetId=spreadsheetId,
                                                                     range=rangeSheet).execute()
        valuesList = gradeReadResponse[VALUES_KEY]
        return (index, spreadsheetId, valuesList)


def calculateRange(index, number_graders, number_questions, startColumn):
    """
    Calculates the sheet range to be fetched
    :param index: Index of student to be searched for in the sheet
    :param number_graders: Number of graders
    :param number_questions: Number of questions
    :param startColumn : Start reading from column
    :return: Range sheet For example : A1:B2
    """
    sheetStartRowIndex = (index * number_graders) + 2
    rangeEndIndex = chr(ASCII_G + 2 * number_questions)
    sheetEndRowIndex = (index * number_graders) + 2 + (number_graders - 1)
    rangeSheet = startColumn + str(sheetStartRowIndex) + ":" + rangeEndIndex + str(sheetEndRowIndex)
    log.info("Range of sheet to be read/write : %s", rangeSheet)
    return rangeSheet


def writeGradesToSheet(index, credentials, spreadsheetId, number_graders, number_questions, sheetValueList):
    """
    Writes the updated grades to the sheet
    :param index: Index of the student in the overall student list
    :param credentials: Required identity parameter to connect to Google SHEET API services.
    :param spreadsheetId: Spreadsheet Id of the sheet.
    :param number_graders: Number of grading assignments graded by each student
    :param number_questions: Number of questions per assignment
    :param sheetValueList: List of values to be written to the sheet
    :return: None
    """

    rangeSheet = calculateRange(index, number_graders, number_questions, chr(ASCII_G))

    requestBody = {RANGE_KEY: rangeSheet, VALUES_KEY: sheetValueList}
    serviceSheet = getSheetService(credentials)
    serviceSheet.spreadsheets().values().update(spreadsheetId=spreadsheetId, range=rangeSheet, body=requestBody,
                                                valueInputOption=SHEET_VALUE_INPUT_OPTION_RAW).execute()
    log.info("Grading data written to sheet %s ", spreadsheetId)
