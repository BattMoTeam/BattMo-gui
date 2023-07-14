
import julia
import matplotlib as plt
import numpy as np


#Initialize Julia (only needed for first execution)
#julia.install()
from julia.api import Julia
jl = Julia(compiled_modules=True)
#Import the Julia module
from julia import Main

#Add the BattMo,jl code directory to the Julia module path
Main.eval('push!(LOAD_PATH, "BattMoJulia")')

###Include julia file that is a function that runs the simulation with the input  parameters###
Main.include("BattMoJulia/runP2DBattery.jl")

#Path to input parameters
#path_input = "matlab/battmo_formatted_input.json"

#Call Julia function
output = Main.runP2DBattery("BattMoJulia\p2d_40_jl.json")



#print(max(output))


# print("time = ",time)
# print("E = ",E)


