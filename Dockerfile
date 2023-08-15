FROM python:3.11.4

WORKDIR /app

RUN pip install julia jill ipython Flask juliacall redis streamlit Pylance --no-cache-dir
# julia is pyjulia, our python-julia interface
# jill is a python package for easy Julia installation
# IPython is helpful for magic (both %time and %julia)
# Include these in your requirements.txt if you have that instead

RUN jill install 1.9.2 --confirm

# PyJulia setup (installs PyCall & other necessities)
RUN python -c "import julia; julia.install()"

# Helpful Development Packages
RUN julia -e 'using Pkg; Pkg.add(["BattMo", "Jutul"])'