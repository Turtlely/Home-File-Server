from fileinput import filename
from http.server import HTTPServer, SimpleHTTPRequestHandler,BaseHTTPRequestHandler
from librarian import *
import sys
import cgi

PORT = 8000
Handler = BaseHTTPRequestHandler

class Server(Handler):
    #This is the server that handles the connection

    '''
    This server can do this:
    1. upload files from the client to a server directory
    2. send files from a server directory to the client
    3. create directories / CREATEDIRECTORY / [PATH FROM ROOT] / [NAME OF DIRECTORY]
    4. view directories  / VIEWDIRECTORY / [PATH] / [NAME OF DIRECTORY]
    5. check if a directory exists
    5. self update when given update files from the client
    '''

    #GET request handler
    def do_GET(self):

        #Create a directory
        if self.path[0:6] == '/CDIR/':
            self.send_response(200,'OK')
            self.end_headers()            
            directory_path = self.path[5:]
            print(self.path)

            print('Writing Directory')
            r = makeDir(directory_path)
            self.wfile.write(bytes(r,'utf-8'))

            print('----------------^^DONE^^------------------')

        #View a directory
        elif self.path[0:6] == '/VDIR/':
            self.send_response(200,'OK')
            self.end_headers()

            print('Viewing directory')

            directory_path = self.path[5:]
            self.wfile.write(bytes(str(viewDir(directory_path)),'utf-8'))

            print('------------------^^DONE^^----------------')
        
        #Retrieve a file
        elif self.path[0:6] == '/RFIL/':
            self.send_response(200,'OK')
            self.end_headers()

            print("Retrieving files")
            directory_path = self.path[5:]
            f = getFile(directory_path)
            
            if f[1] == 'ERROR':
                print(f'ERROR: {f[0]}')
                self.wfile.write(bytes(f[0],'utf-8'))

            elif f[1] == None:
                self.wfile.write(f[0])
            
            else:
                self.wfile.write(bytes(f[0],f[1]))


            print('------------------^^DONE^^----------------')


        else:
            self.send_response(200,'OK')
            self.end_headers()
            self.wfile.write(bytes('Invalid Request, check your formatting','utf-8'))
            
    #POST request handler
    def do_POST(self):
        if self.path[0:6] == '/UFIL/':
            self.send_response(200,'OK')
            self.end_headers()

            print("Uploading files")

            directory_path = self.path[5:]

            content_length = int(self.headers['content-length']) # <--- Gets the size of data
            codec = self.headers['Codec']
            filename = self.headers['Filename']


            ctype, pdict = cgi.parse_header(self.headers['Content-Type'])
            pdict['boundary'] = bytes(pdict['boundary'], 'utf-8')
            fields = cgi.parse_multipart(self.rfile, pdict)
            data = fields['upload']

            if codec != "None":
                #print(self.rfile.read(content_length).decode(codec))
                #print(data[0])
                storeFile(directory_path,filename,codec,data[0])
            else:
                #print(self.rfile.read(content_length))
                #print(data[0].decode(codec))
                storeFile(directory_path,filename,None,data[0])
            
            self.wfile.write(bytes(f'Successfully uploaded {filename}',encoding='utf-8'))


        else:
            self.send_response(200,'OK')
            self.end_headers()
            self.wfile.write(bytes('Invalid Request, check your formatting',encoding='utf-8'))            
        return

if __name__ == '__main__':
    server = HTTPServer(('',PORT),Server)

    print('------------------------------------------')
    print(f'Server started at http://localhost:{PORT}')
    print('------------------------------------------')
    
    try:
        server.serve_forever()
    except KeyboardInterrupt:
        server.server_close()
        print('Server closed')
        sys.exit(0)
