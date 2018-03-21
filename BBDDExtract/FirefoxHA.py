#!/usr/bin/python

# -*- coding: utf-8 -*-
import platform
import sqlite3
import sys
import getpass
import os
from flask import render_template
from flask import Flask, request, redirect, url_for
from werkzeug import secure_filename

###
# Author: Juan Angel Lopez
###

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
    <title>Upload Firefox History Sqlite3 Database</title>
    <h1>Upload new File</h1>
    <form action="" method=post enctype=multipart/form-data>
      <p><input type=file name=file>
         <input type=submit value=Upload>
    </form>
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
    <title>Upload Firefox Cookies Sqlite3 Database</title>
    <h1>Upload new File</h1>
    <form action="" method=post enctype=multipart/form-data>
      <p><input type=file name=file>
         <input type=submit value=Upload>
    </form>
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

#Show result of places query
#Param: Sqlite BD cursor
#Return path: Query result
 
def showPlaces(cursor):
	try:
		result = cursor.execute("""
			SELECT 
			url
			,visit_count
			,hidden
			,datetime((last_visit_date/1000000), 'unixepoch','localtime')			
			FROM moz_places""")
		
		return list(result)
	    
	except sqlite3.OperationalError:
		 return render_template('error.html')
		

#Show result of bookmarks query
#Param: Sqlite BD cursor
#Return path: Query result

def showBookmarks(cursor):
	try:
		result = cursor.execute("""
			SELECT 
			title
			,datetime((dateAdded/1000000), 'unixepoch','localtime')
			FROM moz_bookmarks""")
		
		return list(result)
	    
	except sqlite3.OperationalError:
		 return render_template('error.html')

#Show result of cookies query
#Param: Sqlite BD cursor
#Return path: Query result

def showCookies(cursor):
	try:
		result = cursor.execute("""
			select			
			baseDomain
			,value
			,datetime((expiry/1000000), 'unixepoch','localtime')
			,datetime((lastAccessed/1000000), 'unixepoch','localtime')
			,datetime((creationTime/1000000), 'unixepoch','localtime')
			From moz_cookies
			""")
		
		return list(result)
	    
	except sqlite3.OperationalError:
		 return render_template('error.html')

#History filename path
#Param: filename
#Return path: Rendered HTML template

@app.route('/history/<filename>')
def uploaded_history(filename):
    conection = sqlite3.connect(os.path.join(app.config['UPLOAD_FOLDER'], filename))
    cursor = conection.cursor()
    places = showPlaces(cursor)
    bookmarks = showBookmarks(cursor)
    return render_template('layoutff.html',places=places,bookmarks=bookmarks)

#Cookies filename path
#Param: filename
#Return path: Rendered HTML template

@app.route('/cookies/<filename>')
def uploaded_cookies(filename):
    conection = sqlite3.connect(os.path.join(app.config['UPLOAD_FOLDER'], filename))
    cursor = conection.cursor()
    cookies = showCookies(cursor)
    return render_template('layoutffcookies.html',cookies=cookies)

#Main: Init Flask app
if __name__ == "__main__":
    app.run(debug=True)
