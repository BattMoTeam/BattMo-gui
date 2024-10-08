
println("Current project genie: $(Base.active_project())")
println("BattMo loaded")
using Genie, Genie.Renderer.Json, Genie.Requests, Genie.Router, Genie.Assets
using HTTP
using HTTP.WebSockets
using UUIDs
using JSON
using HDF5
using Base.Threads: ReentrantLock, lock, unlock, @async, wait, Condition
using SwagUI
using SwaggerMarkdown


include("runP2DBattery.jl")


# Set the host explicitly
Genie.config.run_as_server = true
Genie.config.server_host = "0.0.0.0"
Genie.config.cors_allowed_origins = ["*"]




# Initialize lock
const simulation_lock = ReentrantLock()
const simulations = Dict{String, Tuple{Task, Condition}}()
const clients = Dict{UUID, HTTP.WebSockets.WebSocket}()


#############################################################################
# Websocket 
#############################################################################

function handle_websocket(ws::WebSocket)
    try
        for msg in ws
            # Attempt to read a message from the WebSocket
            # input_data = WebSockets.receive(ws)
            if msg === nothing
                break  # Exit the loop if no message is received (end of stream)
            end
            
            parsed_data = JSON.parse(msg)
            client_id_str = parsed_data["user_id"]
            client_id = UUID(client_id_str)
            clients[client_id] = ws

            # Handle "start_simulation" command
            if haskey(parsed_data, "command") && parsed_data["command"] == "start_simulation"

                println("Received JSON input data with id: ", client_id_str)
                WebSockets.send(ws, "UUID: $client_id_str")

                # Create a file name with the UUID
                input_file_name = "$client_id_str.json"
                output_path_name = "$client_id_str.h5"
                input_file_path = "input_files/$input_file_name"
                output_file_path = "results/$output_path_name"

                json_input_data = parsed_data["parameters"]
                
                # Write the JSON data to the file
                open(input_file_path, "w") do temp_input_file
                    JSON.print(temp_input_file, json_input_data)
                end

                stop_condition = Condition()

                # Spawn a new thread to handle the simulation
                simulation_thread = @async run_simulation(input_file_path, output_file_path, stop_condition,ws)

                # Store the simulation thread and condition variable
                # simulations[client_id_str] = (simulation_thread, stop_condition)

                # Inform the client that the simulation has started
                # WebSockets.send(ws, "Simulation started with ID: $uuid_str_out")

                # Polling to wait until the file is ready
                
                max_retries = 600
                sleep_interval = 0.1
                retries = 0

                while !isfile(output_file_path) && retries < max_retries
                    sleep(sleep_interval)
                    retries += 1

                    # WebSockets.send(ws, "Simulation progress: $((retries / max_retries) * 100)")
                end

                if retries >= max_retries
                    WebSockets.send(ws, "Simulation timed out or failed.")
                    WebSockets.close(ws)  # Ensure the WebSocket is closed 
                end

                # Clean up: remove the input file
                if isfile(input_file_path)
                    rm(input_file_path)  # Delete the file
                    println("File deleted successfully.")
                else
                    println("File does not exist.")
                end

                # Once the file is ready, read it and return the response
                open(output_file_path, "r") do hdf5_file
                    hdf5_data = read(hdf5_file)
                    WebSockets.send(ws, hdf5_data)
                end

                # WebSockets.send(ws, "Simulation complete! HDF5 data has been sent.")
                # WebSockets.send(ws, "Simulation complete! HDF5 data (ID: $client_id_str) has been sent.")

                rm(output_file_path)

                WebSockets.close(ws)  # Ensure the WebSocket is closed

            # Handle "stop_simulation" command
            elseif haskey(parsed_data, "command") && parsed_data["command"] == "stop_simulation"

                uuid = parsed_data["uuid"]
                if haskey(simulations, uuid)
                    task, stop_condition = simulations[uuid]

                    # Signal the task to stop
                    lock(simulation_lock) do
                        notify(stop_condition)
                    end

                    # Wait for the task to complete
                    wait(task)
                    delete!(simulations, uuid)

                    WebSockets.send(ws, JSON.json(Dict("status" => "stopped", "uuid" => uuid)))
                else
                    WebSockets.send(ws, JSON.json(Dict("status" => "error", "message" => "No simulation found with ID $uuid")))
                end
            end
        end
    catch e
        println("Error handling WebSocket: ", e)
        WebSockets.send(ws, "Error handling WebSocket: ", e)
    finally
        WebSockets.close(ws)  # Ensure the WebSocket is closed
    end
end

function start_websocket_server()
    ws_port = 8081
    HTTP.WebSockets.listen!("0.0.0.0", ws_port) do ws
        handle_websocket(ws)
    end
end

start_websocket_server()


#############################################################################
# Run BattMo simulation
#############################################################################


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

function run_simulation(input_file_path, output_path_path, stop_condition::Condition, ws::WebSocket)

    try
        output = runP2DBattery.runP2DBatt(input_file_path,ws);

        print("....", output[2])

        lock(simulation_lock) do
            create_hdf5_output_file(output,output_path_path)
        end

    catch e
        @error "Simulation error: $e"

    finally
        lock(simulation_lock) do
            notify(stop_condition)
        end

    end

end

#############################################################################
# Build a AsyncAPI document
#############################################################################

# Get the path of the directory where the current script is located
current_dir = @__DIR__

# Set the static directory to the docs/html folder of the first app directory
static_dir = abspath(joinpath(current_dir, "..", "docs", "html"))  # This should resolve to /home/genie/app/docs/html

println("Current Directory: $current_dir")
println("Static Directory: $static_dir")
println("Starting server...")

# Function to serve static files
function serve_file(req::HTTP.Request)
    # Log when the function is called
    println("Received request for: ", req.target)

    # Extract the requested file path from the URL
    file_path = HTTP.URIs.path(req.target)

    # If no specific file is requested, serve index.html
    if file_path == "/"
        file_path = "/index.html"  # Serve index.html if no specific file is requested
    end

    # Construct the full path to the file
    full_path = joinpath(static_dir, file_path)

    # Log the constructed path
    println("Full path: $full_path")

    # Check if the file exists
    if isfile(full_path)
        println("File found: $full_path")
        mime_type = HTTP.MIMETypes.getmime(full_path)

        # Read the file content
        content = read(full_path)
        println("Serving: $full_path with MIME type: $mime_type")
        return HTTP.Response(200, content, Dict("Content-Type" => mime_type))
    else
        println("File not found: $full_path")
        return HTTP.Response(404, "File not found")
    end
end

# Start the HTTP server
HTTP.serve(serve_file, "0.0.0.0", 8080)