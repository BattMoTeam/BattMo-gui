# pull latest julia image
FROM julia:latest

# Install required packages
RUN apt-get update \
    && apt-get install -y \
    build-essential \
    vim \
    tmux \
    unzip \
    cmake \
    && apt-get clean

# Set working directory
WORKDIR /app

# Copy manifest and project files
COPY Manifest.toml Project.toml ./

# Install and precompile Julia packages
RUN julia --project=/app -e 'import Pkg; Pkg.instantiate(); Pkg.precompile()'

# Add PackageCompiler to project environment
RUN julia --project=/app -e 'import Pkg; Pkg.add("PackageCompiler"); Pkg.precompile()'

# Copy compiled files
COPY compiled compiled

# Activate project directory
RUN julia --project=/app -e 'import Pkg; Pkg.activate(".")'

# Install PackageCompiler package
RUN julia -e 'import Pkg; Pkg.add("PackageCompiler")'
RUN julia -e 'import Pkg; Pkg.add("Genie")'
RUN julia -e 'import Pkg; Pkg.add("HTTP")'
RUN julia -e 'import Pkg; Pkg.add("JLD2")'
RUN julia -e 'import Pkg; Pkg.add("JSON")'
RUN julia -e 'import Pkg; Pkg.add("UUIDs")'
RUN julia -e 'import Pkg; Pkg.add("ZipFile")'
RUN julia -e 'import Pkg; Pkg.add("LoggingExtras")'
RUN julia -e 'using Pkg; Pkg.add(PackageSpec(;url="https://github.com/BattMoTeam/BattMo.jl.git", rev="cccv"))'

# Compile app
RUN julia compiled/make.jl

# Copy application files
COPY app .

COPY bin .

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
