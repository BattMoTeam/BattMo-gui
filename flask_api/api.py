from flask import Flask, request, render_template, send_file 
import multiprocessing
from multiprocessing import Queue
import time
import json
from flask_restful import Resource, Api
import pickle
from uuid import uuid4
import os
import numpy as np


##############################
# Global variable for status
##############################
execution_status = "Not started"

##############################
# RUN JULIA CODE FUNCTION
##############################

def run_julia(q_in,q_out):

    
    from juliacall import Main as jl

    jl.seval('include("julia/runP2DBattery.jl")')
    print("Julia module is imported")

    while True:

        if uuid_str:= q_in.get():
            uuid_str = str(uuid_str)
            file_name = f"{uuid_str}.json"
            
            # Define the Julia code to execute
            julia_code = f"runP2DBattery.runP2DBatt(\"{file_name}\")"
            log_messages, number_of_states, cell_voltage, cell_current, time_values, negative_electrode_grid, negative_electrode_grid_bc, electrolyte_grid, electrolyte_grid_bc, positive_electrode_grid, positive_electrode_grid_bc, negative_electrode_concentration, electrolyte_concentration, positive_electrode_concentration, negative_electrode_potential, electrolyte_potential, positive_electrode_potential = jl.seval(julia_code)
            
            print("The simulation has completed {} time steps.".format(number_of_states))

            # Converting data to python objects
            negative_electrode_concentration = [jl.Py(subarray).to_numpy() for subarray in negative_electrode_concentration],
            negative_electrode_concentration = np.vstack(negative_electrode_concentration)

            electrolyte_concentration = [jl.Py(subarray).to_numpy() for subarray in electrolyte_concentration],
            electrolyte_concentration = np.vstack(electrolyte_concentration)

            positive_electrode_concentration = [jl.Py(subarray).to_numpy() for subarray in positive_electrode_concentration],
            positive_electrode_concentration = np.vstack(positive_electrode_concentration)

            negative_electrode_potential = [jl.Py(subarray).to_numpy() for subarray in negative_electrode_potential],
            negative_electrode_potential = np.vstack(negative_electrode_potential)

            electrolyte_potential = [jl.Py(subarray).to_numpy() for subarray in electrolyte_potential],
            electrolyte_potential = np.vstack(electrolyte_potential)

            positive_electrode_potential = [jl.Py(subarray).to_numpy() for subarray in positive_electrode_potential],
            positive_electrode_potential = np.vstack(positive_electrode_potential)

            
            print(number_of_states)
            
            output = [ np.array(log_messages),
                int(number_of_states[0]),
                jl.Py(cell_voltage).to_numpy(),
                jl.Py(cell_current).to_numpy(),
                jl.Py(time_values).to_numpy(),
                np.squeeze(jl.Py(negative_electrode_grid).to_numpy()),
                np.squeeze(jl.Py(negative_electrode_grid_bc).to_numpy()),
                np.squeeze(jl.Py(electrolyte_grid).to_numpy()),
                np.squeeze(jl.Py(electrolyte_grid_bc).to_numpy()),
                np.squeeze(jl.Py(positive_electrode_grid).to_numpy()),
                np.squeeze(jl.Py(positive_electrode_grid_bc).to_numpy()),
                negative_electrode_concentration,
                electrolyte_concentration,
                positive_electrode_concentration,
                negative_electrode_potential,
                electrolyte_potential,
                positive_electrode_potential]
            
            
            # print("1: ", negative_electrode_grid)
            # print("2: ", output[5])
            # print("3: ", type(output[5]))
            # with open("test.txt", "w") as new_pickle_file:
            #     new_pickle_file.write(output)

            with open(os.path.join("results",uuid_str), "wb") as new_pickle_file:
                pickle.dump(output, new_pickle_file)

            os.remove("%s.json" % uuid_str)


            q_out.put(uuid_str)
            
        else:
            print("wait")
            time.sleep(2)




##############################
# Create flask app
############################

server = Flask(__name__)
api = Api(server)

q_in = Queue()
q_out = Queue()
p = multiprocessing.Process(name = 'p',target = run_julia, args=(q_in,q_out ))
p.start()

class RunSimulation(Resource):

    def post(self):
        
        
        data = request.json

        uuids = uuid4()
        uuid_str = str(uuids)
        file_name = "%s.json" % uuid_str

        with open(file_name, "w") as temp_input_file:
            json.dump( data,temp_input_file)

        print("Temporary input file is created")

        q_in.put(uuid_str)

        print("q_in is filled")
        running = True

        while running == True:
            print("...")
            if uuids := q_out.get():
                print("q_out has been filled")
                running = False
            else:
                time.sleep(1)
               
        uuid_str = str(uuids)

        # Send the HDF5 file to the client
        return send_file(f"results/{uuid_str}", as_attachment=True, mimetype='application/octet-stream')


api.add_resource(RunSimulation, '/run_simulation')