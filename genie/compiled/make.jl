

# make.jl
using PackageCompiler, Logging

#include("packages.jl")

# Get the directory of the make.jl script
script_dir = dirname(@__FILE__)

# Specify the output path for the sysimg.so file relative to the script directory
sysimage_path = joinpath(dirname(dirname(dirname(script_dir))), "sysimage.so")
println("sysimage_path.=",sysimage_path)
example_path = joinpath(script_dir, "compile_run_battery.jl")
project_path = dirname(script_dir)
# Set up logging configuration
global_logger(Logging.SimpleLogger(stdout, Logging.Debug))

# Now you can use logging functions in your script
@info "Starting sysimage creation process"

open("compiler_log.txt", "w") do io
	redirect_stdout(io) do
		# Create the system image
		create_sysimage([:LoggingExtras,:Genie,:BattMo,:HTTP,:JSON,:UUIDs,:HDF5];
		sysimage_path = sysimage_path,
		project = project_path,
		precompile_execution_file=example_path,
		cpu_target = "generic;native,sandybridge,-xsaveopt,clone_all;haswell,-rdrnd,base(1)")
		#cpu_target="generic")
		#cpu_target = PackageCompiler.default_app_cpu_target())
	end
end
# Print additional debug information if needed
@debug "Debug message here"

@info "Sysimage creation process completed"
