
### Import packages ###
# using Pkg
# Pkg.add("BattMo")
# Pkg.add("JSON")
# Pkg.add("Jutul")
# Pkg.add("PlutoUI")
# Pkg.add("Measures")


module runP2DBattery

    using BattMo, Jutul, JSON

    export runP2DBatt

    function runP2DBatt(json_file)


        print("Calling BattMo simulation")
        #states, reports, extra = runBattery_1d(input = jsondict, info_level = 0, extra_timing = false);
        states, reports, extra = run_battery_1d(filename = json_file, info_level = -1, end_report = true, extra_timing = false);
        print("Simulation finished")

        con = BattMo.Constants()

        # Get some result values
        number_of_states = size(states)
        timesteps = extra[:timesteps]
        time_values = cumsum(timesteps)/con.hour
        cell_voltage = [state[:BPP][:Phi][1] for state in states]
        cell_current = [state[:BPP][:Current][1] for state in states]
        negative_electrode_grid_wrap = physical_representation(extra[:model][:NAM])
        electrolyte_grid_wrap = physical_representation(extra[:model][:ELYTE])
        positive_electrode_grid_wrap = physical_representation(extra[:model][:PAM])
        negative_electrode_concentration = Array([state[:NAM][:Cp] for state in states])/1000
        electrolyte_concentration = [state[:ELYTE][:C] for state in states]/1000
        positive_electrode_concentration = Array([state[:PAM][:Cp] for state in states])/1000
        negative_electrode_potential = [state[:NAM][:Phi] for state in states]
        electrolyte_potential = [state[:ELYTE][:Phi] for state in states]
        positive_electrode_potential = [state[:PAM][:Phi] for state in states]

        # Mesh cell centroids coordinates
        centroids_NAM = negative_electrode_grid_wrap[:cell_centroids, Cells()]
        centroids_ELYTE = electrolyte_grid_wrap[:cell_centroids, Cells()]
        centroids_PAM = positive_electrode_grid_wrap[:cell_centroids, Cells()]

        # Boundary faces coordinates
        boundaries_NAM = negative_electrode_grid_wrap[:boundary_centroids, BoundaryFaces()]
        boundaries_ELYTE = electrolyte_grid_wrap[:boundary_centroids, BoundaryFaces()]
        boundaries_PAM = positive_electrode_grid_wrap[:boundary_centroids, BoundaryFaces()]

        # Create grid arrays

        negative_electrode_grid = [centroids_NAM, boundaries_NAM]
        electrolyte_grid = [centroids_ELYTE, boundaries_ELYTE]
        positive_electrode_grid = [centroids_PAM, boundaries_PAM]

        # The following piece of code is needed when using JuliaCall as translation package:
        
        # cell_voltage = JSON.json(cell_voltage)
        # cell_current = JSON.json(cell_current)
        # time_values = JSON.json(time_values)
        # negative_electrode_grid = JSON.json(negative_electrode_grid)
        # electrolyte_grid = JSON.json(electrolyte_grid)
        # positive_electrode_grid = JSON.json(positive_electrode_grid)
        # negative_electrode_concentration = JSON.json(negative_electrode_concentration)
        # print("size=",size(negative_electrode_concentration))
        # electrolyte_concentration = JSON.json(positive_electrode_grid)
        # positive_electrode_concentration = JSON.json(positive_electrode_concentration)
        # negative_electrode_potential = JSON.json(negative_electrode_potential)
        # electrolyte_potential = JSON.json(electrolyte_potential)
        # positive_electrode_potential = JSON.json(positive_electrode_potential)




        
        output = [number_of_states, cell_voltage, cell_current, time_values, negative_electrode_grid, electrolyte_grid, positive_electrode_grid, negative_electrode_concentration, electrolyte_concentration, positive_electrode_concentration, negative_electrode_potential, electrolyte_potential, positive_electrode_potential];

        return output
    end
end