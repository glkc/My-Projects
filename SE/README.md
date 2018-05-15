PeerReview Module for Classroom Documentation!
==============================================

This Module allows a functionality to provide peer review for the assignments. 
It uses OAuth, Sheets, Drive, Classroom. 

Features:
---------
* Uses OAuth (By google) for authentication
* Allows Instructor to create assignments for a course in Classroom
* Allows the assignments to be automatically distributed (in random order) for grading, after the deadline
* Allows student to grade the assignments
* Stores Details provided by User to respective sheets

Prerequisite:
-------------
Supported Versions:
```
Python - 2.7
```
Install the below libraries
```
pip install django-bootstrap-ui
pip install --upgrade google-api-python-client
```
This module uses a global account to access and edit content. Create a credentials for it using 
```
python quickstart.py
```
Quick start:
------------
```
python manage.py runserver <IP>
```

