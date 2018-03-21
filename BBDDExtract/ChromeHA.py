#!/usr/bin/python

# -*- coding: utf-8 -*-
from markupsafe import Markup
import simplejson as json
import platform
import sqlite3
import sys
import getpass
import os
from flask import render_template
from flask import Flask, request, redirect, url_for
from werkzeug import secure_filename

##################
# Author: Juan Angel Lopez
####################

UPLOAD_FOLDER = '.'

app = Flask(__name__)
app.config['UPLOAD_FOLDER'] = UPLOAD_FOLDER

sys.setrecursionlimit(2000) 


#UploadHistory path
#Param: Path
#Param: Methods
#Return path: Upload history html


@app.route('/uploadHistory', methods=['GET', 'POST'])
def upload_history():
    if request.method == 'POST':
        file = request.files['file']
        filename = secure_filename(file.filename)
        file.save(os.path.join(app.config['UPLOAD_FOLDER'], filename))
        return redirect(url_for('uploaded_history',
                                    filename=filename))
    return '''
    <!doctype html>
    <center>
    <title>Upload Chrome History Sqlite3 Database</title>
    <h1>>Upload Chrome History Sqlite3 Database</h1>
    <form action="" method=post enctype=multipart/form-data>
         <input type=file name=file>
         <input type=submit value=Upload>
    </form>
    </center>
    '''

#UploadCookies path
#Param: Path
#Param: Methods
#Return path: Upload cookies html    
 
@app.route('/uploadCookies', methods=['GET', 'POST'])
def upload_cookies():
    if request.method == 'POST':
        file = request.files['file']
        filename = secure_filename(file.filename)
        file.save(os.path.join(app.config['UPLOAD_FOLDER'], filename))
        return redirect(url_for('uploaded_cookies',
                                    filename=filename))
    return '''
    <!doctype html>
    <center>
    <title>Upload Chrome Cookies Sqlite3 Database</title>
    <h1>>Upload Chrome Cookies Sqlite3 Database</h1>
    <form action="" method=post enctype=multipart/form-data>
      <p><input type=file name=file>
         <input type=submit value=Upload>
    </form>
    </center>
    '''

#Main path
#Param: Path
#Return path: Main html

@app.route('/')
def upload_file():
    return '''
    <!doctype html>
    <h1>Select file type to upload</h1>
    <a href="http://localhost:5000/uploadHistory">Upload History Database</a>
    <a href="http://localhost:5000/uploadCookies">Upload Cookies Database</a>
    '''

#Show result of visits query
#Param: Sqlite BD cursor
#Return path: Query result

def showVisits(cursor):
	try:
		cursor.execute("""
		SELECT urls.url
		,title
		,datetime(((visits.visit_time/1000000)-11644473600), "unixepoch")
		,datetime(visit_duration) 
		FROM urls INNER JOIN visits ON urls.id = visits.url ORDER BY title""")
		
		result = [[item.replace("""u'""","'").encode('ascii','ignore') for item in results] for results in cursor.fetchall()]
			
		return result


	except sqlite3.OperationalError:
		 return render_template('error.html')

#Show result of downloads query
#Param: Sqlite BD cursor
#Return path: Query result

def showDownloads(cursor):
  
		try:
			result = cursor.execute("""
			SELECT
			current_path
			,datetime(((start_time/1000000)-11644473600), "unixepoch","localtime")
			,received_bytes
			,state
			,opened
			,referrer
			,mime_type
			,datetime(((end_time/1000000)-11644473600), "unixepoch","localtime")
			FROM downloads""")
			
			return list(result)
		except sqlite3.OperationalError:
			 return render_template('error.html')

	
#Show result of urls query
#Param: Sqlite BD cursor
#Return path: Query result	

def showUrls(cursor):
		try:
			cursor.execute("""
			SELECT
			url
			,title
			,datetime(((last_visit_time/1000000)-11644473600), "unixepoch")
			FROM urls""")

			result = [[item.replace("""u'""","'").encode('ascii','ignore') for item in results] for results in cursor.fetchall()]
			
			return result				
			
		except sqlite3.OperationalError:
			 return render_template('error.html')

#Show result of cookies query
#Param: Sqlite BD cursor
#Return path: Query result		

def showCookies(cursor):
		try:
			cursor.execute("""
			SELECT
			datetime(((creation_utc/1000000)-11644473600), "unixepoch")
			,host_key
			,path
			,datetime(((expires_utc/1000000)-11644473600), "unixepoch")
			,datetime(((last_access_utc/1000000)-11644473600), "unixepoch")
			FROM cookies""")
			
			result = [[item.replace("""u'""","'").encode('ascii','ignore') for item in results] for results in cursor.fetchall()]
						
			return result				
			
		except sqlite3.OperationalError:
			 return render_template('error.html')

#Returns JSON in Timeline JS format with the downloads
#Param: DB Filename
#Return path: Downloads JSON	

