from PeerReview.Logger import getLogger
from service import getClassRoomService, getDriveService, getSheetService
from keyConstants import *
from sheetUtility import findSheet, createSheet, extractFileId, readAssignmentDetails
from distribution import getStudentData
from instructorUtility import getGradeFormsFolderId

log = getLogger("report")


def createFinalReport(credentials, courseId, courseWorkId, variationFlag, leastValueNotAllowedFlag):
    """
    Creates the report for the final combined assignment and peer grading grades for all the student
    :param credentials: Required identity parameter to connect to Google Mail API service.
    :param courseId: Unique Identifier of the course.
    :param courseWorkId: Unique Identifier of the courseWork of the course.
    :param variationFlag: Flag to allow variation
    :param leastValueNotAllowedFlag: Flag to remove least value while calculating average marks
    :return: Google doc link to the Report spreadsheet.
    """
    try:
        serviceSheet = getSheetService(credentials)
        driveResourceLinkId = getGradeFormsFolderId(credentials, courseId)
        assignmentDetails = readAssignmentDetails(credentials, driveResourceLinkId, courseId, courseWorkId)
        (spreadsheetId, numPeerGraders, numQuestion, assignmentPercentage, courseWorkDriveResourceLinkId, numStudent,
         studentData, total_score) = getReportParameter(credentials, courseId, courseWorkId, assignmentDetails)
        sheetRows = readDataFromSheet(serviceSheet, numQuestion, numPeerGraders, numStudent, spreadsheetId)
        (studentDict, peerGradersDict) = getDataIntoDictionaries(sheetRows, numQuestion, numPeerGraders)
        (studentDict, peerGradersDict) = processData(studentDict, peerGradersDict, numQuestion, variationFlag,
                                                     leastValueNotAllowedFlag, total_score)
        valuesList = generateSheetValueList(studentDict, peerGradersDict, studentData, numQuestion, numPeerGraders,
                                            assignmentPercentage, leastValueNotAllowedFlag)
        reportSpreadSheetId = writeReportToSheet(credentials, serviceSheet, courseWorkDriveResourceLinkId, valuesList)
        reportSpreadSheetDriveLink = fetchSpreadSheetLink(serviceSheet, reportSpreadSheetId)
        log.info("Report Drive Link : %s", reportSpreadSheetDriveLink)
        return reportSpreadSheetDriveLink
    except Exception as e:
        log.error("Error while reporting the final sheet : %s", str(e))


def getReportParameter(credentials, courseId, courseWorkId, assignmentDetails):
    """
    Get all the parameters needed to process grading data and generate report
    :param credentials: Required identity parameter to connect to Google Mail API service.
    :param courseId: Unique Identifier of the course.
    :param courseWorkId: Unique Identifier of the courseWork of the course.
    :param assignmentDetails: Dictionary of the coursework details
    :return: A tuple of all the parameters : spreadsheetId, number of peer graders, number of questions, assignment marks weightage, courseWork Drive Resource Link Id, number of student,
            student data and total score
    """
    classroomService = getClassRoomService(credentials)
    courseWorkGetResult = classroomService.courses().courseWork().get(courseId=courseId, id=courseWorkId).execute()
    courseWorkDriveResourceLink = courseWorkGetResult[ASSIGNMENT_KEY][STUDENT_WORK_FOLDER_KEY][
        ALTERNATE_DRIVEFILE_LINK_KEY]
    courseWorkDriveResourceLinkId = extractFileId(courseWorkDriveResourceLink)
    driveService = getDriveService(credentials)
    spreadsheetId = findSheet(driveService, courseWorkDriveResourceLinkId, ASSIGNMENT_DISTRIBUTION_FILE_KEY)
    numPeerGraders = int(assignmentDetails[NO_GRADERS])
    numQuestion = int(assignmentDetails[NO_QUESTIONS])
    assignmentPercentage = float(assignmentDetails[ASSIGNMENT_PERCENTAGE_KEY])
    total_score = 0
    for i in range(0, numQuestion):
        key = 'q-' + str(i + 1)
        total_score += int(assignmentDetails[key])
    studentData = getStudentData(credentials, courseId)
    numStudent = len(studentData)
    log.info("Parameters for report generation are ready for course %s and courseWork %s : ", courseId, courseWorkId)
    log.info(spreadsheetId, numPeerGraders, numQuestion, assignmentPercentage, courseWorkDriveResourceLinkId,
             numStudent,
             studentData, total_score)
    return (spreadsheetId, numPeerGraders, numQuestion, assignmentPercentage, courseWorkDriveResourceLinkId, numStudent,
            studentData, total_score)


