# BattMo - Graphical User Interface (GUI)

[![](./python/resources/images/battmo_logo.png)](https://github.com/BattMoTeam/BattMo.git)
[![](https://zenodo.org/badge/410005581.svg)](https://zenodo.org/badge/latestdoi/410005581)

The Battery Modelling Toolbox (**BattMo**) is a resource for continuum modelling of electrochemical devices in MATLAB. 
It offers users a flexible framework for building fully coupled electrochemical-thermal simulations of electrochemical 
devices using 1D, 2D, or 3D geometries. **BattMo** is implemented in MATLAB and builds on the open-source MATLAB 
Reservoir Simulation Toolbox (MRST) developed at SINTEF. 

Additional information about BattMo on the [BattMo repository](https://github.com/BattMoTeam/BattMo.git)

The **BattMo GUI** is a web-based application build with **streamlit** which offers a user-friendly interface to 
conduct an end to end simulation experience. Each physical quantity needed to define an experimental protocol can be 
modified to suit the user's needs The parameter set thus defined is then used to run the BattMo P2D model. 


## Install & Run the BattMo GUI

BattMo is based on [MRST](https://www.sintef.no/Projectweb/MRST/), which provides a general unstructured grid format,
generic MATLAB automatic differentiation tools and Newton solvers. The MRST code source wil be installed directly via
**git submodules**. To install the GUI you need to correctly install BattMo, you have therefore to clone this repository
with the submodule option `--recurse-submodules`, as follows:

`git clone --recurse-submodules https://github.com/BattMoTeam/BattMo-gui.git`

Then run the streamlit app from a terminal, as follows:

`streamlit run <path_to_directory_with_repo>/BattMo-gui/python/Define_parameters.py`


## Development structure

The **BattMo GUI** is build in python using **streamlit**. 
- The *python* directory contains the streamlit app code and a 
database that stores the parameters used to define an experimental protocol (default values, metadata).
- The *matlab* directory contains the **BattMo** code, currently in MATLAB (might move to Julia during summer 2023). 
This code is called from the *python* section, from the **RunSimulation** class. 

This streamlit app is a multipage app
(cf [streamlit doc](https://docs.streamlit.io/library/get-started/multipage-apps/create-a-multipage-app)).
The first page, and therefore the file to run to start the app, is *Define_parameters.py*. The other pages' start files
are stored in the *pages* directory, as specified in the streamlit documentation. Here below is a brief description
of each page.

- **Define parameters** : Starting page, allows user to define all physical quantities needed to define the desired 
experimental protocol. The parameters and metadata (units, IRIs, values from literature) are stored in a SQLite file
called *BattMo_gui.db*. Once the physical quantities fit the user's need, one must **save** them using the corresponding
widget, which will save the parameters in a json file called *battmo_input* (stored in the matlab directory). 
The *battmo_input* file contains all the parameters' metadata; a second file called *battmo_formatted_input* is also
created, it's the version used as input by the matlab code.


- **Run Simulation** : Allows the user to launch the simulation, based on the parameters saved in the 
*battmo_formatted_input* file. Not accessible from the same page as the parameters definition to optimize software's
performance and make sure that the saved parameters are running.


- **Plot latest results** : Plots the results of the last simulation run, using matplotlib.


- **About** : Description tab, to be improved

## Acknowledgements

Contributors, in alphabetical order

-   Oscar Bolzinger, SINTEF Industry
-   Simon Clark, SINTEF Industry
-   Eibar Flores, SINTEF Industry

BattMo has received funding from the European Union's Horizon 2020
innovation program under grant agreement numbers:

-   875527 HYDRA
-   957189 BIG-MAP
