FROM python:3.11.4

WORKDIR /BattMo-gui

COPY .devcontainer .devcontainer/
COPY BattMoJulia BattMoJulia/
COPY python python/
COPY results results/



RUN pip install jill Flask flask_restful juliacall Pylance streamlit streamlit_extras numpy flask_restful h5py matplotlib sympy --no-cache-dir
# jill is a python package for easy Julia installation

RUN jill install 1.9.2 --confirm

# Helpful Development Packages
RUN julia -e 'using Pkg; Pkg.add(["Jutul","LoggingExtras","PythonCall", "BattMo","JSON"])'

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
