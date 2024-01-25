from flask import Flask, request, render_template
import multiprocessing
from multiprocessing import Queue
import time
import json
from flask_restful import Resource, Api
import pickle
from uuid import uuid4
import os

##############################
# Global variable for status
##############################
execution_status = "Not started"

##############################
# RUN JULIA CODE FUNCTION
##############################

def run_julia(q_in,q_out):

    
    from juliacall import Main as jl

    jl.seval('include("BattMoJulia/runP2DBattery.jl")')
    print("Julia module is imported")

    while True:

        if uuid_str:= q_in.get():
            uuid_str = str(uuid_str)
            file_name = f"{uuid_str}.json"
            
            # Define the Julia code to execute
            julia_code = f"runP2DBattery.runP2DBatt(\"{file_name}\")"
            log_messages, number_of_states, cell_voltage, cell_current, time_values, negative_electrode_grid, electrolyte_grid, positive_electrode_grid, negative_electrode_concentration, electrolyte_concentration, positive_electrode_concentration, negative_electrode_potential, electrolyte_potential, positive_electrode_potential = jl.seval(julia_code)
            
            print("The simulation has completed {} time steps.".format(number_of_states))
            
            output = [log_messages, number_of_states, cell_voltage, cell_current, time_values, negative_electrode_grid, electrolyte_grid, positive_electrode_grid, negative_electrode_concentration, electrolyte_concentration, positive_electrode_concentration, negative_electrode_potential, electrolyte_potential, positive_electrode_potential]
        
            os.remove("%s.json" % uuid_str)

            with open(os.path.join("results",uuid_str), "wb") as new_pickle_file:
                pickle.dump(output, new_pickle_file)


            q_out.put(uuid_str)
            
        else:
            print("wait")
            time.sleep(2)




##############################
# Create flask app
##############################

app = Flask(__name__)
api = Api(app)


class run_simulation(Resource):

    def get(self):

        data = request.form

        input_file = data['InputFolder'] + '/' + data['InputFile']
        print(input_file)
        with open(input_file, 'r') as j:
            json_data = json.loads(j.read()) 


        uuids = uuid4()
        uuid_str = str(uuids)
        file_name = "%s.json" % uuid_str

        with open(file_name, "w") as temp_input_file:
            json.dump( json_data,temp_input_file)

        print("Temporary input file is created")

        q_in.put(uuid_str)

        print("q_in is filled")
        running = True

        while running == True:
            if uuids := q_out.get():
                print("q_out has been filled")
                running = False
            else:
                time.sleep(1)
               
        uuid_str = str(uuids)

        return uuid_str

    def post(self):
        
        return ("nothing")


@app.route('/')
def index():


    return render_template('index.html', message="The Flask API is active")


api.add_resource(run_simulation, '/run_simulation')




if __name__ == '__main__':
    multiprocessing.set_start_method("spawn")
    q_in = Queue()
    q_out = Queue()
    p = multiprocessing.Process(name = 'p',target = run_julia, args=(q_in,q_out ))
    p.start()

    app.run(debug=False, use_reloader = False)
