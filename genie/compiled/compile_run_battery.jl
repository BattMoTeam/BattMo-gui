using BattMo
using Genie, Genie.Renderer.Json, Genie.Requests
using HTTP
using UUIDs
using JSON
using ZipFile
using Logging
using JLD2

# Get the directory of the make.jl script
script_dir = dirname(@__FILE__)

# Specify the output path for the sysimg.so file relative to the script directory
json_path = joinpath(script_dir, "p2d_40_cccv.json")

json_file = JSONFile(json_path)
states, reports, extra = run_battery(json_file, extra_timing = false);