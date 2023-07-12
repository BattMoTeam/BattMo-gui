
### Import packages ###
using Pkg
Pkg.add("BattMo")
Pkg.add("JSON")

using BattMo, JSON

function runP2DBattery(x, input)



##############
# Test function
    y = x+x

##############


    states, reports, extra = run_battery_1d(filename = input, info_level = 0, extra_timing = false);

    # Get some result values
    number_of_states = size(states)
    timesteps = extra[:timesteps]

    time = cumsum(timesteps)
    E    = [state[:BPP][:Phi][1] for state in states]



    Output = {time, E}


    #output = {number_of_states, cell_voltage, cell_current, time_values, negative_electrode_grid, electrolyte_grid, positive_electrode_grid, negative_electrode_concentration, electrolyte_concentration, positive_electrode_concentration, negative_electrode_potential, electrolyte_potential, positive_electrode_potential};

    return output
end