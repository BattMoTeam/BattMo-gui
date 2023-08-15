from flask import Flask, render_template, request
import multiprocessing 
import time
import json
import requests
#from q import Queue

# global jl
# jl = Main

##############################
# RUN JULIA CODE FUNCTION
##############################
def run_julia(queue):
    print("start")
    from julia import Main
    Main.include("BattMoJulia/runP2DBattery.jl")

    while True:

        if data := queue.get:
            output = Main.runP2DBattery.runP2DBatt(data)
            print("Output = ", output[0])
        else:
            time.sleep(0.5)
 
    
###############################################
# SET MULTIPROCESSING START METHOD FUNCTION
###############################################

def multi_set():
    multiprocessing.set_start_method("spawn")


##############################
# Create flask app
##############################

app = Flask(__name__)



@app.route("/multi")
def multi():
    print("Multi")
    multi_set()
    data = requests.get('http://localhost:8501/Run_simulation')
    data = data
    return ("Setup is %s") %data
    

@app.route('/run_simulation')
def background_process_test():
    #multiprocessing.set_start_method("spawn")
    data = requests.get('http://localhost:8501/Run_simulation')
    print("Background")
    q = multiprocessing.Queue()
    q.put(data)
    process1 = multiprocessing.Process(name = 'process1',target = run_julia, args = (q, )) 
    process1.start()
    process1.join()

    print("simulation finished")
    return ("nothing")




if __name__ == '__main__':
    print("main")

    app.run(debug=True)





    
# @app.route ("/home")
# def home():
#     return render_template('home.html')

# @app.route("/result", methods = ['POST', 'GET'])
# def result():
#     output = request.form.to_dict()
#     name = output["name"]
#     return render_template('home.html', name = name)

# @app.route("/run")
# def json_run():

#     return render_template('json.html')

# @app.route("/input")
# def input():
#     json_file = json.loads("BattMoJulia/battmo_formatted_input.json")
#     data = requests.post('http://127.0.0.1:5000/run_simulation',json = json_file)
#     print(data)

#     return "nothing"

# @app.route('/multip')
# def multiprocess():
#     multi()
#     return ("nothing")