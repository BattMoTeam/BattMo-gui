#############################################################################
# Run a simulation
#############################################################################

export run_simulation

function run_simulation(input_file_path, output_path, ws::Union{WebSocket, Nothing}=nothing)
    # Get the path of the directory where the current script is located
    current_dir = @__DIR__

    # define the path for the logging output
    log_path = abspath(joinpath(current_dir, "..", "logs", "run_simulation.log"))

    open(log_path, "w") do file

        redirect_stdout(file)
        redirect_stderr(file)

        try
            # Create a custom IOBuffer to capture log messages
            log_buffer = IOBuffer();

            # Redirect the logger to use the custom IOBuffer
            global_logger(ConsoleLogger(log_buffer));


            output = runBattMo1D(input_file_path,ws);
            println(output[1])
           
            println(output_path)
            
            if output_path !== nothing
                lock(simulation_lock) do
                    println(output_path)
                    create_hdf5_output_file(output,output_path)
                end

            end

        catch e
            @error "Simulation error: $e"

        finally
            if stop_condition !== nothing
                lock(simulation_lock) do
                    notify(stop_condition)
                end
            end

        end
    end

end