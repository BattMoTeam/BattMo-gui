
### Import packages ###
# using Pkg
# Pkg.add("BattMo")
# Pkg.add("JSON")
# Pkg.add("Jutul")
# Pkg.add("PlutoUI")
# Pkg.add("Measures")

using BattMo, JSON,Jutul, PlutoUI, Measures

include("runbattery_1d.jl")



function runP2DBattery(json_file)
    #include(run_battery_file)
    print("open")
    #jsondict = JSON.parsefile(json_file)

    print("Calling BattMo simulation")
    #states, reports, extra = runBattery_1d(input = jsondict, info_level = 0, extra_timing = false);
    states, reports, extra = run_battery_1d(filename = json_file);
    print("Simulation finished")
    # Get some result values
    number_of_states = size(states)
    timesteps = extra[:timesteps]

    time = cumsum(timesteps)
    E    = [state[:BPP][:Phi][1] for state in states]


    


    #output = {number_of_states, cell_voltage, cell_current, time_values, negative_electrode_grid, electrolyte_grid, positive_electrode_grid, negative_electrode_concentration, electrolyte_concentration, positive_electrode_concentration, negative_electrode_potential, electrolyte_potential, positive_electrode_potential};

    return time, E
end