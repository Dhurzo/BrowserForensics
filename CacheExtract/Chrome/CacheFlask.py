#!/usr/bin/python

# -*- coding: utf-8 -*-
import platform
import sqlite3
import sys
import getpass
import os
import chromagnonCache
from flask import render_template
from flask import Flask, request, redirect, url_for
from werkzeug import secure_filename
##################
# Author: Juan Angel Lopez
####################
sys.path.insert(0, './chromagnon')
import cacheParse

UPLOAD_FOLDER = './Cache'

app = Flask(__name__)
app.config.from_object(__name__)
app.config['UPLOAD_FOLDER'] = UPLOAD_FOLDER

sys.setrecursionlimit(2000) 

#Main path
#Param: Path
#Return path: Main html
@app.route('/', methods=['GET', 'POST'])
def upload_history():
    if request.method == 'POST' and 'file' in request.files:
	for upload in request.files.getlist("file"):
	  upload.save(os.path.join(app.config['UPLOAD_FOLDER'], upload.filename))
	return redirect(url_for('uploaded_cache'))       
    return render_template('upload.html')


#Cache path: Parse Chrome cache and generate report
#Return path:Rendered HTML render_template

@app.route('/cache')
def uploaded_cache():
    try:
      cache = cacheParse.parse("./Cache")
      index = 0
      for entrance in cache: 
		 aux = str(entrance)
		 entrance = aux[0:aux.index('Creation Time')] + '''<br/>''' + aux[aux.index('Creation Time'):aux.index('Key:')] + '''<br/>''' +aux[aux.index('Key:'):]
		 cache[index] = entrance
		 index = index + 1
		 print index
      return render_template('layout.html',cache=cache)
    except: 
		print "Unexpected error:", sys.exc_info()[0]
		return render_template('error.html')

#Main: Init Flask app
if __name__ == "__main__":
  app.debug = True
  app.run()
