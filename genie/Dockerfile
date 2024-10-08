# pull latest julia image
FROM julia:latest

RUN useradd --create-home --shell /bin/bash genie


RUN mkdir /home/genie/app
#COPY . /home/genie/app
COPY deps.jl /home/genie/app
COPY Project.toml /home/genie/app
COPY Manifest.toml /home/genie/app
COPY docs /home/genie/app/docs



WORKDIR /home/genie/app

RUN apt-get update && apt-get install -y g++

# Install curl to download Node.js setup script
RUN apt-get update && \
    apt-get install -y curl gnupg git && \
    curl -fsSL https://deb.nodesource.com/setup_18.x | bash - && \
    apt-get install -y nodejs && \
    npm install -g @asyncapi/cli


# Generate the HTML documentation during the build
# RUN asyncapi generate fromFile /home/genie/app/docs/asyncapi.yaml @asyncapi/html-template -o /home/genie/app/docs/html
RUN asyncapi generate fromTemplate /home/genie/app/docs/asyncapi.yaml @asyncapi/html-template -o docs/html

# Print the contents of the generated HTML folder to confirm files were created
RUN echo "Contents of the generated HTML folder:" && ls -l /home/genie/app/docs/html

RUN chown -R genie:genie /home/
RUN chown -R genie:genie /home/genie/app/docs/html

USER genie

# Print the contents of the generated HTML folder to confirm files were created
RUN echo "Contents of the generated HTML folder:" && ls -l /home/genie/app/docs/html

RUN julia --project=. -e "using Pkg; Pkg.activate(\".\"); Pkg.instantiate(); Pkg.precompile();"
RUN julia --project=. -e 'println("Current project: $(Base.active_project())")'


RUN julia --project=. /home/genie/app/deps.jl
RUN julia --project=. -e "using Pkg; Pkg.activate(\".\"); Pkg.instantiate(); Pkg.precompile();"

# # Build AsyncApi html file
# COPY --chown=genie:genie docs/asyncapi.yaml /home/genie/app/docs/asyncapi.yaml
# RUN julia --project=. -e 'using NodeJS; npm = string(NodeJS.npm_cmd()); node = string(NodeJS.nodejs_cmd());node_path = dirname(node); ENV["PATH"] = node_path * ":" * ENV["PATH"]; run(`$npm install -g @asyncapi/generator`); ag = joinpath(dirname(npm), "../lib/node_modules/@asyncapi/generator/cli.js"); run(`$node $ag -o /home/genie/app/docs -t @asyncapi/html-template /home/genie/app/docs/asyncapi.yaml`)'


# Copy application files
COPY --chown=genie:genie compiled /home/genie/app/compiled

# Ensure the directory is owned by the genie user
RUN chown -R genie:genie /home/genie/app/compiled

# Switch to the genie user before running the Julia command
# USER genie

RUN julia --project=. /home/genie/app/compiled/make.jl
ENV JULIA_DEPOT_PATH "/home/genie/.julia"
ENV JULIA_REVISE="off"
ENV EARLYBIND "true"

COPY --chown=genie:genie app /home/genie/app/app
COPY --chown=genie:genie bin /home/genie/app/bin
RUN mkdir /home/genie/app/results
RUN mkdir /home/genie/app/input_files
# COPY --chown=genie:genie results /home/genie/app/results
# COPY --chown=genie:genie input_files /home/genie/app/input_files














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
