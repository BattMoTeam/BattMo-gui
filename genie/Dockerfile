# pull latest julia image
FROM julia:latest

RUN useradd --create-home --shell /bin/bash genie


RUN mkdir /home/genie/app
#COPY . /home/genie/app
COPY deps.jl /home/genie/app
COPY Manifest.toml /home/genie/app
COPY Project.toml /home/genie/app

WORKDIR /home/genie/app

RUN apt-get update && apt-get install -y g++

RUN chown -R genie:genie /home/
USER genie

RUN julia --project=. -e "using Pkg; Pkg.activate(\".\"); Pkg.instantiate(); Pkg.precompile();"
RUN julia --project=. -e 'println("Current project: $(Base.active_project())")'


RUN julia --project=. /home/genie/app/deps.jl
RUN julia --project=. -e "using Pkg; Pkg.activate(\".\"); Pkg.instantiate(); Pkg.precompile();"



# Copy application files
COPY --chown=genie:genie compiled /home/genie/app/compiled

# Ensure the directory is owned by the genie user
RUN chown -R genie:genie /home/genie/app/compiled

# Switch to the genie user before running the Julia command
USER genie


RUN julia --project=. /home/genie/app/compiled/make.jl
ENV JULIA_DEPOT_PATH "/home/genie/.julia"
ENV JULIA_REVISE="off"
ENV EARLYBIND "true"

COPY --chown=genie:genie app /home/genie/app
COPY --chown=genie:genie bin /home/genie/app


# Copy compiled files
# COPY --chown=genie:genie compiled /home/genie/app/compiled

# RUN julia --project=. /home/genie/app/compiled/compile_run_battery.jl
# RUN julia -e "using Pkg; Pkg.activate(\".\"); Pkg.instantiate(); Pkg.precompile();"

# # Compile app
# RUN julia --project=. /home/genie/app/compiled/make.jl








# Set working directory
# WORKDIR /app
# Install required packages
# RUN apt-get update \
#     && apt-get install -y \
#     build-essential \
#     vim \
#     tmux \
#     unzip \
#     cmake \
#     && apt-get clean
# Copy manifest and project files
# COPY Manifest.toml Project.toml ./


# # Install and precompile Julia packages
# RUN julia --project=. -e 'import Pkg; Pkg.instantiate(); Pkg.precompile()'

# # Add PackageCompiler to project environment
# RUN julia --project=. -e 'import Pkg; Pkg.add("PackageCompiler"); Pkg.precompile()'

# # Activate project directory
# RUN julia --project=. -e 'import Pkg; Pkg.activate(".")'







# Set final command
#CMD [ "bin/server" ]



































# FROM --platform=linux/amd64 julia:latest

# # # create dedicated user
# # RUN useradd --create-home --shell /bin/bash genie

# # # set up the app
# WORKDIR /app


# # RUN mkdir /home/genie/app
# # COPY Manifest.toml .
# # COPY Project.toml .


# # C compiler for PackageCompiler
# RUN apt-get update && apt-get install -y g++

# # # configure permissions
# # RUN chown -R genie:genie /home/

# # RUN touch bin/repl  # Create an empty file
# # RUN touch bin/server  # Create an empty file
# # RUN touch bin/runtask  # Create an empty file
# # RUN chmod +x bin/repl

# # RUN chmod +x bin/runtask

# # # switch user
# # USER genie

# # instantiate Julia packages
# RUN julia -e "using Pkg; Pkg.activate(\".\"); Pkg.instantiate(); "

# COPY compiled compiled
# # configure permissions
# # RUN chown -R genie:genie /home/
# # RUN find /home/genie/app/compiled -type f -exec chmod +x {} \;

# # Compile app
# RUN julia --project compiled/make.jl

# COPY . .
# RUN chmod +x bin/server

# # # configure permissions
# # RUN chown -R genie:genie /home/

# # ports
# EXPOSE 8000
# EXPOSE 80

# # set up app environment
# ENV JULIA_DEPOT_PATH ".julia"
# ENV GENIE_ENV "prod"
# ENV GENIE_HOST "0.0.0.0"
# ENV PORT "8000"
# ENV WSPORT "8000"
# ENV EARLYBIND "true"

# # run precompiled image
# CMD ["bin/server"]

# # or maybe include a Julia file
# # CMD julia -e 'using Pkg; Pkg.activate("."); include("IrisClustering.jl"); '
