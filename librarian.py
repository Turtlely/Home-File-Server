import os
import chardet
from pathlib import Path

'''
This program is responsible for managing the files stored in the file server, aptly named Librarian

Path format: (MUST HAVE /{root_folder}/ IN ORDER TO BE PROCESSED)
# /root/test1/test2/test.py
'''

#Encoding prediction function
def predict_encoding(file_path: Path, n_lines: int=20) -> str:
    '''Predict a file's encoding using chardet'''

    # Open the file as binary data
    with Path(file_path).open('rb') as f:
        # Join binary lines for specified number of lines
        rawdata = b''.join([f.readline() for _ in range(n_lines)])

    return chardet.detect(rawdata)['encoding']

#Name of the root folder, the program will only access and modify files within this folder
#Multiple roots may be possible to create isolated filesystems
root_folder = 'root'

#Make root folder if it doesnt already exist
if not os.path.exists(root_folder):
    os.makedirs(root_folder)

#Create directories
def makeDir(path):
    #Basic security 
    if path[0:2+len(root_folder)] != f'/{root_folder}/':
        print(path)
        return f'root folder named "{path[0:2+len(root_folder)]}" does not exist, make sure the path begins with "/{root_folder}/"'
    
    path = root_folder + path[1+len(root_folder):]

    if os.path.isfile(path):
        return 'This is not a directory'

    if not os.path.exists(f'{os.getcwd()}/{path}'):
        os.makedirs(f'{os.getcwd()}/{path}')
        return 'Success!'

    else:
        return 'Directory already exists!'


#View directories
def viewDir(path):
    #Basic security 
    if path[0:2+len(root_folder)] != f'/{root_folder}/':
        return 'Path not in file structure'
    
    path = root_folder + path[1+len(root_folder):]

    if os.path.isfile(path):
        return 'This is not a directory'
    

    if os.path.exists(path):
        return os.listdir(path)

    else:
        return 'Directory doesnt exist!'


#Pick up file for client from a directory
def getFile(path):
    #Basic security 
    if path[0:2+len(root_folder)] != f'/{root_folder}/':
        return 'Path not in file structure'
    path = root_folder + path[1+len(root_folder):]

    if os.path.isfile(path):
        n=20 #starting number of lines

        while True: #Encoding may not always be right the first time due to sampling lines
            codec = predict_encoding(path,n_lines=n) 

            if n > 100: #threshold before breaking out, since reading too many lines may take too long
                return 'ERROR NO ENCODING WAS FOUND', 'utf-8'

            if codec == None: #binary file
                try:
                    with open(path,'rb') as f:
                        file = f.read()
                    f.close()
                    return file, codec

                except UnicodeDecodeError:
                    n+=1 #increment number of lines to sample by 1

            else: #not a binary file (usually just a txt file)
                try:
                    with open(path,'r',encoding=codec) as f:
                        file = f.read()
                    f.close()
                    return file, codec

                except UnicodeDecodeError:
                    n+=1 #increment number of lines to sample by 1

    else:
        return 'This file doesnt exist here!'
    
#Store file for client to a directory
def storeFile(path,filename,codec,post_data):
    #in case a file already exists with the same name, add a number to the end
    count = 0
    path = root_folder + path[1+len(root_folder):]
    print(path)
    if codec == None:
            while True:
                try:
                    with open(f'{path}/{filename}', 'wb') as f:
                        f.write(post_data)
                        f.close()
                        print('------------------^^DONE^^----------------')
                        return 'Successfully uploaded'
                except Exception as e:
                    count+=1
                    print(e)
                    filename + str(count)
    else:
        while True:
            try:
                with open(f'{path}/{filename}', 'w') as f:
                    f.write(post_data.decode(codec))
                    f.close()
                    print('------------------^^DONE^^----------------')
                    return 'Successfully uploaded'
            except Exception as e:
                count+=1
                print(e)
                filename + str(count)