def readDataFromSheet(serviceSheet, numQuestion, numPeerGraders, numStudent, spreadsheetId):
    """
    Reads the data from the assignmentDistribution sheet which contains all the peer grades.
    :param serviceSheet: Parameter to access Google Spreadsheet service.
    :param numQuestion: Total number of questions in the assignment.
    :param numPeerGraders: Number of peer graders per assignment.
    :param numStudent: Total number of student in the course.
    :param spreadsheetId: Unique identifier of the assignmentDistribution spreadsheet.
    :return: A list containing all the rows of assignmentDistribution sheet.
    """
    # Get all data in the spreadsheet
    numCol = ASCII_G + numQuestion - 1
    numRow = numStudent * numPeerGraders + 1
    # Define range from the information above
    rangeLetter = SHEET_START_COLUMN + ROW_1 + ":" + chr(numCol) + str(numRow)
    # Get data from sheet
    dataFromSheet = serviceSheet.spreadsheets().values().get(spreadsheetId=spreadsheetId, range=rangeLetter).execute()
    sheetRows = dataFromSheet["values"]
    log.info("Values successfully read from the %s sheet", ASSIGNMENT_DISTRIBUTION_FILE_KEY)
    return sheetRows


def getDataIntoDictionaries(sheetRows, numQuestion, numPeerGraders):
    """
    Converts the sheet data into 2 dictionaries : 1. Student Dictionary - containing details of the student whose assignment is graded, 2. Peer Grader dictionary - containing details of the peer graders.
    :param sheetRows: A list containing all the rows of assignmentDistribution sheet.
    :param numQuestion: Number of questions in the assignment.
    :param numPeerGraders: Number of peer graders per assignment.
    :return: A tuple of studentDict and peerGradersDict
    """
    peerGradersDict = {}
    studentDict = {}
    for rowIndex in range(1, len(sheetRows)):
        currentRow = sheetRows[rowIndex]
        if len(currentRow) > MARKS_START_SHEET_INDEX:
            if currentRow[SHEET_GRADING_ASSIGNMENT_STUDENT_ID] in peerGradersDict:
                dict = peerGradersDict[currentRow[SHEET_GRADING_ASSIGNMENT_STUDENT_ID]]
                dict[GRADED_COUNT] += numQuestion
            else:
                dict = {}
                dict[GRADED_COUNT] = numQuestion
                dict[GRADE_DEVIATED_COUNT] = 0
                dict[GRADE_TOTAL_COUNT] = numQuestion * numPeerGraders
            peerGradersDict[currentRow[SHEET_GRADING_ASSIGNMENT_STUDENT_ID]] = dict
            if currentRow[SHEET_USERID_INDEX] in studentDict:
                dict = studentDict[currentRow[SHEET_USERID_INDEX]]
                graderList = dict[GRADER_ID_LIST]
                graderList.append(currentRow[SHEET_GRADING_ASSIGNMENT_STUDENT_ID])
                dict[GRADER_ID_LIST] = graderList
                for i in range(0, len(currentRow) - MARKS_START_SHEET_INDEX):
                    key = 'q-' + str(i + 1)
                    lst = dict[key]
                    lst.append(int(currentRow[MARKS_START_SHEET_INDEX + i]))
                    dict[key] = lst
            else:
                dict = {}
                dict[GRADER_ID_LIST] = [currentRow[SHEET_GRADING_ASSIGNMENT_STUDENT_ID]]
                for i in range(0, len(currentRow) - MARKS_START_SHEET_INDEX):
                    key = 'q-' + str(i + 1)
                    dict[key] = [int(currentRow[MARKS_START_SHEET_INDEX + i])]
            studentDict[currentRow[SHEET_USERID_INDEX]] = dict
    log.info("Data from sheet successfully converted to Dictionaries.")
    return (studentDict, peerGradersDict)


def processData(studentDict, peerGradersDict, numQuestion, variationFlag, leastValueNotAllowedFlag, total_score):
    """
    Processes Student dictionary and peer grader dictionary to calculate assignment score and peer grading score.
    :param studentDict: Student dictionary containing details of the student whose assignment is graded.
    :param peerGradersDict: Peer grader dictionary containing details of the peer graders.
    :param numQuestion: Number of questions in the assignment.
    :param variationFlag: Flag to allow variation.
    :param leastValueNotAllowedFlag: Flag to remove least value while calculating average marks.
    :param total_score: Total score for the assignment.
    :return: A tuple of updated studentDict and peerGradersDict.
    """
    for uid in studentDict.keys():
        dict = studentDict[uid]
        score = 0
        for i in range(0, numQuestion):
            key = 'q-' + str(i + 1)
            qList = dict[key]
            mean = float(sum(qList)) / len(qList)
            if variationFlag:
                variationAllowed = float(mean * SCORE_VARIANCE_PERCENTAGE / 100)
                subtractmean = [0 if abs(x - mean) <= variationAllowed else 1 for x in qList]
                for j in range(0, len(qList)):
                    if subtractmean[j] == 1:
                        peerGradersDict[studentDict[uid][GRADER_ID_LIST][j]][GRADE_DEVIATED_COUNT] += 1
            leastValue = min(s for s in qList)
            sumQ = sum(qList) - leastValue
            leastValueRemovedMean = float(sumQ) / (len(qList) - 1)
            dict[key + GRADE_MEAN] = mean
            dict[key + GRADE_MEAN_WITH_LEAST_VALUE_REMOVED] = leastValueRemovedMean
            if leastValueNotAllowedFlag:
                score += leastValueRemovedMean
            else:
                score += mean
        dict[GRADE_SCORE] = float(score) * 100 / total_score
        studentDict[uid] = dict
    log.info("Processing on student dictionary and peer grader dictionary is successful.")
    return (studentDict, peerGradersDict)


