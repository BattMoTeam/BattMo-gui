module runP2DBattery

    using BattMo, Logging,Jutul

    export runP2DBatt

    function runP2DBatt(json_file)

        inputparams = readBattMoJsonInputFile(json_file)

        try

            # setup simulation from the input parameters
            output = setup_simulation(inputparams)

            simulator = output[:simulator]
            model     = output[:model]
            state0    = output[:state0]
            forces    = output[:forces]
            timesteps = output[:timesteps]    
            cfg       = output[:cfg] 


            print("Calling BattMo simulation")
            states, reports = simulate(state0, simulator, timesteps; forces = forces, config = cfg)

            energy_efficiency = computeEnergyEfficiency(states);
            discharge_energy = computeCellEnergy(states);

            print("Simulation finished")

            con = BattMo.Constants();

            # Get some result values
            println("Number of states = ", size(states))
            number_of_states = size(states);
            time_values = cumsum(timesteps)/con.hour;
            cell_voltage = [state[:Control][:Phi][1] for state in states];
            cell_current = [state[:Control][:Current][1] for state in states];
            negative_electrode_grid_wrap = physical_representation(model[:NeAm]);
            electrolyte_grid_wrap = physical_representation(model[:Elyte]);
            positive_electrode_grid_wrap = physical_representation(model[:PeAm]);
            negative_electrode_concentration = Array([[state[:NeAm][:Cs] for state in states]/1000]);
            electrolyte_concentration = [state[:Elyte][:C] for state in states]/1000;
            positive_electrode_concentration = Array([[state[:PeAm][:Cs] for state in states]]/1000);
            negative_electrode_potential = [state[:NeAm][:Phi] for state in states];
            electrolyte_potential = [state[:Elyte][:Phi] for state in states];
            positive_electrode_potential = [state[:PeAm][:Phi] for state in states];

            nsteps = length(cell_voltage);
            time_values = time_values[1 : nsteps];

            # Mesh cell centroids coordinates
            centroids_NeAm = negative_electrode_grid_wrap[:cell_centroids, Cells()];
            centroids_Elyte = electrolyte_grid_wrap[:cell_centroids, Cells()];
            centroids_PeAm = positive_electrode_grid_wrap[:cell_centroids, Cells()];

            # Boundary faces coordinates
            boundaries_NeAm = negative_electrode_grid_wrap[:boundary_centroids, BoundaryFaces()];
            boundaries_Elyte = electrolyte_grid_wrap[:boundary_centroids, BoundaryFaces()];
            boundaries_PeAm = positive_electrode_grid_wrap[:boundary_centroids, BoundaryFaces()];

            negative_electrode_grid = centroids_NeAm.*10^6;
            negative_electrode_grid_bc = boundaries_NeAm.*10^6;
            electrolyte_grid = centroids_Elyte.*10^6;
            electrolyte_grid_bc = boundaries_Elyte.*10^6;
            positive_electrode_grid = centroids_PeAm.*10^6;
            positive_electrode_grid_bc = boundaries_PeAm.*10^6;
            negative_electrode_concentration = negative_electrode_concentration[1];
            positive_electrode_concentration = positive_electrode_concentration[1];
            
            return number_of_states, cell_voltage, cell_current, time_values, negative_electrode_grid, negative_electrode_grid_bc, electrolyte_grid, electrolyte_grid_bc, positive_electrode_grid, positive_electrode_grid_bc, negative_electrode_concentration, electrolyte_concentration, positive_electrode_concentration, negative_electrode_potential, electrolyte_potential, positive_electrode_potential,discharge_energy,energy_efficiency
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
            discharge_energy = [0]
            energy_efficiency = [0]

            return number_of_states, cell_voltage, cell_current, time_values, negative_electrode_grid, negative_electrode_grid_bc, electrolyte_grid, electrolyte_grid_bc, positive_electrode_grid, positive_electrode_grid_bc, negative_electrode_concentration, electrolyte_concentration, positive_electrode_concentration, negative_electrode_potential, electrolyte_potential, positive_electrode_potential,discharge_energy,energy_efficiency

        end

    end
end