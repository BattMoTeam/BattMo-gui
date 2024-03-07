using Pkg
Pkg.update()
Pkg.add("Genie")
Pkg.add("HTTP")
Pkg.add("LoggingExtras")
Pkg.add(PackageSpec(;url="https://github.com/BattMoTeam/BattMo.jl.git", rev="cccv"))
Pkg.add("JSON")
Pkg.add("UUIDs")
Pkg.add("ZipFile")
Pkg.add("JLD2")
Pkg.add("PackageCompiler")

Pkg.precompile()