def generateSheetValueList(studentDict, peerGradersDict, studentData, numQuestion, numPeerGraders, assignmentPercentage,
                           leastValueNotAllowedFlag):
    """
    Generates the sheet values list to be inserted into the report sheet.
    :param studentDict: Student dictionary containing details of the student whose assignment is graded.
    :param peerGradersDict: Peer grader dictionary containing details of the peer graders.
    :param studentData: Student data dictionary containing details of each student like Id, email Id, full name etc.
    :param numQuestion: Number of question in the assignment.
    :param numPeerGraders: Number of peer graders per assignment.
    :param assignmentPercentage: Percentage of assignment score in the final score
    :param leastValueNotAllowedFlag: Flag to remove least value while calculating average marks.
    :return: A list of list of values to be inserted into the report sheet.
    """
    valuesList = []
    header = [USER_ID_KEY, NAME_KEY, EMAIL_ADDRESS_KEY]
    for i in range(0, numQuestion):
        key = 'q-' + str(i + 1)
        header.append(key)
    header.append(ASSIGNMENT_SCORE_KEY)
    header.append(PEER_GRADING_SCORE_KEY)
    header.append(TOTAL_SCORE_KEY)
    header.append(GRADING_DEVIATION)
    valuesList.append(header)
    for uid in studentData.keys():
        if uid in studentDict:
            deviationFlag = 'N'
            peerGradeDetail = peerGradersDict[uid]
            deviationCount = numQuestion * numPeerGraders * float(PEER_GRADING_VARIANCE_PERCENTAGE) / 100
            if peerGradeDetail[GRADE_DEVIATED_COUNT] > deviationCount:
                deviationFlag = 'Y'
            peerGradingScore = float(peerGradeDetail[GRADED_COUNT]) * 100 / peerGradeDetail[GRADE_TOTAL_COUNT]
            value = []
            value.append(uid)
            value.append(studentData[uid][PROFILE_KEY][NAME_KEY][FULL_NAME_KEY])
            value.append(studentData[uid][PROFILE_KEY][EMAIL_ADDRESS_KEY])
            for i in range(0, numQuestion):
                key = 'q-' + str(i + 1)
                if leastValueNotAllowedFlag:
                    value.append(studentDict[uid][key + GRADE_MEAN])
                else:
                    value.append(studentDict[uid][key + GRADE_MEAN_WITH_LEAST_VALUE_REMOVED])
            value.append(studentDict[uid][GRADE_SCORE])
            value.append(peerGradingScore)
            peerPlusAssignmentGrade = (float(studentDict[uid][GRADE_SCORE]) * assignmentPercentage + float(
                peerGradingScore) * (100 - assignmentPercentage)) / 100
            value.append(peerPlusAssignmentGrade)
            value.append(deviationFlag)
            valuesList.append(value)
        else:
            value = []
            value.append(uid)
            value.append(studentData[uid][PROFILE_KEY][NAME_KEY][FULL_NAME_KEY])
            value.append(studentData[uid][PROFILE_KEY][EMAIL_ADDRESS_KEY])
            value += (len(header) - 3) * [0]
            valuesList.append(value)
    return valuesList


def writeReportToSheet(credentials, serviceSheet, courseWorkDriveResourceLinkId, valuesList):
    """
    Creates/updates the report sheet with value list.
    :param credentials: Required identity parameter to connect to Google Mail API service.
    :param serviceSheet: Parameter to access Google Spreadsheet service.
    :param courseWorkDriveResourceLinkId: Course Work drive resource link Id.
    :param valuesList: A list of list of values to be inserted into the report sheet.
    :return: unique identifier of the report spreadsheet.
    """
    reportSpreadsheetId = createSheet(credentials, courseWorkDriveResourceLinkId, REPORT_SHEET_NAME_KEY)
    rangeSheet = SHEET_START_COLUMN + ROW_1 + ":" + chr(ASCII_A + len(valuesList[0]) - 1) + str(len(valuesList))
    requestBody = {RANGE_KEY: rangeSheet, VALUES_KEY: valuesList}
    serviceSheet.spreadsheets().values().update(spreadsheetId=reportSpreadsheetId, range=rangeSheet,
                                                body=requestBody,
                                                valueInputOption=SHEET_VALUE_INPUT_OPTION_RAW).execute()
    log.info("Report grading data written to sheet %s ", reportSpreadsheetId)
    return reportSpreadsheetId


def fetchSpreadSheetLink(serviceSheet, spreadsheetId):
    """
    Fetches the spreadsheet url from the spread sheet id.
    :param serviceSheet: Parameter to access Google Spreadsheet service.
    :param spreadsheetId: Unique identifier of the report spreadsheet.
    :return: The Google DOC link to the report spreadsheet.
    """
    sheetDetails = serviceSheet.spreadsheets().get(spreadsheetId=spreadsheetId).execute()
    spreadSheetLink = sheetDetails[SPREADSHEET_URL_KEY]
    return spreadSheetLink
