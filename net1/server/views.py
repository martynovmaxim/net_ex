from functools import wraps
from flask import render_template, url_for
from flask import request, redirect, Response, make_response
from server import app, redis_store as db
from server.passutils import check_password, generate_salt, create_password
import os
import subprocess

def printsmth(x):
	user = { 'nickname': x }
	return render_template("index.html",
		title = 'Home',
		user = user)

def check_auth(username, password):
	hpass = db.get(username)
	if hpass is None:
		return False
	hpass = hpass.decode('utf-8')
	if check_password(hpass, password):
		return True
	return False

def authenticate():
	return redirect(url_for('login'))

def login_required(func):
	@wraps(func)
	def decorated_function(*args, **kwargs):
		sessionid = request.cookies.get('sessionid', None)
		if sessionid is None:
			return authenticate()
		return func(*args, **kwargs)
	return decorated_function

@app.route('/login', methods = ['GET', 'POST'])
def login():
	if request.method == 'POST':
		data = request.form
		hpass = db.get(data.get('username'))
		if hpass is not None:
			hpass = hpass.decode('utf-8')
		#hpass = 'pbkdf2$10000$3937695218abe02362ab796ee2f4233255117a6960af0a1a28294b38e05716e7$123'
		if check_auth(data.get('username'), data.get('password')):
			sessionid = generate_salt()
			#sessionid = "sessionid"
			db.set(sessionid , data.get('username'))
			response = Response()
			response.set_cookie('sessionid', sessionid)
			return response
		else:
			return authenticate()
	if request.method == "GET":
		return render_template("login.html")

@app.route('/registration', methods = ['GET', 'POST'])
def registration():
	if request.method == 'POST':
		data = request.form
		hpass = create_password(data.get('password'), 'sha256')
		db.set(data.get('username'), hpass)
		return printsmth(hpass)
	if request.method == "GET":
		return render_template("registration.html")


@app.route('/logout')
@login_required
def logout():
	sessionid = request.cookies.get('sessionid', None)
	if sessionid is not None:
		db.delete(sessionid)
		response = Response()
		response.set_cookie('sessionid', expires = 0)
		return response
	return Response()


@app.route('/db', methods = ['GET', 'POST'])
@login_required
def db_request():
	if request.method == "GET":
		return render_template('db_page.html')
	if request.method == "POST":
		data = request.form
		if db.get(data.get('request')) is not None:
			response = make_response(str(db.get(data.get('request')).decode('utf-8')))
			return response
		else:
			return Response()

@app.route('/calc')
@login_required
def calculate():
	n = 32244
	factors = ""
	i = 2
	while i * i <= n:
		if n % i == 0:
			factors += ", " + str(i)
			n //= i
		else:
			i += 1
	if n > 1:
		factors += ", " + str(n)
	factors = factors[2:len(factors):1]
	response = make_response(factors)
	return response

def pingTarget(target):
	p = subprocess.Popen(['ping',target,'-c','10',"-W","2"], stdout=subprocess.PIPE)
	p.wait()
	lines = []
	while True:
		line = p.stdout.readline()
		if line == b'':
			break
		l = line.decode('utf8').rstrip()
		lines.append(l)
	transmited, received = [int(a.split(' ')[0]) for a in lines[-2].split(', ')[:2]]
	stats, unit = lines[-1].split(' = ')[-1].split(' ')
	min_, avg, max_, stddev = [float(a) for a in stats.split('/')]
	return transmited, received, unit, min_, avg, max_, stddev


@app.route('/ping')
@login_required
def ping():
	ip = request.remote_addr
	transmited, received, unit, min_, avg, max_, stddev = pingTarget(ip)
	text = "" + ' ' + str(transmited) + ' ' + str(received) + ' ' + str(unit) + ' ' + str(min_) + ' ' + str(avg) + ' ' + str(max_) + ' ' + str(stddev)
	response = make_response(text)
	return response


@app.route('/bigfile/<filename>')
@login_required
def get_big_files(filename):
	#filename = request.match_info.get('name')
	with open(os.path.join('/vagrant', 'server', 'static', 'big_files', filename)) as f:
	#with open(os.path.join('/Users/admin/Documents/flask/server/static/big_files/', filename)) as f:
		text = f.read()
	response = make_response(text)
	return response


@app.route('/file/<filename>')
@login_required
def get_files(filename):
	#filename = request.match_info.get('name')
	with open(os.path.join('/vagrant', 'server', 'static', 'big_files', filename)) as f:
	#with open(os.path.join('/Users/admin/Documents/flask/server/static/big_files/', filename)) as f:
		text = f.read()
	response = make_response(text)
	return response
