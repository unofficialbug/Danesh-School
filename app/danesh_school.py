from __future__ import print_function
import pickle
import os.path
from googleapiclient.discovery import build
from google_auth_oauthlib.flow import InstalledAppFlow
from google.auth.transport.requests import Request
from google.oauth2.credentials import Credentials

from google.oauth2 import service_account

SCOPES = ['https://www.googleapis.com/auth/spreadsheets.readonly']
SERVICE_ACCOUNT_FILE = 'river-acrobat-332515-6ad92bdf904e.json'

creds = None
creds = service_account.Credentials.from_service_account_file(
        SERVICE_ACCOUNT_FILE, scopes=SCOPES)

# The ID the spreadsheet.
SAMPLE_SPREADSHEET_ID = '1548KUFKJuVU6UF_PYLXKSufrizKCEiABbL6ksbFDr1Q'

service = build('sheets', 'v4', credentials=creds)

    # Call the Sheets API
sheet = service.spreadsheets()
result = sheet.values().get(spreadsheetId=SAMPLE_SPREADSHEET_ID,
                            range='لیست دانش‌آموزان!A1:E26').execute()
values = result.get('values', [])


class Student:
	def __init__(self, class_number, firstname, lastname, studentID, nationalID,scores):
		self.studentID = studentID
		self.nationalID = nationalID
		self.class_number= class_number
		self.firstname = firstname
		self.lastname = lastname
		self.scores = scores

def get_scores(student):
	student.scores = []
	my_spreadsheet = service.spreadsheets().get(spreadsheetId=SAMPLE_SPREADSHEET_ID).execute()
	for sheet in my_spreadsheet['sheets']:
		sheet_range = str(sheet.get('properties').get('title'))+'!A1:C1000'
		sheet_result = service.spreadsheets().values().get(spreadsheetId=SAMPLE_SPREADSHEET_ID,range=sheet_range).execute()
		sheet_values = sheet_result.get('values', [])
		for row in sheet_values:
			if student.firstname == row[0].strip() and student.lastname==row[1].strip():
				if len(row)>2:
					student.scores.append([sheet.get('properties').get('title')[:-4],row[2].strip() ])

student_list = []
def list_of_students():
    for row in values:
    	student_list.append(Student(
    		class_number = row[0].strip(),
    		firstname = row[1].strip(),
            lastname= row[2].strip(),
            studentID = row[3].strip(),
            nationalID =row[4].strip(),
            scores = []
            )
    		)
list_of_students();

def if_student_exists(input_id):
    for x in student_list:
        if x.studentID==input_id:
            return x;
    return None
"""
"""

"""
tikk herre we have made the students list
"""



from flask import (
	Flask,
	flash,
	    g,
    redirect,
    render_template,
    request,
    session,
    url_for
)
		
app = Flask(__name__)
app.secret_key = 'somesecretkeythatonlyishouldknow'

@app.before_request
def before_request():
    g.student = None
    if 'student_id' in session:
    	user = [x for x in student_list if x.studentID == session['student_id']][0]
    	g.student = user

@app.route('/')

@app.route('/',methods=['GET', 'POST'])
def login():
	if request.method =='POST':
		session.pop('student_id', None)
		studentID = request.form['StudentID']
		nationalID= request.form['NationalID']
		student = if_student_exists(studentID)
		if student!= None:
			if student.nationalID == nationalID:
				session['student_id'] = student.studentID
				return redirect(url_for('profile'))
			else:
				return redirect(url_for('/'))

		else:
			return redirect(url_for('/'))

	else:
		return render_template('login.html')


@app.route('/profile')
def profile():
	if not g.student:
		return redirect(url_for('/'))
	get_scores(g.student)
	return render_template('profile.html')

if __name__=='__main__':
	app.run(host='0.0.0.0', port=5000)
