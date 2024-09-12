include("runP2DBattery.jl")

input_file_name = "C:/Users/lorenah/Documents/Repositories/BattMo-gui/genie/app/test1.json"

log_file = "simulation_log.log"  # Define the log file name
open(log_file, "w") do file

    redirect_stdout(file)
    redirect_stderr(file)

    output = runP2DBattery.runP2DBatt(input_file_name);

end