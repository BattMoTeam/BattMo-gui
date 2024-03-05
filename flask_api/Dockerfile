FROM python:3.11.4

WORKDIR /app


RUN pip install jill --no-cache-dir

RUN jill install 1.10.0 --confirm

# Helpful Development Packages

# # Copy Julia environment files
# COPY Project.toml Manifest.toml /app/

# # Install required packages (if any)
# RUN julia --project=/app -e 'using Pkg; Pkg.instantiate();'

# # Precompile Julia packages
# RUN julia --project=/app -e 'using Pkg; Pkg.precompile();'

RUN julia -e 'using Pkg; Pkg.add(PackageSpec(;name = "PythonCall",version = "0.9.14"))'
RUN julia -e 'using Pkg; Pkg.add(PackageSpec(;url="https://github.com/BattMoTeam/BattMo.jl.git", rev="cccv"))'
RUN julia -e 'using Pkg; Pkg.add(PackageSpec(;name = "JSON",version = "0.21.4"))'

#RUN julia -e 'using Pkg; Pkg.add(PackageSpec(;name = "BattMo",version = "0.1.6"))'
#RUN julia -e 'using Pkg; Pkg.add("BattMo")'
RUN julia -e 'using Pkg; Pkg.add(PackageSpec(;name = "Jutul",version = "0.2.23"))'

#RUN julia -e 'using Pkg; Pkg.add(PackageSpec(;name = "Jutul",version = "0.2.14"))'
RUN julia -e 'using Pkg; Pkg.add(PackageSpec(;name = "LoggingExtras",version = "1.0.3"))'

# # Precompile Julia packages
# RUN julia -e 'using PythonCall'
# RUN julia -e 'using JSON'
# RUN julia -e 'using BattMo'
# RUN julia -e 'using Jutul'
# RUN julia -e 'using LoggingExtras'



#RUN julia -e 'using Pkg; Pkg.add(PackageSpec(;name = "PrettyTables",version = "2.2.7"))'

# Precompile Julia packages
# RUN julia -e 'using PkgCompiler; PkgCompiler.compile_package("PythonCall")'
# RUN julia -e 'using PkgCompiler; PkgCompiler.compile_package("JSON")'
# RUN julia -e 'using PkgCompiler; PkgCompiler.compile_package("BattMo")'
# RUN julia -e 'using PkgCompiler; PkgCompiler.compile_package("Jutul")'
# RUN julia -e 'using PkgCompiler; PkgCompiler.compile_package("LoggingExtras")'
# RUN julia -e 'using PkgCompiler; PkgCompiler.compile_package("PrettyTables")'


COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt
#RUN mkdir /app/results
COPY . .
