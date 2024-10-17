

export create_hdf5_output_file
function create_hdf5_output_file(output, output_file_path)
    # Get the path of the directory where the current script is located
    current_dir = @__DIR__

    # define the path for the logging output
    log_path = abspath(joinpath(current_dir, "..", "logs", "hdf5Formatting.log"))

    open(log_path, "w") do file

        redirect_stdout(file)
        redirect_stderr(file)

        try
            # Create a custom IOBuffer to capture log messages
            log_buffer = IOBuffer();

            # Redirect the logger to use the custom IOBuffer
            global_logger(ConsoleLogger(log_buffer));
            log_messages,
            number_of_states,
            cell_voltage,
            cell_current,
            time_values,
            negative_electrode_grid,
            negative_electrode_grid_bc,
            electrolyte_grid,
            electrolyte_grid_bc,
            positive_electrode_grid,
            positive_electrode_grid_bc,
            negative_electrode_concentration,
            electrolyte_concentration,
            positive_electrode_concentration,
            negative_electrode_potential,
            electrolyte_potential,
            positive_electrode_potential,
            discharge_energy,
            energy_efficiency = output

            log_messages_strings = string.(log_messages)
            #bio = IOBuffer()

            HDF5.h5open(output_file_path, "w") do file
                print(number_of_states)
                file["number_of_states"] = number_of_states[1]

                # Write datasets
                print(typeof(log_messages))
                file["log_messages"] = log_messages_strings
                file["cell_voltage"] = cell_voltage
                file["cell_current"] = cell_current
                file["time_values"] = time_values

                println("number of states = ", number_of_states[1])

                # Create groups
                grids = create_group(file, "grids")
                concentrations = create_group(file, "concentrations")
                potentials = create_group(file, "potentials")
                indicators = create_group(file, "indicators")
                json_files = create_group(file, "json_input_files")

                # Write indicators
                cell = create_group(indicators, "cell")
                cell_discharge_energy = create_group(cell, "discharge_energy")
                write(cell_discharge_energy, "value", discharge_energy)
                cell_spec_energy = create_group(cell, "specific_energy")
                write(cell_spec_energy,"value",1)
                cell_spec_energy = create_group(cell, "energy_efficiency")
                write(cell_spec_energy, "value", energy_efficiency)

                # Write grid datasets
                grids["negative_electrode_grid"] = negative_electrode_grid
                grids["positive_electrode_grid"] = positive_electrode_grid
                grids["electrolyte_grid"] = electrolyte_grid
                grids["negative_electrode_grid_bc"] = negative_electrode_grid_bc
                grids["electrolyte_grid_bc"] = electrolyte_grid_bc
                grids["positive_electrode_grid_bc"] = positive_electrode_grid_bc


                negative_electrode_concentrations = create_group(concentrations, "negative_electrode")
                electrolyte_concentrations = create_group(concentrations, "electrolyte")
                positive_electrode_concentrations = create_group(concentrations, "positive_electrode")
                negative_electrode_potentials = create_group(potentials, "negative_electrode")
                electrolyte_potentials = create_group(potentials, "electrolyte")
                positive_electrode_potentials = create_group(potentials, "positive_electrode")

                # Write concentration and potential datasets
                for i in 1:number_of_states[1]
                    ne_c_dataset_name = "ne_c_state_$i"
                    pe_c_dataset_name = "pe_c_state_$i"
                    elyte_c_dataset_name = "elyte_c_state_$i"
                    ne_p_dataset_name = "ne_p_state_$i"
                    pe_p_dataset_name = "pe_p_state_$i"
                    elyte_p_dataset_name = "elyte_p_state_$i"

                    write(negative_electrode_concentrations, ne_c_dataset_name, negative_electrode_concentration[i])
                    write(positive_electrode_concentrations, pe_c_dataset_name, positive_electrode_concentration[i])
                    write(electrolyte_concentrations, elyte_c_dataset_name, electrolyte_concentration[i])

                    write(negative_electrode_potentials, ne_p_dataset_name, negative_electrode_potential[i])
                    write(positive_electrode_potentials, pe_p_dataset_name, positive_electrode_potential[i])
                    write(electrolyte_potentials, elyte_p_dataset_name, electrolyte_potential[i])
                end
            end

        catch e
            println("Error formatting hdf5 file: ", e)
        end
    end

end
