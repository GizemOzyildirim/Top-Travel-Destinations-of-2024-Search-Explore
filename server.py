# Name: Gizem Ozyildirim
# 41B Advanced Python
# Spring 2014
# Module 5
# Lab 5
# server.py

import os
import sys
import glob
import json
import time
import socket
import threading

PORT = 5551
HOST = "localhost"
DATA_LIMIT = 4*1024

# On command line find processes using port 5551
# lsof -i :5551 --> returns the {process_id} using the port 5551
# kill -9 {process_id} --> to kill the process with {process_id}

class Opereations:
    '''Handles client command operations.'''
        
    def __init__(self, socket, client_index, start_directory):
        '''Initializes the Operations class with socket, client index, and start directory.

        Args:
            socket (socket): The socket object for client-server communication.
            client_index (int): The index number of the client.
            start_directory (str): The starting directory path for the operations.
        '''
        
        self.client_index = client_index
        self.current_directory = start_directory
        self.s = socket
        
        self.cmd_lookup_table = {
            "cd": lambda args: self.change_directory(args), # Change Directory
            "ls": self.list_current_directory, # LiSt
            "lsr": self.list_directories_recursively, # LiSt DirectoryRecursively
            # "q": self.quit # Quit
        }
        
    
    def change_directory(self, args):
        '''Changes the current directory to a new path.

        Args:
            args (list): The arguments containing the new path.

        Returns:
            dict: A dictionary containing the status, current directory, and error message (if any).
        '''
        
        path = None
        success = False
        error_msg = None
        try:
            path = args[0]
            new_path = os.path.join(self.current_directory, path)
            new_path = os.path.realpath(new_path)
            if os.path.isdir(new_path):
                self.current_directory = new_path
                success = True
            else:
                error_msg = f'Targeted new path {new_path} is not a directory.'
        except Exception as e:
            error_msg = f"Directory cannot be changed for current directory {self.current_directory} to the new path {path}"
            print(error_msg)
        
        return {'status':success, 'pwd':self.current_directory, 'error': error_msg}
    
    def list_current_directory(self):
        '''Lists the contents of the current directory.

        Returns:
            dict: A dictionary containing the status, current directory, directory items, and error message (if any).
        '''
        
        error_msg = None
        success = False
        directory_items = []
        try:
            directory_items = os.listdir(self.current_directory)
            success = True
        except Exception as e:
            error_msg = f"Directory content cannot be listed for current directory {self.current_directory}"
            print(error_msg)
            
        return {'status': success, 'pwd':self.current_directory, 'dir_items': directory_items, 'error': error_msg}
    
    def list_directories_recursively(self):
        '''Lists all directories recursively from the current directory.

        Returns:
            dict: A dictionary containing the status, current directory, recursive directory items, and error message (if any).
        '''
        
        error_msg = None
        success = False
        recursive_directory_items = []
        # For glob work recursively add asterix; it means scan all subfolders
        glob_path = os.path.join(self.current_directory, '**/')
        try:
            for dir_name in glob.glob(glob_path, recursive=True):
                recursive_directory_items.append(dir_name)
            success = True
        except Exception as e:
            error_msg = f"Subdirectories could not be listed for the directory {self.current_directory}"
            print(error_msg)
        
        return {'status': success, 'pwd':self.current_directory, 'dir_items': recursive_directory_items, 'error': error_msg}

    # def quit(self):
    #     ''' Terminates the current thread '''
        
    #     sys.exit(0)
        
        
    def handle(self):
        '''Handles the client connection, processes commands, and sends responses.'''
      
        try:
            (conn, addr) = self.s.accept()
            conn.settimeout(None)
                    
            while True:
                fromClient = conn.recv(DATA_LIMIT).decode('utf-8')
                
                # Parse the command and its arguments
                cmd_args = [cmd for cmd in fromClient.split(" ") if cmd]
                cmd = cmd_args[0]
                args = cmd_args[1:]
                if fromClient == 'q':
                    return
                func = self.cmd_lookup_table.get(cmd)
                
                if func is not None:
                    if len(args) > 0:
                        result = func(args)
                    else:
                        result = func()
                        
                
                result_json = json.dumps(result)
                conn.send(result_json.encode('utf-8'))
        except TimeoutError as e:
            print(f"{socket_timeout_secs} sec is up, closing 1 unused connections")
                
    

if __name__=='__main__':
    '''Main function to initialize server settings and handle multiple client connections.'''
    
    # Ensure that the script is run with exactly two command-line arguments
    if len(sys.argv) != 3:
        print("Two parameters required. First is for the supported client count; second for the socket timeout")
        sys.exit(1)
    
    number_of_clients = None
    socket_timeout_secs = None
    
    # Validate and parse the command-line arguments
    try:
        number_of_clients = int(sys.argv[1])
        socket_timeout_secs = int(sys.argv[2])
    except TypeError as e:
        print("Both of the parameters should be numbers")
        sys.exit(1)
    
    # Check if the number of clients is within the allowed range    
    if number_of_clients >= 5:
        print("Allowed max number of clients is 5")
        sys.exit(1)
    
    # Check if the socket timeout is within the allowed range    
    if not (3 < socket_timeout_secs < 120):
        print("Allowed socket timeout is between 3 and 120secs")
        sys.exit(1)
    
    # Set the starting directory for the server operations      
    start_directory = os.getcwd()
    # start_directory = os.path.join(start_directory, 'test')
    
    # Set the default timeout for the socket
    socket.setdefaulttimeout(socket_timeout_secs)
    
    # Create and configure the server socket
    with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as s:
        s.bind((HOST, PORT))
        print("Server is up, hostname:", HOST, "port:", PORT)
        print(f'Starting directory {start_directory}')
        
        # Start listening for incoming client connections
        s.listen(number_of_clients)
        
        threads = []
        # Create and start a thread for each client
        for client_index in range(1, number_of_clients+1):
            operationer = Opereations(s, client_index, start_directory)
            t = threading.Thread(target=operationer.handle)
            t.start()
            threads.append((client_index, t))
        
        # Monitor the threads and remove the dead ones from the list  
        while len(threads) > 0:
            time.sleep(1)
            # the dead threads needs to be removed from the thread list
            temp_threads = threads.copy()
            for client_index, thread in temp_threads:
                if not thread.is_alive():
                    print(f"Connection to client {client_index} closed")
                    threads.remove((client_index, thread))

"""      
    Note to myself:
    
               
    sys.exit(0):    Exits the program with a status code of 0. 
    This status code indicates that the program has terminated successfully. 
    
    sys.exit(1):    Exits the program if the check fails.
    
    sys.argv:   It is a list in Python that contains the command-line arguments
    passed to the script. argv stands for "argument vector".

"""  