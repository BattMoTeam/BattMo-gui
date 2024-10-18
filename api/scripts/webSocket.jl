#############################################################################
# Websocket 
#############################################################################

export start_websocket_server

function handle_websocket(ws::WebSocket)
    current_dir = @__DIR__
    log_path = abspath(joinpath(current_dir, "..", "logs", "websocket.log"))

    open(log_path, "w") do file
        redirect_stdout(file)
        redirect_stderr(file)

        try
            log_buffer = IOBuffer()
            global_logger(ConsoleLogger(log_buffer))

            for msg in ws
                if msg === nothing
                    break  # Exit the loop if no message is received (end of stream)
                end
                
                parsed_data = JSON.parse(msg)
                client_id_str = parsed_data["user_id"]
                client_id = UUID(client_id_str)
                clients[client_id] = ws

                operation = parsed_data["operation"]
                if haskey(parsed_data, "operation") && parsed_data["operation"] == "run_simulation"
                    println("Received JSON input data with id: ", client_id_str)
                    WebSockets.send(ws, "UUID: $client_id_str")

                    input_file_name = "$client_id_str.json"
                    output_path_name = "$client_id_str.h5"
                    input_file_path = "input_files/$input_file_name"
                    output_file_path = "results/$output_path_name"

                    json_input_data = parsed_data["parameters"]
                    open(input_file_path, "w") do temp_input_file
                        JSON.print(temp_input_file, json_input_data, 3)
                    end
                    println("Received JSON input data with id: ", client_id_str)
                    simulation_thread = @async run_simulation(input_file_path, output_file_path, ws)

                    max_retries = 600
                    sleep_interval = 0.1
                    retries = 0
                    while_loop = true

                    while !isfile(output_file_path) && while_loop
                        sleep(sleep_interval)
                        retries += 1
                    end

                    # if retries >= max_retries
                    #     if !ws.writeclosed
                    #         WebSockets.send(ws, "Simulation timed out or failed.")
                    #         WebSockets.close(ws)
                    #     end
                    #     return  # Stop further execution
                    # end

                    if !ws.writeclosed
                        WebSockets.send(ws, "Simulation finished.")
                    end

                    if isfile(input_file_path)
                        rm(input_file_path)
                        println("File deleted successfully.")
                    else
                        println("File does not exist.")
                    end

                    open(output_file_path, "r") do hdf5_file
                        hdf5_data = read(hdf5_file)
                        if !ws.writeclosed
                            WebSockets.send(ws, hdf5_data)
                        end
                    end

                    rm(output_file_path)

                    WebSockets.close(ws)  # Ensure the WebSocket is closed
                end
            end
        catch e
            println("Error handling WebSocket: ", e)
            println("Stacktrace: ", stacktrace())
            if !ws.writeclosed
                WebSockets.send(ws, "Error handling WebSocket: $(e)")
            end
        finally
            if !ws.writeclosed
                WebSockets.close(ws)
            end
        end
    end
end


function start_websocket_server(ws_port::Int)
    HTTP.WebSockets.listen!("0.0.0.0", ws_port) do ws
        handle_websocket(ws)
    end
end