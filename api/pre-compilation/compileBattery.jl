using HTTP
using HTTP.WebSockets
using UUIDs
using JSON
using HDF5
using Base.Threads: ReentrantLock, lock, unlock, @async, wait, Condition
using BattMo
using Logging
using Jutul

include("../scripts/webSocket.jl")
include("../scripts/apiDocumentation.jl")
include("../scripts/runSimulation.jl")
include("../scripts/runBattMo.jl")
include("../scripts/hdf5Formatting.jl")

json_input_data = nothing
json_battmo_input = nothing
input_file_path = "./exampleInput.json"
output_file_path = nothing
stop_condition = nothing
ws = nothing
run_simulation( input_file_path, output_file_path,ws)