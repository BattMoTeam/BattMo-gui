
println("Current project genie: $(Base.active_project())")
println("BattMo loaded")
using Genie, Genie.Renderer.Json, Genie.Requests
using HTTP
using UUIDs
using JSON
using HDF5

include("runP2DBattery.jl") 


# Set the host explicitly
Genie.config.run_as_server = true
Genie.config.server_host = "0.0.0.0"
Genie.config.cors_allowed_origins = ["*"]

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
    positive_electrode_potential = output


    #bio = IOBuffer()

    HDF5.h5open(file_path, "w") do file
        file["number_of_states"] = number_of_states[1]
        
        # Write datasets
        file["log_messages"] = log_messages
        file["cell_voltage"] = cell_voltage
        file["cell_current"] = cell_current
        file["time_values"] = time_values
        file["negative_electrode_grid_bc"] = negative_electrode_grid_bc
        file["electrolyte_grid_bc"] = electrolyte_grid_bc
        file["positive_electrode_grid_bc"] = positive_electrode_grid_bc
        println("number of states = ", number_of_states[1])

        # Create groups
        grids = create_group(file, "grids")
        concentrations = create_group(file, "concentrations")
        potentials = create_group(file, "potentials")

        # Write grid datasets
        grids["negative_electrode_grid"] = negative_electrode_grid
        grids["positive_electrode_grid"] = positive_electrode_grid
        grids["electrolyte_grid"] = electrolyte_grid

        # Write concentration datasets
        for i in 1:number_of_states[1]
            concentrations["negative_electrode_concentration_$i"] = negative_electrode_concentration[i]
            concentrations["positive_electrode_concentration_$i"] = positive_electrode_concentration[i]
            concentrations["electrolyte_concentration_$i"] = electrolyte_concentration[i]
        end

        # Write potential datasets
        for i in 1:number_of_states[1]
            potentials["negative_electrode_potential_$i"] = negative_electrode_potential[i]
            potentials["positive_electrode_potential_$i"] = positive_electrode_potential[i]
            potentials["electrolyte_potential_$i"] = electrolyte_potential[i]
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
    output = runP2DBattery.runP2DBatt(input_file_name);

    if isfile(input_file_name)
        rm(input_file_name)  # Delete the file
        println("File deleted successfully.")
    else
        println("File does not exist.")
    end

    create_hdf5_output_file(output,"results/$output_path_name.h5")

    hdf5_data = read("results/$output_path_name.h5")

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