@app.route('/_getDownloadsJson/<filename>')
def _getDownloadsJson(filename):
    try:
      conection = sqlite3.connect(os.path.join(app.config['UPLOAD_FOLDER'], filename))
      cursor = conection.cursor()
      downloads = showDownloads(cursor)


      json = """
      {
    	"title": {
        	"text": {
         	 "headline": "Downloads",
         	 "text": "Chrome downloads timeline"
         	 }
   	  },	
	"""
      
      events = """ "events":
      [
      """

      for download in downloads[0:len(downloads)-1]:
      		events = events + """{
      			"start_date": {
      				"month":\""""+str(download[1][5:7])+"""\",
      				"day": \""""+str(download[1][8:10])+"""\",
      				"year": \""""+str(download[1][0:4])+"""\"
      			},
      				 "text": {
        	  "headline": "Download:"""+download[5]+"""\",
        	  "text": \""""+download[5]+"""\"
      	  }
    	  },
		"""

      events = events + """{
      			"start_date": {
      				"month": \""""+str(downloads[len(downloads)-1][1][5:7])+"""\",
      				"day": \""""+str(downloads[len(downloads)-1][1][8:10])+"""\",
      				"year": \""""+str(downloads[len(downloads)-1][1][0:4])+"""\"
      			},
      				 "text": {
        	  "headline": "last",
        	  "text": \""""+str(downloads[len(downloads)-1][5])+"""\"
      	  }
    	  }
		"""

      events = events + """ ]
	  }"""

      json = json + events
		
      return json
    except sqlite3.Error:
      return render_template('error.html')



#Returns JSON in Timeline JS format with the visits
#Param: DB Filename
#Return path: Visits JSON	

@app.route('/_getVisitJson/<filename>')
def _getVisitJson(filename):
    try:
      conection = sqlite3.connect(os.path.join(app.config['UPLOAD_FOLDER'], filename))
      cursor = conection.cursor()
      visits = showVisits(cursor)

      json = """
      {
    	"title": {
        	"text": {
         	 "headline": "Visits",
         	 "text": "Chrome visit timeline"
         	 }
   	  },	
	"""
      
      events = """ "events":
      [
      """

      for visit in visits[0:len(visits)-1]:
      		events = events + """{
      			"start_date": {
      				"month":\""""+str(visit[2][5:7])+"""\",
      				"day": \""""+str(visit[2][8:10])+"""\",
      				"year": \""""+str(visit[2][0:4])+"""\"
      			},
      				 "text": {
        	  "headline": "Visit:"""+visit[0]+"""\",
        	  "text": \""""+visit[0]+"""\"
      	  }
    	  },
		"""

      events = events + """{
      			"start_date": {
      				"month": \""""+str(visits[len(visits)-1][2][5:7])+"""\",
      				"day": \""""+str(visits[len(visits)-1][2][8:10])+"""\",
      				"year": \""""+str(visits[len(visits)-1][2][0:4])+"""\"
      			},
      				 "text": {
        	  "headline": "last",
        	  "text": \""""+str(visits[len(visits)-1][0])+"""\"
      	  }
    	  }
		"""

      events = events + """ ]
	  }"""

      json = json + events
		
      return json
    except sqlite3.Error:
      return render_template('error.html')


#History filename path
#Param: filename
#Return path: Rendered HTML template

@app.route('/history/<filename>')
def uploaded_history(filename):
    try:
      conection = sqlite3.connect(os.path.join(app.config['UPLOAD_FOLDER'], filename))
      cursor = conection.cursor()
      visits = showVisits(cursor)
      downloads = showDownloads(cursor)
      urls = showUrls(cursor)

     
      return render_template('layout.html',visits=visits,downloads=downloads,urls=urls)
    except sqlite3.Error:
      return render_template('error.html')

#Returns JSON in Timeline JS format with the cookies
#Param: DB Filename
#Return path: Visits JSON	

@app.route('/_getCookiesJson/<filename>')
def _getCookiesJson(filename):
    try:
      conection = sqlite3.connect(os.path.join(app.config['UPLOAD_FOLDER'], filename))
      cursor = conection.cursor()
      cookies = showCookies(cursor)
      json = """
      {
    	"title": {
        	"text": {
         	 "headline": "Cookies",
         	 "text": "Chrome cookies timeline"
         	 }
   	  },	
	"""
      
      events = """ "events":
      [
      """

      for cookie in cookies[0:len(cookies)-1]:		
      		events = events + """{
      			"start_date": {
      				"month":\""""+str(cookie[0][5:7])+"""\",
      				"day": \""""+str(cookie[0][8:10])+"""\",
      				"year": \""""+str(cookie[0][0:4])+"""\"
      			},
      				 "text": {
        	  "headline": "Cookie:"""+cookie[0]+"""\",
        	  "text": \""""+cookie[0]+"""\"
      	  }
    	  },
		"""

      events = events + """{
      			"start_date": {
      				"month": \""""+str(cookies[len(cookies)-1][0][5:7])+"""\",
      				"day": \""""+str(cookies[len(cookies)-1][0][8:10])+"""\",
      				"year": \""""+str(cookies[len(cookies)-1][0][0:4])+"""\"
      			},
      				 "text": {
        	  "headline": "last",
        	  "text": \""""+str(cookies[len(cookies)-1][1])+"""\"
      	  }
    	  }
		"""

      events = events + """ ]
	  }"""

      json = json + events
		
      return json
    except sqlite3.Error:
      return render_template('error.html')



#Cookies filename path
#Param: filename
#Return path: Rendered HTML template

@app.route('/cookies/<filename>')
def uploaded_cookies(filename):
    try:
      conection = sqlite3.connect(os.path.join(app.config['UPLOAD_FOLDER'], filename))
      cursor = conection.cursor()
      cookies = showCookies(cursor)
      return render_template('layoutcookies.html',cookies=cookies)
    except sqlite3.Error:
      return render_template('error.html')




#Main: Init Flask app
if __name__ == "__main__":
    app.run(debug=True)
