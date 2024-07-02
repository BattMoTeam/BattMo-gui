
println("Current project genie: $(Base.active_project())")
println("BattMo loaded")
using Genie, Genie.Renderer.Json, Genie.Requests
using HTTP
using UUIDs
using JSON
using HDF5
using Base.Threads: ReentrantLock, lock, unlock


include("runP2DBattery.jl")


# Set the host explicitly
Genie.config.run_as_server = true
Genie.config.server_host = "0.0.0.0"
Genie.config.cors_allowed_origins = ["*"]

# Initialize lock
const simulation_lock = ReentrantLock()

function create_hdf5_output_file(output,file_path)

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

    HDF5.h5open(file_path, "w") do file
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

end



route("/run_simulation", method = POST) do
    # Retrieve JSON data from the request sent by Client
    input_data = jsonpayload()

    # Generate a UUID
    uuid_str_in = string(UUIDs.uuid4())
    uuid_str_out = string(UUIDs.uuid4())

    # Create a file name with the UUID
    input_file_name = "$uuid_str_in.json"
    output_path_name = uuid_str_out


    # Write the JSON data to the file
    open(input_file_name, "w") do temp_input_file
        JSON.print(temp_input_file, input_data)
    end

     # Process the input data as needed
    # For example, you can access input_data["key"] to access specific values

    # Run BattMo simulation
    try
        lock(simulation_lock) do
            output = runP2DBattery.runP2DBatt(input_file_name);

            if isfile(input_file_name)
                rm(input_file_name)  # Delete the file
                println("File deleted successfully.")
            else
                println("File does not exist.")
            end

            create_hdf5_output_file(output,"results/$output_path_name.h5")
        end
    catch e
        return JSON.json(Dict("error" => string(e)))


    end

    hdf5_data = read("results/$output_path_name.h5")

    # h5file = h5open("results/$output_path_name.h5", "r") do file
    #     # Read datasets
    #     number_of_states = read(file["concentrations"]["electrolyte"]["elyte_c_state_1"])
    #     println(number_of_states)
    # end


    # Concatenate the vectors of UInt8 into a single vector
    concatenated_data = vcat(hdf5_data...)

    # Set up the HTTP response
    response = HTTP.Response(200)
    push!(response.headers, "Content-Type" => "application/octet-stream")
    response.body = concatenated_data
    # response = HTTP.Response(200, headers=Dict("Content-Type" => "application/octet-stream"), body=concatenated_data)

    return response

end

up()