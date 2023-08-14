from flask import Flask, render_template

import sys
import os

# sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
# print(sys.path)

#jl.seval('include("BattMoJulia/runP2DBattery.jl")')




app = Flask(__name__)

@app.route("/run")
def json():

    return render_template('json.html')

from julia import Main

#jl.seval("using BattMo")
Main.include("BattMoJulia/runP2DBattery.jl")

#background process happening without any refreshing
@app.route('/background_process_test')
def background_process_test():


    print ("Hello")
    #states, reports, extra = jl.seval('run_battery_1d(filename ="BattMoJulia/p2d_40_jl.json")')
    states, reports, extra = Main.runP2DBatt("BattMoJulia/p2d_40_jl.json")

    print("simulation finished")
    return ("nothing")

    # output = jl.seval('runP2DBattery("BattMoJulia/p2d_40_jl.json")')

    
    # return "<p>Voltage, = , %s </p>" % output(2)

