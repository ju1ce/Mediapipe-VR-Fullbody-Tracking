# Importing flask module in the project is mandatory
# An object of Flask class is our WSGI application.
from flask import Flask, render_template, request, redirect, url_for

import numpy as np

params = None

# Flask constructor takes the name of
# current module (__name__) as argument.
app = Flask(__name__)
 
# The route() function of the Flask class is a decorator,
# which tells the application which URL should call
# the associated function.
@app.route('/')
# ‘/’ URL is bound with hello_world() function.
def hello_world():
    return render_template('index.html', name="there", smooth=np.round(params.additional_smoothing,2))
    
@app.route('/smoothing', methods=["POST"])
def smoothing():
    if request.form["action"] in options.keys():
        newvalue = params.additional_smoothing + 0.1*options[request.form["action"]]
    else:
        newvalue = float(request.form["value"])
    newvalue = np.clip(newvalue,0,1)
    params.change_additional_smoothing(newvalue,paramid=1)
    return redirect(url_for("hello_world"))
    
options = {
"<<":-10,
"<":-1,
">":1,
">>":10}

@app.route('/roty', methods=["POST"])
def roty():
    cur = params.euler_rot_y
    change = options[request.form["action"]]
    params.rot_change_y(cur+change)
    return redirect(url_for("hello_world"))
    
@app.route('/rotx', methods=["POST"])
def rotx():
    cur = params.euler_rot_x
    change = options[request.form["action"]]
    params.rot_change_x(cur+change)
    return redirect(url_for("hello_world"))
    
@app.route('/rotz', methods=["POST"])
def rotz():
    cur = params.euler_rot_z
    change = options[request.form["action"]]
    params.rot_change_z(cur+change)
    return redirect(url_for("hello_world"))
    
@app.route('/scale', methods=["POST"])
def scale():
    cur = params.posescale
    change = options[request.form["action"]] /100
    params.change_scale(cur+change)
    return redirect(url_for("hello_world"))
    
@app.route('/autocalib', methods=["POST"])
def autocalib():
    params.gui.autocalibrate()
    return redirect(url_for("hello_world"))
 
# main driver function
def start_webui(param):
    global params
    params=param
    # run() method of Flask class runs the application
    # on the local development server.
    print("INFO: Starting WebUI!")
    print("INFO: To access the webui, simply open the second Running on IP address on your quests browser!")
    app.run(host="0.0.0.0")