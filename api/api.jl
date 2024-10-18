using HTTP
using HTTP.WebSockets
using UUIDs
using JSON
using HDF5
using Base.Threads: ReentrantLock, lock, unlock, @async, wait, Condition
using BattMo
using Logging
using Jutul

include("scripts/webSocket.jl")
include("scripts/apiDocumentation.jl")
include("scripts/runSimulation.jl")
include("scripts/runBattMo.jl")
include("scripts/hdf5Formatting.jl")

# Initialize lock
const simulation_lock = ReentrantLock()
const simulations = Dict{String, Tuple{Task, Condition}}()
const clients = Dict{UUID, HTTP.WebSockets.WebSocket}()


        
ws_port = 8081
start_websocket_server(ws_port)

doc_port = 8080
start_documentation_server(doc_port)
