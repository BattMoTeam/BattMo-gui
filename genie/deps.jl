using Pkg
Pkg.update()
Pkg.add("Genie")
Pkg.add("HTTP")
Pkg.add("LoggingExtras")
Pkg.add(PackageSpec(;name="BattMo", rev="dev"))
Pkg.add(PackageSpec(;name="Jutul", rev="battmo"))
Pkg.add("JSON")
Pkg.add("UUIDs")
Pkg.add("PackageCompiler")
Pkg.add("HDF5")








using Genie, HTTP, LoggingExtras, BattMo, JSON, Jutul, UUIDs, ZipFile, JLD2, PackageCompiler

Pkg.precompile()