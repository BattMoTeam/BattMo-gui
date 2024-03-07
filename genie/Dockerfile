# pull latest julia image
FROM julia:latest

RUN apt-get update \
    && apt-get install -y g++\
    build-essential \
    vim \
    tmux \
    unzip \
    cmake \
    && apt-get clean

WORKDIR /app

RUN chmod +x /app

ADD deps.jl deps.jl

RUN julia deps.jl

COPY compiled compiled

# Compile app
RUN julia compiled/make.jl --verbose

COPY app .


CMD [ "bin/server" ]



































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
