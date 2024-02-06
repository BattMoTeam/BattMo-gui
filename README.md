# BattMo - Graphical User Interface (GUI)

[![](./python/resources/images/battmo_logo.png)](https://github.com/BattMoTeam/BattMo.git)
[![](https://zenodo.org/badge/410005581.svg)](https://zenodo.org/badge/latestdoi/410005581)

The Battery Modelling Toolbox (**BattMo**) is a resource for continuum modelling of electrochemical devices in MATLAB and Julia. 
It offers users a flexible framework for building fully coupled electrochemical-thermal simulations of electrochemical 
devices using 1D, 2D, or 3D geometries. The original **BattMo** is implemented in MATLAB and builds on the open-source MATLAB 
Reservoir Simulation Toolbox (MRST) developed at SINTEF. BattMo being rewritten in Julia and builds on the open source Julia framework for multiphysics simulators, Jutul.jl. This repository builds further upon BattMo.jl.

Additional information about BattMo on the [BattMo repository](https://github.com/BattMoTeam/BattMo.git)

The **BattMo GUI** is a web-based application build with **streamlit** which offers a user-friendly interface to 
conduct an end to end simulation experience. Each physical quantity needed to define an experimental protocol can be 
modified to suit the user's needs. The parameter set thus defined is then used to run the BattMo P2D model. 

## Docker images

The BattMo GUI is available as a set of Docker images in the Github container registry and can be found among BattMoTeam's packages. In order to use it you have to install Docker. See the [Docker website](https://www.docker.com/) for more information about Docker and how to install it. 

Open a bash terminal and pull the latest Docker images from the registry. For the streamlit image that represents the frontend:
```<bash>
docker pull ghcr.io/battmoteam/battmogui_streamlit:latest
```
For the flask api Docker images that runs the BattMo.jl package:
```<bash>
docker pull ghcr.io/battmoteam/battmogui_flask_api:latest
```
And for the production server Nginx:
```<bash>
docker pull ghcr.io/battmoteam/battmogui_nginx:latest
```
Run the images in containers by using a docker compose file. Create a docker-compose.yml file with the following content:
```<docker>
version: "3"

services:

  flask_api:
    build: ./flask_api
    container_name: flask_api
    restart: always
    ports:
      - "8000:8000"
    command: gunicorn -w 1 -b 0.0.0.0:8000 wsgi:server --timeout 200

  nginx:
    build: ./nginx
    container_name: nginx
    restart: always
    ports:
      - "8001:8001"
    depends_on:
      - flask_api
 
  streamlit:
    build: ./streamlit
    container_name: streamlit
    restart: always
    ports:
      - "8501:8501"

    command: streamlit run Introduction.py --global.disableWidgetStateDuplicationWarning true --server.port=80
```
Now run the following command to start the containers:
```<bash>
docker-compose up
```

Now you can open your browser and go to 'localhost:8501' where the GUI will be visible.

## Install & Run the BattMo GUI

Clone the repository:
```<git>
git clone https://github.com/BattMoTeam/BattMo-gui.git
```

Within your environment, go in the BattMo-gui directory and install the required python packages, as follows:

```<powershell>
cd BattMo-gui; pip install -r streamlit/requirements.txt; pip install -r flask_api/requirements.txt
```

Initiate the Julia terminal in the command prompt and install the Julia packages (see 'Manifest.toml' for the correct versions):

```<powershell>
julia
```
```<Julia>
using Pkg; Pkg.add(["BattMo@0.1.6","Jutul@0.2.14","LoggingExtras@1.0.3", "JSON@0.21.4","PythonCall@0.9.14"])
```
Now the GUI can be run from 2 different terminals:

1. One for the Flask api running on the background. Initiate the flask server in a command prompt:

```<powershell>
python flask_api/wsgi.py
```
    
2. One to initiate the streamlit interface. Iniate the streamlit server in another command prompt:

```<powershell>
streamlit run streamlit/Introduction.py
```

Now you can go to 'Localhost:8501' in your browser in order to visualize and use the web-application.


## Development structure

The **BattMo GUI** is build in python using **streamlit**. 
- The *streamlit* directory contains the streamlit app code and a 
database that stores the parameters used to define an experimental protocol (default values, metadata).
- The *flask_api* directory contains the Julia backend code that runs the **BattMo** package, and the flask code that serves as an api by running the Julia backend code on demand of the streamlit frontend.  

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
