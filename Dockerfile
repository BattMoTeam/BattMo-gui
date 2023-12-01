FROM python:3.11.4

WORKDIR /BattMo-gui

COPY .devcontainer .devcontainer/
COPY BattMoJulia BattMoJulia/
COPY python python/
COPY results results/
COPY Project.toml .
COPY Manifest.toml .
COPY requirements.txt .



RUN pip install jill --no-cache-dir
#Flask juliacall flask_restful Pylance streamlit streamlit_extras numpy flask_restful h5py matplotlib sympy --no-cache-dir
# jill is a python package for easy Julia installation

RUN pip install --no-cache-dir -r requirements.txt

RUN jill install 1.9.2 --confirm

# Helpful Development Packages
#RUN julia -e 'using Pkg; Pkg.add(["Jutul","LoggingExtras","PythonCall","JSON"])'
RUN julia -e 'using Pkg; Pkg.add(PackageSpec(;url="https://github.com/BattMoTeam/BattMo.jl.git", rev="refac"))'
RUN julia -e 'using Pkg; Pkg.add(PackageSpec(;name = "Jutul",version = "0.2.14"))'
RUN julia -e 'using Pkg; Pkg.add(PackageSpec(;name = "LoggingExtras",version = "1.0.3"))'
RUN julia -e 'using Pkg; Pkg.add(PackageSpec(;name = "PythonCall",version = "0.9.14"))'
RUN julia -e 'using Pkg; Pkg.add(PackageSpec(;name = "JSON",version = "0.21.4"))'

#RUN julia -e 'using Pkg; Pkg.instantiate()'
#RUN julia --project=. -e 'using Pkg; Pkg.instantiate()'


#RUN julia -e 'using Pkg; Pkg.add(PackageSpec(;name = "Jutul",version = "0.2.14"))'
RUN julia -e 'using Pkg; Pkg.add(PackageSpec(;name = "PrettyTables",version = "2.2.7"))'
#RUN julia -e 'using Pkg; Pkg.add(url="https://github.com/BattMoTeam/BattMo.jl.git#refac")'

# Copy your application files into the container
#COPY python/Introduction.py python/Introduction.py
COPY api.py api.py


# COPY supervisord.conf   app/supervisord.conf

# ENTRYPOINT [ "python" ]

# # Set the CMD to start both Streamlit and Flask servers
# CMD ["/usr/bin/supervisord", "-c", "app/supervisord.conf"]

COPY runner.sh /scripts/runner.sh

RUN ["chmod", "+x", "/scripts/runner.sh"]
ENTRYPOINT ["/bin/sh","/scripts/runner.sh"]
