from flask import Flask, render_template, request
import multiprocessing 
from multiprocessing import Queue
import time
import json
import requests
from flask_restful import Resource, Api
import pickle



##############################
# RUN JULIA CODE FUNCTION
##############################
 
def run_julia(q):
    
    from julia import Main
    Main.include("BattMoJulia/runP2DBattery.jl")   
    print("run")
    while True:

        if q.get():
            output = Main.runP2DBattery.runP2DBatt("BattMoJulia/battmo_formatted_input.json")
            print("Output = ", output[0])
            with open("python/battmo_result", "wb") as new_pickle_file:
                pickle.dump(output, new_pickle_file)
        else:
            print("wait")
            time.sleep(2)


##############################
# Create flask app
##############################

app = Flask(__name__)
api = Api(app)



class run_simulation(Resource):
    def get(self, run):

        return {'running': run}
    
    def put(self):
        run = request.form['data']
        #uuid = uuid4()
        print("running = ", run)
        
        q.put(run)
        
        #p.join()
        return {'running': run}


api.add_resource(run_simulation, '/run_simulation')


if __name__ == '__main__':
    multiprocessing.set_start_method("spawn")
    q = Queue()
    p = multiprocessing.Process(name = 'p',target = run_julia, args=(q, )) 
    p.start()
    app.run(debug=True, use_reloader = True)




# @app.route('/run_simulation', methods = ['GET', 'POST'])
# def background_process_test():
#     #multiprocessing.set_start_method("spawn")
#     data = requests.get('http://localhost:8501/Run_simulation')
#     print(data.status_code)
#     print(data)

#     input_object = json.dumps(data)
#     ID = "input_temporary"

#     with open((ID,".json"), "w") as outfile:
#         outfile.write(input_object)

#     print("Background")
#     #data = json.loads(data)
#     print(ID+".json")
#     q = Queue()
#     q.put(ID)

        
    
#     p = multiprocessing.Process(name = 'p',target = run_julia, args = (q,)) 
#     p.start()
  


#     print("simulation finished")
#     return q

# def run_julia(q):
#     print("start")
#     from julia import Main
#     Main.include("BattMoJulia/runP2DBattery.jl")
#     ID = q.get
#     file_path = ID +".json"
#     output = Main.runP2DBattery.runP2DBatt(file_path)
#     print("Output = ", output[0])
    
    
#     # while True:

        
#     #     filled = q.empty

#     #     if filled == False:
#     #     #filled == False:
#     #         #print(data)
#     #         #
#     #         data = 'BattMoJulia/battmo_formatted_input.json'
#     #         file_path = ID +".json"
#     #         print(file_path)
#     #         output = Main.runP2DBattery.runP2DBatt(file_path)
#     #         print("Output = ", output[0])
#     #     else:
#     #         print("wait")
#     #         time.sleep(2)


    
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