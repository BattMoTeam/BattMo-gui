module runP2DBattery

    using BattMo, Logging,Jutul

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
        negative_electrode_grid_bc = 0
        electrolyte_grid_bc = 0
        positive_electrode_grid_bc = 0
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
            states, reports, extra = run_battery(json_file, extra_timing = false);
            print("Simulation finished")
            
            # file = "./"*output_path*"/jutul_1.jld2"
            # output_1 = JLD2.load(file)


            # print(output_1)

            con = BattMo.Constants()

            # Get some result values
            number_of_states = size(states)
            timesteps = extra[:timesteps]
            time_values = cumsum(timesteps)/con.hour
            cell_voltage = [state[:Control][:Phi][1] for state in states]
            cell_current = [state[:Control][:Current][1] for state in states]
            negative_electrode_grid_wrap = physical_representation(extra[:model][:NeAm])
            electrolyte_grid_wrap = physical_representation(extra[:model][:Elyte])
            positive_electrode_grid_wrap = physical_representation(extra[:model][:PeAm])
            negative_electrode_concentration = Array([[state[:NeAm][:Cs] for state in states]/1000])
            electrolyte_concentration = [state[:Elyte][:C] for state in states]/1000
            positive_electrode_concentration = Array([[state[:PeAm][:Cs] for state in states]]/1000)
            negative_electrode_potential = [state[:NeAm][:Phi] for state in states]
            electrolyte_potential = [state[:Elyte][:Phi] for state in states]
            positive_electrode_potential = [state[:PeAm][:Phi] for state in states]

            nsteps = length(cell_voltage)
            time_values = time_values[1 : nsteps]

            # Mesh cell centroids coordinates
            centroids_NeAm = negative_electrode_grid_wrap[:cell_centroids, Cells()]
            centroids_Elyte = electrolyte_grid_wrap[:cell_centroids, Cells()]
            centroids_PeAm = positive_electrode_grid_wrap[:cell_centroids, Cells()]

            # Boundary faces coordinates
            boundaries_NeAm = negative_electrode_grid_wrap[:boundary_centroids, BoundaryFaces()]
            boundaries_Elyte = electrolyte_grid_wrap[:boundary_centroids, BoundaryFaces()]
            boundaries_PeAm = positive_electrode_grid_wrap[:boundary_centroids, BoundaryFaces()]

            # Create grid arrays

            # negative_electrode_grid = [centroids_NeAm, boundaries_NeAm].*10^6
            # electrolyte_grid = [centroids_Elyte, boundaries_Elyte].*10^6
            # positive_electrode_grid = [centroids_PeAm, boundaries_PeAm].*10^6

            negative_electrode_grid = centroids_NeAm.*10^6
            negative_electrode_grid_bc = boundaries_NeAm.*10^6
            electrolyte_grid = centroids_Elyte.*10^6
            electrolyte_grid_bc = boundaries_Elyte.*10^6
            positive_electrode_grid = centroids_PeAm.*10^6
            positive_electrode_grid_bc = boundaries_PeAm.*10^6
            negative_electrode_concentration = negative_electrode_concentration[1]
            positive_electrode_concentration = positive_electrode_concentration[1]

            # Capture log messages
            seekstart(log_buffer)
            log_messages = split(String(take!(log_buffer)), "\n")
             
            return log_messages, number_of_states, cell_voltage, cell_current, time_values, negative_electrode_grid, negative_electrode_grid_bc, electrolyte_grid, electrolyte_grid_bc, positive_electrode_grid, positive_electrode_grid_bc, negative_electrode_concentration, electrolyte_concentration, positive_electrode_concentration, negative_electrode_potential, electrolyte_potential, positive_electrode_potential
        catch e
            println("Simulation failed: $e")

            number_of_states = [0]
            cell_voltage = [0]
            cell_current = [0]
            time_values = [0]
            negative_electrode_grid = [0]
            negative_electrode_grid_bc = [0]
            electrolyte_grid = [0]
            electrolyte_grid_bc = [0]
            positive_electrode_grid = [0]
            positive_electrode_grid_bc = [0]
            negative_electrode_concentration = [0]
            electrolyte_concentration = [0]
            positive_electrode_concentration = [0]
            negative_electrode_potential = [0]
            electrolyte_potential = [0]
            positive_electrode_potential = [0]

            # Capture log messages
            seekstart(log_buffer)
            log_messages = split(String(take!(log_buffer)), "\n")
            return log_messages, number_of_states, cell_voltage, cell_current, time_values, negative_electrode_grid, negative_electrode_grid_bc, electrolyte_grid, electrolyte_grid_bc, positive_electrode_grid, positive_electrode_grid_bc, negative_electrode_concentration, electrolyte_concentration, positive_electrode_concentration, negative_electrode_potential, electrolyte_potential, positive_electrode_potential

        finally
            close(log_buffer)  
        end

        #return log_messages, number_of_states, cell_voltage, cell_current, time_values, negative_electrode_grid, negative_electrode_grid_bc, electrolyte_grid, electrolyte_grid_bc, positive_electrode_grid, positive_electrode_grid_bc, negative_electrode_concentration, electrolyte_concentration, positive_electrode_concentration, negative_electrode_potential, electrolyte_potential, positive_electrode_potential
    end
end