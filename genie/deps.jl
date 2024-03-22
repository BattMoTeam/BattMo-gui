using Pkg
Pkg.update()
Pkg.add("Genie")
Pkg.add("HTTP")
Pkg.add("LoggingExtras")
Pkg.add(PackageSpec(;name="BattMo", rev="dev"))
Pkg.add("JSON")
Pkg.add(PackageSpec(;name="Jutul", rev="battmo"))
Pkg.add("UUIDs")
Pkg.add("ZipFile")
Pkg.add("JLD2")
Pkg.add("PackageCompiler")

using Genie, HTTP, LoggingExtras, BattMo, JSON, Jutul, UUIDs, ZipFile, JLD2, PackageCompiler

Pkg.precompile()