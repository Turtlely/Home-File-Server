from ast import arg
from turtle import down
import requests
import os
import sys
import argparse
from pathlib import Path
import chardet
from colorama import Fore, Back, Style
import shutil

#TODO implement way to delete directories, move files within file server, and automatically update server
#TODO make a better UI system

#TODO move this stuff into a config file
HOSTNAME = "localhost" #this has to be changed for whatever your server's hostname is
PORT = 8000

base_url = f'http://{HOSTNAME}:{PORT}'

downloads = "downloads" #in the future, allow to specify a downloads folder

#Server connection check
try:
    r = requests.get(f'{base_url}/ping')
    if r.text == 'SERVER RUNNING OK':
        print(r.text)
    else:
        print(f'{Fore.RED}ERROR: {Fore.WHITE}Server not connected')
        sys.exit()
except Exception as e:
    print(f'{Fore.RED}ERROR: {Fore.WHITE}{e}')
    sys.exit()

#Make root folder if it doesnt already exist
#TODO notify user that a new folders was made
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

#Encoding prediction function
def predict_encoding(path, n_lines: int=20) -> str:
    '''Predict a file's encoding using chardet'''
    # Open the file as binary data
    with open(path,'rb') as f:
        # Join binary lines for specified number of lines
        rawdata = b''.join([f.readline() for _ in range(n_lines)])

    return chardet.detect(rawdata)['encoding']

#Encoding prediction function FOR RAW DATA
def predict_encoding_RAW(rawdata, n_lines: int=20) -> str:
    '''Predict raw data's encoding using chardet'''
    return chardet.detect(rawdata)['encoding']

def client():
    #UI
    os.system('cls||clear')
    columns = shutil.get_terminal_size().columns
    print(f'='*columns)
    print(f'{Fore.CYAN}FILE SERVER CLI'.center(columns))
    print(f'{Fore.RED}{quit}{Style.RESET_ALL}'.center(columns))
    print(f'='*columns)
    
    #TODO maybe show the file system structure upon opening
    while True:
        op = input(f'{Fore.GREEN}Enter Operation: [d] [udir] [u] [m] [v] [-h] [update] [clear]\n{Fore.YELLOW}')
        
        #Upload file command
        if op == 'u':
            path = input(f"{Fore.GREEN}Enter destination path: {Fore.YELLOW}")
            while True:
                filePath = input(f'{Fore.GREEN}Enter Source path: {Fore.YELLOW}')
                if not os.path.isfile(filePath):
                    print(f"{Fore.RED}ERROR:{Style.RESET_ALL} Invalid path, try again")
                else:
                    #Upload file
                    print(f'{Fore.CYAN}{upload(filePath,path)}{Fore.WHITE}')
                    break

        #View a directory
        elif op == 'v':
            path = input(f"{Fore.GREEN}Enter server path: {Fore.YELLOW}")
            #send request to file server
            r = requests.get(f'{base_url}/VDIR/{path}')

            #do this at the beginning of every command
            if r.status_code != 200:
                print(f'{Fore.RED}ERROR: {Fore.WHITE}Server connection error')
                sys.exit()
            r=r.text
            #Make sure that we got a successful response, in the form of a list by checking the last character
            if r[0] == '[': 
                #Formatting response
                entries = r[1:-1].split(',') #removes brackets
                n=1
                while True:
                    if path.split("/")[-1*n] == "":
                        n+=1
                    else:
                        break

                print(f"{Style.RESET_ALL}="*46)
                print(f'{Fore.CYAN}Contents of "{path.split("/")[-1*n]}" directory'.center(52))
                print(f"{Fore.WHITE}="*46)
                
                #print out the entries inside of the directory
                if entries[0] == '':
                    print("EMPTY DIRECTORY")
                else:
                    for e in entries:
                        print(f'{Fore.RED}[{str(entries.index(e)+1)}] - {Fore.WHITE}{e.strip()[1:-1]}')
            else:
                print(f'{Fore.WHITE}='*46)
                print(f'{Fore.RED}ERROR:{Fore.WHITE} {r}'.center(56))
                print(f'{Fore.WHITE}='*46)
    
        #Make a directory
        elif op == 'm':
            path = input(f"{Fore.GREEN}Enter server path: {Fore.YELLOW}")
            
            r=requests.get(f'{base_url}/CDIR/{path}')

            #do this at the beginning of every command
            if r.status_code != 200:
                print(f'{Fore.RED}ERROR: {Fore.WHITE}Server connection error')
                sys.exit()

            print(r.text) #see if we can eliminate these print statements

        #Download a file from the server
        elif op == 'd':
            #print("this is broken as of now")
            path = input(f"{Fore.GREEN}Enter server path: {Fore.YELLOW}")
            fetch(path)

        #Update the server
        elif op == 'update':
            print(f'{Fore.RED}Sorry! update functionality has not yet been implemented{Fore.WHITE}')
        
        #Clear terminal
        elif op == 'clear':
            os.system('cls||clear')
            columns = shutil.get_terminal_size().columns
            print(f'{Fore.WHITE}='*columns)
            print(f'{Fore.CYAN}FILE SERVER CLI'.center(columns))
            print(f'{Fore.RED}{quit}{Style.RESET_ALL}'.center(columns))
            print(f'='*columns)
        
        #Display help
        elif op == '-h':
            print("Help manual coming soon")

        #Upload an entire directory to the server
        elif op == 'udir':
            #Get destination path
            path = input(f"{Fore.GREEN}Enter destination path: {Fore.YELLOW}")
            while True:
                #Get source path
                dirPath = input(f'{Fore.GREEN}Enter Source path: {Fore.YELLOW}')
                
                #Ensure that this is a directory, not a file TODO in the future automatically decide to upload directories or files
                if not os.path.isdir(dirPath):
                    print(f"{Fore.RED}ERROR:{Fore.WHITE} Invalid Path. Select a directory")
                else:
                    #generate list of files
                    files = [f for f in os.listdir(dirPath) if os.path.isfile(os.path.join(dirPath,f))]
                    
                    #Confirm with the user that they are going to upload the directory
                    print(f'{Fore.RED}WARNING: {Fore.WHITE}You are about to upload {Fore.RED}{len(files)}{Fore.WHITE} file(s) to "{Fore.RED}{os.path.normpath(path)}{Fore.WHITE}"')
                    print(files)
                    flag = input(f'{Fore.GREEN}Continue? {Fore.WHITE}(y/n){Fore.YELLOW}')
                    if flag == 'n':
                        print(f'{Fore.CYAN}Exiting...')
                        break
                    elif flag == 'y':
                        pass
                    else:
                        print(f"{Fore.RED}ERROR: {Fore.WHITE}Invalid Input")
                        print(f'{Fore.CYAN}Exiting...{Fore.YELLOW}')
                    #Upload files
                    for f in files:
                        try:
                            print(f'Uploading file {f}/{len(files)} [{f}]...')
                            print(f'{Fore.CYAN}{upload(os.path.join(dirPath,f),path)}{Fore.WHITE}')
                            print()
                        except Exception as e:
                            print(f"{Fore.RED}ERROR: {Fore.WHITE}{e}")
                    
                    print(f'Completed uploading {len(files)} files!')
                    break
            pass

        else:
            print(f'{Fore.RED}ERROR: {Fore.WHITE}Invalid input!')

