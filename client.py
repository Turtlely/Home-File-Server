from ast import arg
from turtle import down
import requests
import os
import sys
import argparse
import json
from pathlib import Path
import chardet

#TODO implement way to delete directories, move files within file server, and automatically update server

HOSTNAME = '127.0.0.1'
PORT = 8000

base_url = f'http://{HOSTNAME}:{PORT}'

downloads = 'downloads'

#Make root folder if it doesnt already exist
if not os.path.exists(downloads):
    os.makedirs(downloads)

'''
Arguments:
    Path:
        The path that is taken for any of the operations

    Operation:
        [d] download from server
        [u] upload to server
        [m] make director
        [v] view directory
        [update] update server 
'''

parser = argparse.ArgumentParser(description='Access the local file server')
parser.add_argument('fileServerPath', metavar = 'path', type = str, help = 'The destination path within the file server')
parser.add_argument('filePath', metavar = 'file path', type = str, help = 'The path of the client file')
parser.add_argument('Operation', metavar = 'operation', type = str, help = '[d] Download, [u] Upload, [m] Make Directory, [v] View Directory, [update] update')
args = parser.parse_args()

path = args.fileServerPath
op = args.Operation
filePath = args.filePath

#Encoding prediction function
def predict_encoding(file_path: Path, n_lines: int=20) -> str:
    '''Predict a file's encoding using chardet'''

    # Open the file as binary data
    with Path(file_path).open('rb') as f:
        # Join binary lines for specified number of lines
        rawdata = b''.join([f.readline() for _ in range(n_lines)])

    return chardet.detect(rawdata)['encoding']

def client():
    #make sure a file path was provided if operation reqiores it
    if op == 'u' and not os.path.isfile(filePath):
        print("Invalid or unprovided client file path")
        sys.exit()

    if op == 'v':
        response = viewDir()
        if response[0] == '[': #Makes sure that we got a successful response, in the form of a list by checking the last character
            #Formatting response
            entries = response[1:-1].split(',') #removes brackets
            n=1
            while True:
                if path.split("/")[-1*n] == "":
                    n+=1
                else:
                    break

            print("----------------------------------------------")
            print(f'Contents of "{path.split("/")[-1*n]}" directory')
            print("----------------------------------------------")
            
            #print out the entries inside of the directory
            if entries[0] == '':
                print("EMPTY DIRECTORY")
            else:
                for e in entries:
                    print(f'[{str(entries.index(e))}] {e.strip()[1:-1]}')
        else:
            print("----------------------------------------------")
            print(f'ERROR: {response}')
            print("----------------------------------------------")
   
    if op == 'm':
        print(makeDir())

    if op == 'd':
        print(fetch())

    if op == 'u':
        print(upload())
    if op == 'update':
        pass

    return

def upload():
    #assemble POST url
    url = f'{base_url}/UFIL/{path}'

    n=20
    while True: #open file with correct encoding
        codec = predict_encoding(filePath,n_lines = n)
        if n > 100:
            return 'ERROR: NO ENCODING WAS FOUND'
        if codec == None: #binary file
            try:
                with open(filePath,'rb') as f:
                    headers = {'Content-Length': str(f.tell()),
                                'Codec':"None",
                                'Filename':os.path.basename(filePath),
                                }
                    file = {'upload': f.read()}
                    r = requests.post(url,files=file,headers=headers)
                    f.close()
                    return r.text
            except Exception as e:
                print(e)
                print(f'WARNING: {codec} did not work, trying again')
                n+=1
        else:
            try:
                with open(filePath,'r',encoding=codec) as f:
                    headers = {'Content-Length': str(f.tell()),
                                'Codec':codec,
                                'Filename':os.path.basename(filePath),
                                }
                    
                    file = {'upload': f.read()}
                    r = requests.post(url,files=file,headers=headers)
                    f.close()
                    return r.text
            except Exception as e:
                print(e)
                print(f'WARNING: {codec} did not work, trying again')
                n+=1

def fetch():
    r = requests.get(f'{base_url}/RFIL/{path}')

    if r.status_code != 200:
        return 'Server Connection Error'

    filename = path.split("/")
    n = -1
    while True:
        if filename[n] == ' ':
            n-=1
        else:
            break

    filename = filename[n]

    n=20 #starting number of lines

    while True: #Encoding may not always be right the first time due to sampling lines
        codec = predict_encoding(path,n_lines=n) 
        if n > 100: #threshold before breaking out, since reading too many lines may take too long
            return 'ERROR NO ENCODING WAS FOUND', 'utf-8'

        if codec == None: #binary file
            try:
                with open(f'{downloads}/{filename}','wb') as f:
                    f.write(r.content)
                    f.close()
                return f'Successfully downloaded "{filename}" to {downloads}'
            except Exception:
                print(f'WARNING: {codec} did not work, trying again')
                n+=1 #increment number of lines to sample by 1

        else: #not a binary file (usually just a txt file)
            try:
                with open(f'{downloads}/{filename}','w',encoding=codec) as f:
                    f.write(r.content)
                    f.close()
                return f'Successfully downloaded "{filename}" to {downloads}'
            except Exception:
                print(f'WARNING: {codec} did not work, trying again')
                n+=1 #increment number of lines to sample by 1

def viewDir():
    r = requests.get(f'{base_url}/VDIR/{path}')
    return r.text

def makeDir():
    #print(f'{base_url}/CDIR/{path}')
    r = requests.get(f'{base_url}/CDIR/{path}')
    return r.text

if __name__ == '__main__':
    client()
