# home file server
Simple file server for personal use

USAGE:

    Arguments:
    
    Path:
        The path that is taken for any of the operations
    
    File path:
        The path of the client file (Only used when uploading files)

    Operation:
        [d] download from server
        [u] upload to server
        [m] make director
        [v] view directory
        [update] update server 


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


KNOWN BUGS AND ISSUES:

    1. file path should only be a required argument for uploading
    2. all code is slightly inefficient or could be written in a more concise way

SCRIPT DESCRIPTIONS:

    a) client.py: Download to the client computer, handles communication to the file server
    b) server.py: Download to the server computer, handles communication with the client
    c) librarian.py: Download to server computer, is responsible for organizing the file system