def upload(filePath,path):
    #assemble POST url
    url = f'{base_url}/UFIL/{path}'

    n=20
    while True: #open file with correct encoding
        codec = predict_encoding(filePath,n_lines = n)
        
        if n > 100:
            return f'{Fore.RED}ERROR: {Fore.WHITE}NO ENCODING WAS FOUND'
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
            except Exception:
                print(f'{Fore.RED}WARNING:{Fore.WHITE} {codec} did not work, trying again')
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
            except Exception:
                print(f'{Fore.RED}WARNING:{Fore.WHITE} {codec} did not work, trying again')
                n+=1

#TODO Fetch is broken with the new UI update
def fetch(path):
    r = requests.get(f'{base_url}/RFIL/{path}')

    #do this at the beginning of every command
    if r.status_code != 200:
        print(f'{Fore.RED}ERROR: {Fore.WHITE}Server connection error')
        sys.exit()
    try:
        if(r.content.decode('utf-8')[0:5] == "ERROR"):
            print(f'{Fore.RED}{r.content.decode("utf-8")[0:6]} {Fore.WHITE}{r.content.decode("utf-8")[6:]}')
            return
    except UnicodeDecodeError:
        pass

    #path handling can be made safer with OS, the while loop is dangerous
    filename = path.split("/") #get the filename from the path
    n = -1
    while True:
        if filename[n] == ' ':
            n-=1
        else:
            break

    filename = filename[n]

    n=20 #starting number of lines

    while True: #Encoding may not always be right the first time due to sampling lines
        codec = predict_encoding_RAW(r.content,n_lines=n) 
        if n > 100: #threshold before breaking out, since reading too many lines may take too long
            print(f'{Fore.RED}ERROR: {Fore.WHITE}NO ENCODING WAS FOUND')
            return

        if codec == None: #binary file
            try:
                with open(f'{downloads}/{filename}','wb') as f:
                    f.write(r.content) #Errors could happen here
                    f.close()
                    print(f'{Fore.CYAN}Successfully downloaded "{Fore.WHITE}{filename}{Fore.CYAN}" to {downloads}')
                return 

            except Exception: #TODO this exception is too general
                print(f'{Fore.RED}WARNING: {Fore.WHITE}{codec} did not work, trying again')
                n+=1 #increment number of lines to sample by 1

        else: #not a binary file (usually just a txt file)
            try:
                with open(f'{downloads}/{filename}','w',encoding=codec) as f:
                    f.write(r.content) #Errors could happen here
                    f.close()
                    print(f'{Fore.CYAN}Successfully downloaded "{Fore.WHITE}{filename}{Fore.CYAN}" to {downloads}')
                return

            except Exception: #TODO this exception is too general
                print(f'{Fore.RED}WARNING: {Fore.WHITE}{codec} did not work, trying again')
                n+=1 #increment number of lines to sample by 1

if __name__ == '__main__':
    client()
