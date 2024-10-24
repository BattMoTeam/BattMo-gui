using Pkg
Pkg.update()
Pkg.add("HTTP")
Pkg.add(PackageSpec(;name="BattMo", rev="dev"))
Pkg.add("Jutul")
Pkg.add("JSON")
Pkg.add("HDF5")
Pkg.add("UUIDs")
Pkg.add("PackageCompiler")

using HTTP, BattMo, JSON, Jutul, UUIDs, HDF5, PackageCompiler
Pkg.precompile()