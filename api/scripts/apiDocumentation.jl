#############################################################################
# Function used and serve the API documentation to port 8080
#############################################################################

export start_documentation_server

# Function to get the file extension
function extname(path::String)
    return splitext(path)[2]  # Returns the file extension including the dot
end

# Function to serve static files
function serve_file(req::HTTP.Request)

    # Get the path of the directory where the current script is located
    current_dir = @__DIR__

    # Set the static directory to the docs/html folder of the first app directory
    static_dir = abspath(joinpath(current_dir, "..", "docs", "build"))  # This should resolve to /api/docs/build

    println("Current Directory: $current_dir")
    println("Static Directory: $static_dir")
    println("Starting server...")
    
    # Log when the function is called
    println("Received request for: ", req.target)

    # Parse the URI from the request target
    uri = HTTP.URIs.URI(req.target)

    # Extract the requested file path from the URI
    file_path = uri.path

    # If no specific file is requested, serve index.html
    if file_path == "/"
        file_path = "/index.html"  # Serve index.html if no specific file is requested
    end

    # Strip any leading slash from file_path to ensure proper join with static_dir
    file_path = lstrip(file_path, '/')

    # Construct the full path to the file
    full_path = joinpath(static_dir, file_path)

    # Log the constructed path
    println("Full path: $full_path")

    # Check if the file exists
    if isfile(full_path)
        println("File found: $full_path")
        # # Get the MIME type using MIMEs package
        # mime = mime_from_extension(extname(full_path))

        # # Log the MIME type
        # println("MIME type: ", mime)

        # Read the file content
        content = read(full_path)

        # Log content length
        println("Content length: ", length(content))

        # Create the response headers without charset
        headers = Dict("Content-Type" => "text/html")  # Remove charset from Content-Type

        # Construct the headers as a Vector of Pairs
        headers_vector = collect(pairs(headers))

        # Log the headers being sent
        println("Headers: ", headers_vector)

        # Return the HTTP response
        return HTTP.Response(200, content)
    else
        println("File not found: $full_path")
        return HTTP.Response(404, "File not found")
    end
end

function start_documentation_server(doc_port::Int)

    # Start the HTTP server
    HTTP.serve(serve_file, "0.0.0.0", doc_port)

end



