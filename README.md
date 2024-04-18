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

## Using the application

The BattMo application can very easily be used on [app.batterymodel.com](http://app.batterymodel.com/). If you'd rather use the application offline, it can be installed using Docker. If you'd like to install for development, see the next section called 'Developer installation'. The BattMo GUI is available as a set of Docker images in the Github container registry and can be found among BattMoTeam's packages. In order to use it you have to install Docker and Docker Compose. See the [Docker website](https://www.docker.com/) for more information about Docker and how to install it. Assuming you have both Docker and Docker Compose installed on your machine:

Open a bash terminal and pull the latest Docker images from the registry. For the streamlit image that represents the frontend:
```<bash>
docker pull ghcr.io/battmoteam/battmogui_streamlit:latest
```
For the genie Docker image that serves as an api and runs the BattMo.jl package:
```<bash>
docker pull ghcr.io/battmoteam/battmogui_genie:latest
```
And for the production server Nginx:
```<bash>
docker pull ghcr.io/battmoteam/battmogui_nginx:latest
```
Run the images in containers by using a docker compose file. Create a docker-compose.yml file with the following content:
```<docker>
version: "3.3"

services:

  genie:
    image: ghcr.io/battmoteam/battmogui_genie:latest
    build: ./genie
    container_name: genie
    restart: always
    ports:
      - "8000:8000"
    volumes:
      - ./genie:/home/genie/app
    command: julia --project=. -e 'include("app/rest.jl")' --color=yes --depwarn=no --project=@. --sysimage="/home/sysimage.so" -q -i -- $$(dirname $$0)/../bootstrap.jl -s=true "$$@"

  nginx:
    image: ghcr.io/battmoteam/battmogui_nginx:latest
    build: ./nginx
    container_name: nginx
    restart: always
    ports:
      - "8001:8001"
      - "8002:8002"
    volumes:
      - ./nginx:/app

    depends_on:
      - genie
      - streamlit
 
  streamlit:
    image: ghcr.io/battmoteam/battmogui_streamlit:latest
    build: ./streamlit
    container_name: streamlit
    restart: always
    ports:
      - "8501:8501"
    volumes:
      - ./streamlit:/app
    depends_on:
      - genie

    command: streamlit run Introduction.py --global.disableWidgetStateDuplicationWarning true --server.port=8501
```
Now run the following command to start the containers:
```<bash>
docker-compose up -d
```

Now you can open your browser and go to 'localhost:8501' where the GUI should be visible and ready to use.

## Developer installation

If you'd like to install the BattMo application for development you need to have both Docker and Docker Compose installed on your computer. See the [Docker website](https://www.docker.com/) for more information about Docker and how to install it. Assuming you have both Docker and Docker Compose installed on your machine:

Clone the repository:
```<git>
git clone https://github.com/BattMoTeam/BattMo-gui.git
```

No the only thing you have to do in order to run the application is to build the images and run the docker containers using Docker Compose. The building setup for the development environment can be found in the file 'docker-compose.yml'. To build the images, go into the BattMo-GUI directory in your terminal and run:

```<bash>
docker-compose build
```

The first build can take up to 20 minutes to finish. After that, it takes a couple of seconds depending on the changes you make during development. To run the containers/application:

```<bash>
docker-compose up -d
```

Now you can go to 'Localhost:8501' in your browser in order to visualize and use the web-application.

After changing anything in the streamlit folder, in order to see the changes in the application you can run:

```<bash>
docker restart streamlit
```

After changing anything in the genie folder, in order to see the changes in the application you can run:

```<bash>
docker restart genie
```

When changing anything in the recources and database, or in the Julia system image building setup, make sure to rebuild the images again instead of only restarting certain containers.

## Development structure

The **BattMo GUI** is build in python using **streamlit**. 
- The *streamlit* directory contains the streamlit app code and a 
database that stores the parameters used to define an experimental protocol (default values, metadata).
- The *genie* directory contains the Julia backend code that uses the Genie framework to create a rest-api. This api enables data transfer between the **BattMo** package and the streamlit frontend and starts a simulation upon receiving input data from the streamlit frontend.

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
