#################################################################
# Stage 1: Base environment for both development and production
#################################################################

# pull latest julia image
FROM julia:latest AS base

# Set working direction to api
WORKDIR /api

# Install asyncapi generator (html generator for documentation) and dependencies
RUN apt-get update && \
    apt-get install -y curl gnupg git && \
    curl -fsSL https://deb.nodesource.com/setup_18.x | bash - && \
    apt-get install -y nodejs && \
    npm install -g @asyncapi/cli

# Generate the HTML documentation during the build
COPY docs /api/docs
RUN asyncapi generate fromTemplate /api/docs/asyncapi.yaml @asyncapi/html-template@3.0.0 --use-new-generator -o docs/build

# Setting up the project environment
COPY dependencies.jl /api/dependencies.jl
RUN julia --project=. /api/dependencies.jl

#################################################################
# Stage 2: Development stage
#################################################################

FROM base AS dev


# RUN julia --project=. -e "using Pkg; Pkg.activate(\".\"); Pkg.instantiate(); Pkg.precompile();"

# Copy the remaining needed scripts to the docker image
COPY api.jl .
COPY scripts /api/scripts
RUN mkdir input_files
RUN mkdir results

#################################################################
# Stage 3: Production stage
#################################################################

FROM base AS prod

# Update the linux system and install the compiler needed to create the pre-compilation system image
RUN apt-get update && apt-get install -y g++

# Copy the remaining needed scripts to the docker image
COPY pre-compilation /api/pre-compilation
COPY logs logs
COPY api.jl .
COPY scripts /api/scripts
RUN mkdir input_files
RUN mkdir results

# pre-compilation of the api (Comment out this line during development as it will rebuild every time you change something in api.jl or the 'scripts' folder.)
RUN julia --project=. /api/pre-compilation/buildSysImage.jl