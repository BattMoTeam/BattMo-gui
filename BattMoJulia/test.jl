# using BattMo; states, reports, extra = run_battery_1d(filename = "p2d_40_jl.json", info_level = -1, end_report = true, extra_timing = false)
using BattMo, Jutul, JSON, PythonCall, Logging, LoggingExtras


json_file = "C:\\Users\\lorenah\\Documents\\Software\\BattMo-gui\\BattMo-gui\\BattMoJulia\\battmo_formatted_input.json"
json_file = JSONFile(json_file)


# Create a custom IOBuffer to capture log messages
log_buffer = IOBuffer()

# Redirect the logger to use the custom IOBuffer
global_logger(ConsoleLogger(log_buffer))


# Function to capture log messages
function capture_logs(json_file)
    log_messages = String[]
    

    try
        
        print("Calling BattMo simulation")
        
        #states, reports, extra = runBattery_1d(input = jsondict, info_level = 0, extra_timing = false);
        states, reports, extra = run_battery(json_file, info_level = -1, end_report = true, extra_timing = false);
        print("Simulation finished")
        
        con = BattMo.Constants()
    finally
        # Capture log messages
        seekstart(log_buffer)
        log_messages = split(String(take!(log_buffer)), "\n")
        close(log_buffer)
    end
    return log_messages
end

log_messages = capture_logs(json_file)

# Display the non-empty log messages
for message in log_messages
    println(message)
end
# Get some result values


# macro my_warn(msg)
#     Logging.warn(logger, msg)
# end

# @my_warn(logger)


#negative_electrode_concentration = Array([[state[:NAM][:Cs] for state in states]]/1000)

# for i in 1:length(negative_electrode_concentration)-1
#     for j in 1:9
#         negative_electrode_concentration[i,j,j] = negative_electrode_concentration[i,j,j]

#     end

# end

# negative_electrode_concentration = cat(negative_electrode_concentration, dims = 2)

# negative_electrode_concentration = reshape(negative_electrode_concentration,10,10,:)