from flask import Flask, request
import multiprocessing
from multiprocessing import Queue
import time
import json
from flask_restful import Resource, Api
import pickle
from uuid import uuid4
import os


##############################
# RUN JULIA CODE FUNCTION
##############################

def run_julia(q_in,q_out):

    from julia import Main
    Main.include("BattMoJulia/runP2DBattery.jl")
    print("run")

    while True:

        if uuid_str:= q_in.get():
            uuid_str = str(uuid_str)
            file_name = "%s.json" % uuid_str
            output = Main.runP2DBattery.runP2DBatt(file_name)
            print("Output = ", output[0])
            os.remove(file_name)

            with open(os.path.join("results",uuid_str), "wb") as new_pickle_file:
                pickle.dump(output, new_pickle_file)


            q_out.put(uuid_str)
            print("...")
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

        print("temp file was made")

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


api.add_resource(run_simulation, '/run_simulation')



if __name__ == '__main__':
    multiprocessing.set_start_method("spawn")
    q_in = Queue()
    q_out = Queue()
    p = multiprocessing.Process(name = 'p',target = run_julia, args=(q_in,q_out ))
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