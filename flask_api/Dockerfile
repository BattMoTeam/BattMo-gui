FROM python:3.11.4

WORKDIR /app


RUN pip install jill --no-cache-dir

RUN jill install 1.9.2 --confirm

# Helpful Development Packages
RUN julia -e 'using Pkg; Pkg.add(PackageSpec(;name = "BattMo",version = "0.1.6"))'
RUN julia -e 'using Pkg; Pkg.add(PackageSpec(;name = "Jutul",version = "0.2.14"))'
#RUN julia -e 'using Pkg; Pkg.add(PackageSpec(;url="https://github.com/BattMoTeam/BattMo.jl.git", rev="refac"))'
#RUN julia -e 'using Pkg; Pkg.add(PackageSpec(;name = "Jutul",version = "0.2.14"))'
RUN julia -e 'using Pkg; Pkg.add(PackageSpec(;name = "LoggingExtras",version = "1.0.3"))'
RUN julia -e 'using Pkg; Pkg.add(PackageSpec(;name = "PythonCall",version = "0.9.14"))'
RUN julia -e 'using Pkg; Pkg.add(PackageSpec(;name = "JSON",version = "0.21.4"))'
RUN julia -e 'using Pkg; Pkg.add(PackageSpec(;name = "PrettyTables",version = "2.2.7"))'

COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt
COPY results /app/results
COPY . .
