# home file server
Simple file server for personal use

Operation:

        [d] download from server
        [u] upload to server
        [m] make director
        [v] view directory
        [-h] help screen (UPCOMING)
        [update] update server (UPCOMING)
        [clear] clear the terminal window 


As of now, it has the following functionality:

    1. Upload files to the server
    2. Download files from the server
    3. Create directories within the server
    4. View contents of directories within the server


Upcoming Functionality:

    1. Send updates to the server remotely
    2. Delete files from the server
    3. Delete directories without deleting contents (should be default)
    4. Delete directoreis and their contents (very dangerous)
    5. automatically delete files from client computer once they have been moved (dangerous)
    6. help screen displayed when -h is called
    7. upload entire directories onto the server


Known bugs and issues:

    1. all code is slightly inefficient or could be written in a more concise way
    2. putting an invalid directory in when uploading a file results in infinite loop
    3. client code does not check if the server is actually alive, implement ping echoing for server
    4. server overwrites duplicate files, instead of adding a number to the end
    5. exceptions are handled too generally, allowing infinite loops of errors
    6. implement escapes if the server response is not 200
    7. when downloading files, the server doesnt check if the given path is an actual file, or if its just a directory


Script Descriptions:

    a) client.py: Download to the client computer, handles communication to the file server
    b) server.py: Download to the server computer, handles communication with the client
    c) librarian.py: Download to server computer, is responsible for organizing the file system