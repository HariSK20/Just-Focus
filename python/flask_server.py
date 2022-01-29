import sys
from flask import Flask, request
from flask_cors import cross_origin


app = Flask(__name__)

ru_flag = True
state = 0

@app.route("/check")
@cross_origin()
def check():
	global state, ru_flag
	if(ru_flag):
		state += 1
	return(str(state))

@app.route("/stop", methods = ['POST', 'GET'])
def stop():
	global ru_flag
	if( request.method == 'POST'):
		ru_flag = not ru_flag
	elif( request.method == 'GET'):
		return(str(ru_flag))
	return("Nothing")

if __name__ == "__main__":
    app.run(host='127.0.0.1', port=5001)
