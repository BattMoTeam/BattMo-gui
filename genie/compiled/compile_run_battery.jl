using BattMo
using Jutul
using Genie, Genie.Renderer.Json, Genie.Requests
using HTTP
using UUIDs
using JSON
using ZipFile
using Logging
using JLD2

 

# Get the directory of the make.jl script
script_dir = dirname(@__FILE__)
module_path = "runP2DBattery.jl"
println(module_path)

include(module_path)

# Specify the output path for the sysimg.so file relative to the script directory
json_path = joinpath(script_dir, "p2d_40_cccv.json")

runP2DBattery.runP2DBatt(json_path);