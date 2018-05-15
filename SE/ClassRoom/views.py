from django.shortcuts import redirect
from django.contrib.auth.decorators import login_required
from django.shortcuts import render
from forms import *
from Models import *
from service import getClassRoomService
from distribution import process, storeAssignmentDetails
from studentUtility import fetchStudentGradingData, updateStudentAssignmentGradeData
from instructorUtility import createAssignment, updateCourseWorkDeadline
from report import createFinalReport

log = getLogger("ClassRoom")


def showCourseList(request):
    """Renders courseList.html with courses list for the user"""
    results = getClassRoomService(request.session[CREDENTIALS_KEY]).courses().list().execute()
    courses = results.get('courses', [])
    form = CourseListForm(courses)
    return render(request, 'CourseList.html', {"form": form})


def showAssignmentsList(request):
    """Renders CourseWorkList.html with assignments list for the selected course by the user"""
    result = getClassRoomService(request.session[CREDENTIALS_KEY]).courses().courseWork().list(
        courseId=request.GET.get(COURSE_ID_KEY)).execute()
    courseWorks = result.get('courseWork', [])
    if request.GET.get(COURSE_NAME_KEY):
        request.session[COURSE_NAME_KEY] = request.GET.get(COURSE_NAME_KEY)
        request.session[COURSE_ID_KEY] = request.GET.get(COURSE_ID_KEY)
        request.session[ASSIGNMENT_NAME_KEY] = ""
        request.session[ASSIGNMENT_ID_KEY] = ""
    form = CourseWorkForm(courseWorks, request.session[COURSE_NAME_KEY], request.session[COURSE_ID_KEY],
                          request.session[CREDENTIALS_KEY])
    return render(request, 'CourseWorkList.html', {"form": form})


def showAssignmentOptions(request, success):
    """If instructor, Renders InstructorForm.html to allow edit/create assignment details for the selected assignment.
    If Student, Renders StudentPage.html to show list of distributed assignments to grade.
    Displays alert when fetching data failed."""
    if request.GET.get(ASSIGNMENT_NAME_KEY):
        request.session[ASSIGNMENT_NAME_KEY] = request.GET.get(ASSIGNMENT_NAME_KEY)
        request.session[ASSIGNMENT_ID_KEY] = request.GET.get(ASSIGNMENT_ID_KEY)
    if isTeacher(request.session[CREDENTIALS_KEY], request.session[COURSE_ID_KEY]):
        form = AssignmentDetailsForm(request.session[COURSE_NAME_KEY], request.session[COURSE_ID_KEY],
                                     request.session[ASSIGNMENT_NAME_KEY])
        try:
            if success != NEW_ASSIGNMENT_OPTION:
                form.assignmentDetails = getAssignmentDetails(request.session[COURSE_ID_KEY],
                                                              request.session[ASSIGNMENT_ID_KEY])
        except Exception as e:
            log.error("Unable to fetch Data", str(e))
            success = OPERATION_FAILED_FETCH
        return render(request, 'InstructorForm.html', {"form": form, "isSuccess": success})
    else:  # FIXME: need UserId
        log.info("Showing Student form to {} for assignment {}".format("", request.session[ASSIGNMENT_NAME_KEY]))
        try:
            data = fetchStudentGradingData(request.session[CREDENTIALS_KEY], request.session[COURSE_ID_KEY],
                                           request.session[ASSIGNMENT_ID_KEY])
            request.session[NO_GRADERS] = data[NO_GRADERS]
            request.session[NO_QUESTIONS] = data[NO_QUESTIONS]
            request.session[GRADING_DATA] = data[GRADING_DATA]
            request.session[STUDENT_INDEX] = data[STUDENT_INDEX]
            request.session[SHEET_ID_KEY] = data[SHEET_ID_KEY]
        except Exception as e:
            log.error("Unable to fetch distributed assignments", str(e))
            request.session[GRADING_DATA] = {}
            success = OPERATION_FAILED_FETCH
        form = StudentAssignmentForm(request.session[COURSE_NAME_KEY], request.session[COURSE_ID_KEY],
                                     request.session[ASSIGNMENT_NAME_KEY], request.session[GRADING_DATA].keys())
        return render(request, 'StudentPage.html', {"form": form, "isSuccess": success})


def postAssignmentDetails(request):
    """Allows instructor to store assignment details."""
    try:
        details = formatAssignmentDetails(request.session[CREDENTIALS_KEY], request.POST,
                                          request.session[COURSE_ID_KEY])
        if request.session[ASSIGNMENT_ID_KEY] == "":
            request.session[ASSIGNMENT_ID_KEY] = createAssignment(request.session[CREDENTIALS_KEY],
                                                                  request.session[COURSE_ID_KEY], details)
            storeAssignmentDetails(request.session[CREDENTIALS_KEY], request.session[COURSE_ID_KEY],
                                   request.session[ASSIGNMENT_ID_KEY], details)
        else:
            storeAssignmentDetails(request.session[CREDENTIALS_KEY], request.session[COURSE_ID_KEY],
                                   request.session[ASSIGNMENT_ID_KEY], details)
            updateCourseWorkDeadline(request.session[CREDENTIALS_KEY], request.session[COURSE_ID_KEY],
                                     request.session[COURSE_NAME_KEY],
                                     request.session[ASSIGNMENT_ID_KEY], details)
            # TODO: Process function needs to be called by scheduler after assignment submission deadline. Uncommenting this method would assume that else part executes after assignment submission deadline
            # process(request.session[CREDENTIALS_KEY], details, request.session[COURSE_ID_KEY],
            #         request.session[COURSE_NAME_KEY],
            #         request.session[ASSIGNMENT_ID_KEY], request.session[ASSIGNMENT_NAME_KEY])
        return redirect('showAssignment', success=OPERATION_SUCCESS)
    except Exception as e:
        log.error(str(e))
        return redirect('showAssignment', success=OPERATION_FAILED)


def gradeAssignment(request):
    """Allows student to grade assignment.
    Allows both POST(Store graded details) and GET(Fetch assignment to be graded)"""
    if request.method == 'POST':
        try:
            log.info("Grade details for assignment - " + request.POST.get("assId"))
            details = formatGradeDetails(request.POST, request.session[NO_QUESTIONS])
            request.session[GRADING_DATA] = updateGradingData(details, request.session[GRADING_DATA],
                                                              request.POST.get("assId"))
            updateStudentAssignmentGradeData(request.session[STUDENT_INDEX], int(request.session[NO_GRADERS]),
                                             int(request.session[NO_QUESTIONS]), request.session[SHEET_ID_KEY],
                                             request.session[GRADING_DATA])
            return render(request, 'NotificationsPage.html', {"isSuccess": OPERATION_SUCCESS})
        except Exception:
            return render(request, 'NotificationsPage.html', {"isSuccess": OPERATION_FAILED})
    index = request.GET.get("index")
    form = GradeAssignmentForm(request.session[ASSIGNMENT_NAME_KEY], index, request.session[GRADING_DATA],
                               request.session[NO_QUESTIONS])
    return render(request, 'GradeAssignment.html', {"form": form})


def generateReport(request):
    # TODO: Unable to update the grades to the classroom.
    link = createFinalReport(request.session[CREDENTIALS_KEY], request.session[COURSE_ID_KEY],
                             request.session[ASSIGNMENT_ID_KEY], True, False)
    return render(request, 'ReportLink.html', {"link": link})


def about(request):
    """webpage related to "how the peer grading work"""
    return render(request, 'about.html')


@login_required
def Home(request):
    return redirect('courses/')
