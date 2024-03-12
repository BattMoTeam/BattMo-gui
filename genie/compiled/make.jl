

# make.jl
using PackageCompiler

#include("packages.jl")

# Get the directory of the make.jl script
script_dir = dirname(@__FILE__)

# Specify the output path for the sysimg.so file relative to the script directory
sysimage_path = joinpath(script_dir,"sysimg.so")
example_path = joinpath(script_dir, "compile_run_battery.jl")
project_path = joinpath(dirname(script_dir))

println("Sysimage path: ", sysimage_path)

# Create the system image
create_sysimage([:LoggingExtras,:Genie];
	sysimage_path = sysimage_path,
	project = project_path,
	precompile_execution_file=example_path)

println("End: Sysimg creation complete.")