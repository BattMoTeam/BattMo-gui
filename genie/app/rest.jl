using Genie, Genie.Renderer.Json, Genie.Requests
using HTTP
using UUIDs
using JSON
using ZipFile
include("runP2DBattery.jl") 


# Set the host explicitly
Genie.config.run_as_server = true
Genie.config.server_host = "0.0.0.0"
Genie.config.cors_allowed_origins = ["*"]


route("/run_simulation", method = POST) do
    # Retrieve JSON data from the request sent by Client
    input_data = jsonpayload()

    # Generate a UUID
    uuid_str_in = string(UUIDs.uuid4())
    uuid_str_out = string(UUIDs.uuid4())

    # Create a file name with the UUID
    input_file_name = "$uuid_str_in.json"
    output_path_name = uuid_str_out


    # Write the JSON data to the file
    open(input_file_name, "w") do temp_input_file
        JSON.print(temp_input_file, input_data)
    end
    
     # Process the input data as needed
    # For example, you can access input_data["key"] to access specific values

    # Run BattMo simulation
    runP2DBattery.runP2DBatt(input_file_name, "results/$output_path_name")

    # Get a list of all files and directories in the specified folder
    output_files_list = readdir("results/$output_path_name")

    # Filter out directories from the list
    #files = filter(file -> isfile(joinpath(folder_path, file)), output_files_list)

    # Count the number of files
    num_files = length(output_files_list)

    # Compress the folder into a zip file
    zip_file_path = "zipped_results/$output_path_name.zip"

    w = ZipFile.Writer(zip_file_path)
    for file_name in output_files_list
        filepath = "results/$output_path_name/$file_name"
        f = open(filepath, "r")
        content = read(f, String)
        close(f)
        zf = ZipFile.addfile(w, basename(filepath));
        write(zf, content)
    end
    close(w)


    # Read the zip file contents into memory
    zip_data = read(zip_file_path, String)

    # Set up the HTTP response
    response = HTTP.Response(200, headers=Dict("Content-Type" => "application/zip"), body=zip_data)

    return response

end

up()