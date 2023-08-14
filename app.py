from flask import Flask, render_template

import multiprocessing




# sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
# print(sys.path)
#import julia

#julia.install()

#jl.seval('include("BattMoJulia/runP2DBattery.jl")')
from julia import Main
# import julia
# julia.install()

Main.include("BattMoJulia/runP2DBattery.jl")


def run_julia():
    print("start")
    # runP2DBatt = Main.eval("""
    # using BattMo, Jutul                       

    # function runP2DBatt(json_file)


    #     print("Calling BattMo simulation")
    #     #states, reports, extra = runBattery_1d(input = jsondict, info_level = 0, extra_timing = false);
    #     states, reports, extra = run_battery_1d(filename = json_file, info_level = -1, end_report = true, extra_timing = false);
    #     print("Simulation finished")

    #     con = BattMo.Constants()

    #     # Get some result values
    #     number_of_states = size(states)
    #     timesteps = extra[:timesteps]
    #     time_values = cumsum(timesteps)/con.hour
    #     cell_voltage = [state[:BPP][:Phi][1] for state in states]
    #     cell_current = [state[:BPP][:Current][1] for state in states]
    #     negative_electrode_grid_wrap = physical_representation(extra[:model][:NAM])
    #     electrolyte_grid_wrap = physical_representation(extra[:model][:ELYTE])
    #     positive_electrode_grid_wrap = physical_representation(extra[:model][:PAM])
    #     negative_electrode_concentration = Array([state[:NAM][:Cp] for state in states])/1000
    #     electrolyte_concentration = [state[:ELYTE][:C] for state in states]/1000
    #     positive_electrode_concentration = Array([state[:PAM][:Cp] for state in states])/1000
    #     negative_electrode_potential = [state[:NAM][:Phi] for state in states]
    #     electrolyte_potential = [state[:ELYTE][:Phi] for state in states]
    #     positive_electrode_potential = [state[:PAM][:Phi] for state in states]

    #     # Mesh cell centroids coordinates
    #     centroids_NAM = negative_electrode_grid_wrap[:cell_centroids, Cells()]
    #     centroids_ELYTE = electrolyte_grid_wrap[:cell_centroids, Cells()]
    #     centroids_PAM = positive_electrode_grid_wrap[:cell_centroids, Cells()]

    #     # Boundary faces coordinates
    #     boundaries_NAM = negative_electrode_grid_wrap[:boundary_centroids, BoundaryFaces()]
    #     boundaries_ELYTE = electrolyte_grid_wrap[:boundary_centroids, BoundaryFaces()]
    #     boundaries_PAM = positive_electrode_grid_wrap[:boundary_centroids, BoundaryFaces()]

    #     # Create grid arrays

    #     negative_electrode_grid = [centroids_NAM, boundaries_NAM]
    #     electrolyte_grid = [centroids_ELYTE, boundaries_ELYTE]
    #     positive_electrode_grid = [centroids_PAM, boundaries_PAM]
    #     #print([state[:BPP][:Phi] for state in states])
    #     #print("time =", time_values.shape)
    #     # print("pep =", positive_electrode_potential)
    #     # print("nep =", negative_electrode_potential)  
    #     #output = negative_electrode_concentration
    #     output = [number_of_states, cell_voltage, cell_current, time_values, negative_electrode_grid, electrolyte_grid, positive_electrode_grid, negative_electrode_concentration, electrolyte_concentration, positive_electrode_concentration, negative_electrode_potential, electrolyte_potential, positive_electrode_potential];

    #     return output
    # end
    #                     """)

    
    output = Main.runP2DBattery.runP2DBatt("BattMoJulia/p2d_40_jl.json")
    #print(output)
    return output


app = Flask(__name__)

@app.route("/run")
def json():

    return render_template('json.html')






#background process happening without any refreshing
@app.route('/background_process_test')
def background_process_test():

    multiprocessing.set_start_method("spawn")
    
    #jl.seval("using BattMo")
    #Main.include("BattMoJulia/runP2DBattery.jl")
    print ("Hello")
    global process

    
    process = multiprocessing.Process(target = run_julia)
    #states, reports, extra = jl.seval('run_battery_1d(filename ="BattMoJulia/p2d_40_jl.json")')
    #run_julia()
    
    process.start()
    process.join()

    print("simulation finished")
    return ("nothing")

    # output = jl.seval('runP2DBattery("BattMoJulia/p2d_40_jl.json")')

    
    # return "<p>Voltage, = , %s </p>" % output(2)

if __name__ == '__main__':
    
    #app.run(debug=True)
    multiprocessing.set_start_method("spawn", force=True)
    app.background_process_test(debug=True)

