
### Import packages ###
# using Pkg
# Pkg.add("BattMo")
# Pkg.add("JSON")
# Pkg.add("Jutul")
# Pkg.add("PlutoUI")
# Pkg.add("Measures")


module runP2DBattery

    using BattMo, Jutul, JSON, PythonCall, Logging
    np = pyimport("numpy")

    export runP2DBatt

    function runP2DBatt(json_file)
        log_messages = String[]
        log_buffer = nothing
        number_of_states = 0 
        cell_voltage = 0
        cell_current = 0
        time_values = 0
        negative_electrode_grid = 0
        electrolyte_grid = 0
        positive_electrode_grid = 0
        negative_electrode_concentration = 0
        electrolyte_concentration = 0
        positive_electrode_concentration = 0
        negative_electrode_potential = 0
        electrolyte_potential = 0
        positive_electrode_potential = 0
        json_file = JSONFile(json_file)

        try
            # Create a custom IOBuffer to capture log messages
            log_buffer = IOBuffer()

            # Redirect the logger to use the custom IOBuffer
            global_logger(ConsoleLogger(log_buffer))

            print("Calling BattMo simulation")
            #states, reports, extra = runBattery_1d(input = jsondict, info_level = 0, extra_timing = false);
            states, reports, extra = run_battery(json_file, info_level = -1, end_report = true, extra_timing = false);
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
            negative_electrode_concentration = Array([[state[:NAM][:Cs] for state in states]/1000])
            electrolyte_concentration = [state[:ELYTE][:C] for state in states]/1000
            positive_electrode_concentration = Array([[state[:PAM][:Cs] for state in states]]/1000)
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
            
            # cell_voltage = np.array(cell_voltage)
            # cell_current = np.array(cell_current)
            # time_values = np.array(time_values)
            # negative_electrode_grid = np.array(negative_electrode_grid)
            # electrolyte_grid = np.array(electrolyte_grid)
            # positive_electrode_grid = np.array(positive_electrode_grid)
            # negative_electrode_concentration = np.array(negative_electrode_concentration)
            # print("size=",size(negative_electrode_concentration))
            # electrolyte_concentration = np.array(positive_electrode_grid)
            # positive_electrode_concentration = np.array(positive_electrode_concentration)
            # negative_electrode_potential = np.array(negative_electrode_potential)
            # electrolyte_potential = np.array(electrolyte_potential)
            # positive_electrode_potential = np.array(positive_electrode_potential)
            negative_electrode_concentration = negative_electrode_concentration[1]
            positive_electrode_concentration = positive_electrode_concentration[1]

            # for i in 1:size(negative_electrode_concentration)-1
            #     for j in 1:size(negative_electrode_concentration[1])-1
            #         negative_electrode_concentration[i,j] = negative_electrode_concentration_jl[i,j]
            #         positive_electrode_concentration[i,j] = positive_electrode_concentration_jl[i,j]
            #     end
            # end
            # Capture log messages
            seekstart(log_buffer)
            log_messages = split(String(take!(log_buffer)), "\n")
             

        finally
            close(log_buffer)  
        end
        #print(size(negative_electrode_concentration[1]))
        #output = [number_of_states, cell_voltage, cell_current, time_values, negative_electrode_grid, electrolyte_grid, positive_electrode_grid, negative_electrode_concentration, electrolyte_concentration, positive_electrode_concentration, negative_electrode_potential, electrolyte_potential, positive_electrode_potential];
        #output_py = pyjl(output)
        return log_messages, number_of_states, cell_voltage, cell_current, time_values, negative_electrode_grid, electrolyte_grid, positive_electrode_grid, negative_electrode_concentration, electrolyte_concentration, positive_electrode_concentration, negative_electrode_potential, electrolyte_potential, positive_electrode_potential
    end
end