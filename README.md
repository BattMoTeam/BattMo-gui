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

Clone the repository:
```<git>
git clone https://github.com/BattMoTeam/BattMo-gui.git
```

Within your environment, go in the BattMo-gui directory and install the required python packages, as follows:

```<powershell>
cd BattMo-gui; pip install -r requirements.txt
```

Initiate the Julia terminal in the command prompt and install the Julia packages:

```<powershell>
julia
```
```<Julia>
using Pkg; Pkg.add(["BattMo@0.1.6","Jutul@0.2.14","LoggingExtras@1.0.3", "JSON@0.21.4","PythonCall@0.9.14"])
```
Now the GUI can be run from 2 different terminals:

1. One for the Flask api running on the background. Initiate the flask server in a command prompt:

```<powershell>
python api.py
```
    
2. One to initiate the streamlit interface. Iniate the streamlit server in another command prompt:

```<powershell>
streamlit run python\Introduction.py
```



## Development structure

The **BattMo GUI** is build in python using **streamlit**. 
- The *python* directory contains the streamlit app code and a 
database that stores the parameters used to define an experimental protocol (default values, metadata).
- The *BattMoJulia* directory contains the **BattMo** code, in Julia. 
This code is called from the *api.py* file that initiates a Flask server on which the BattMo package will be executed. 

This streamlit app is a multipage app
(cf [streamlit doc](https://docs.streamlit.io/library/get-started/multipage-apps/create-a-multipage-app)).
The first page, and therefore the file to run to start the app, is *Introduction.py*. The other pages' start files
are stored in the *pages* directory, as specified in the streamlit documentation. Here below is a brief description
of each page.

- **Introduction** : The starting page, gives an introduction to the app. It provides a description on BattMo, a nevigation to the other pages, and links to more information and documentation.

- **Simulation** : Allows user to define all physical quantities needed to define the desired 
experimental protocol. The parameters and metadata (units, IRIs, values from literature) are stored in a SQLite file
called *BattMo_gui.db*. Once the physical quantities fit the user's need, one must **UPDATE** them using the corresponding
widget, which will save the parameters in a json file called *battmo_input* (stored in the BattMoJulia directory). 
The *battmo_input* file contains all the parameters' metadata; a second file called *battmo_formatted_input* is also
created, it's the version used as input by the Julia code. After updating the parameters, the user can click on the **RUN** button to launch the simulation, based on the parameters saved in the *battmo_formatted_input* file.

- **Results** : Plots the results of the last simulation run, using matplotlib.

- **Materials and models**: Provides more information on the models and materials that can be selected.


## Acknowledgements

Contributors, in alphabetical order

-   Oscar Bolzinger, SINTEF Industry
-   Simon Clark, SINTEF Industry
-   Eibar Flores, SINTEF Industry
-   Lorena Hendrix, SINTEF Industry

BattMo has received funding from the European Union's Horizon 2020
innovation program under grant agreement numbers:

-   875527 HYDRA
-   957189 BIG-MAP
