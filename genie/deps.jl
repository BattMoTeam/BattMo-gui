using Pkg
Pkg.update()
Pkg.add("Genie")
Pkg.add("HTTP")
Pkg.add("LoggingExtras")
Pkg.add(PackageSpec(;name="BattMo", rev="dev"))
Pkg.add("Jutul")
Pkg.add("JSON")
Pkg.add("UUIDs")
Pkg.add("HDF5")
Pkg.add("PackageCompiler")
Pkg.add("SwaggerMarkdown")
Pkg.add("SwagUI")











using Genie, HTTP, LoggingExtras, BattMo, JSON, Jutul, UUIDs, ZipFile, JLD2, PackageCompiler, SwagUI, SwaggerMarkdown

Pkg.precompile()