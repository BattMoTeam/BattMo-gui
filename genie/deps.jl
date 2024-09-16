using Pkg
Pkg.update()
Pkg.add("Genie")
Pkg.add("HTTP")
Pkg.add("LoggingExtras")
Pkg.add(PackageSpec(;name="BattMo", rev="dev"))
Pkg.add(PackageSpec(;name="Jutul", rev="f5ad71487efe734f35db34389a509b562a163e0f"))
Pkg.add("JSON")
Pkg.add("UUIDs")
Pkg.add("HDF5")
Pkg.add("PackageCompiler")
Pkg.add("SwaggerMarkdown")
Pkg.add("SwagUI")










using Genie, HTTP, LoggingExtras, BattMo, JSON, Jutul, UUIDs, ZipFile, JLD2, PackageCompiler, SwagUI, SwaggerMarkdown

Pkg.precompile()