# make.jl
using PackageCompiler

include("packages.jl")

# Get the directory of the make.jl script
script_dir = dirname(@__FILE__)

# Specify the output path for the sysimg.so file relative to the script directory
sysimage_path = joinpath(script_dir, "sysimg.so")

println("Sysimage path: ", sysimage_path)

PackageCompiler.create_sysimage(
  PACKAGES,
  sysimage_path = "/app/compiled/sysimg.dylib",
  precompile_execution_file="/app/compiled/compile_run_battery.jl",
  cpu_target = PackageCompiler.default_app_cpu_target(),
  sysimage_build_args = Cmd(["-O2"])
)

println("End: Sysimg creation complete.")