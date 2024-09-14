# Name: Gizem Ozyildirim
# 41B Advanced Python
# Spring 2014
# Module 5
# Lab 5
# client.py

import time
import json
import socket

PORT = 5551
HOST = '127.0.0.1'
DATA_LIMIT = 4*1024

COMMANDS = [
    'cd',
    'ls',
    'lsr',
    'q'
]

def print_commands():
    '''Prints the list of available commands.'''
    
    print("Commands:")
    print('ls\t\tlist current directory')
    print('lsr\t\tlist subdirectories recursively')
    print('cd dir_name\tgo to dir_name')
    print('q\t\tquit')
    
    
def validate_command(cmd, args):
    '''Validates the entered command and its arguments.

    Args:
        cmd (str): The command to be validated.
        args (list): The list of arguments for the command.

    Returns:
        bool: True if the command is valid, False otherwise.
        str: An error message if the command is invalid.
    '''
    
    valid = True
    error_message = ""
    if cmd not in COMMANDS:
        valid = False
        error_message = f"Invalid command {cmd}!"
    elif cmd == "cd" and len(args) != 1: # If cmd is cd and the args is empty; enter this block
        valid = False
        error_message = f"The command cd takes ecaxctly one word after it!"
    elif cmd in ['ls', 'lsr', 'q'] and len(args) != 0:
        valid = False
        error_message = f"The commands ls, lsr and q do not take any arguments!"
        
    if valid == False:
        print(f"{error_message} Please pick one of the valid commands from the list below:")
        print_commands()
        
    return valid


def print_ls_response(response):
    '''Prints the response of the ls command.

    Args:
        response (dict): The response dictionary from the server.
    '''
    
    if response.get("status"):
        print(f"Listing of {response.get('pwd')}")
        for dir_item in response.get('dir_items'):
            print(dir_item)
    else:
        print(response.get("error"))


def print_lsr_response(response):
    '''Prints the response of the lsr command.

    Args:
        response (dict): The response dictionary from the server.
    '''
    
    if response.get("status"):
        print(f"Recursive listing of {response.get('pwd')}")
        for dir_item in response.get('dir_items'):
            print(dir_item)
    else:
        print(response.get("error"))


def print_cd_response(response):
    '''Prints the response of the cd command.

    Args:
        response (dict): The response dictionary from the server.
    '''
    
    if response.get("status"):
        print(f"New path: {response.get('pwd')}")
    else:
        print(response.get("error"))


''' In this part : Initiates client connection to do server '''
# Create the client socket
with socket.socket() as s :
    # Connect to the server
    s.connect((HOST, PORT))
    print("Client connect to:", HOST, "port:", PORT)
    print_commands() # Print available commands for the user
    
    mesg = None # Initialize the message variable
    
    while mesg != 'q':
        if mesg is not None:
            # Split the input message into command and arguments
            cmd_args = [cmd for cmd in mesg.split(" ") if cmd]            
            cmd = cmd_args[0].lower() # Extract the command and convert to lowercase
            args = cmd_args[1:] # Extract the arguments
            
            # Validate the command and its arguments
            if validate_command(cmd, args):
                
                # Prepare the request string
                args_str = ''
                if len(args) > 0:
                    args_str = f'{args[0]}'
                request = f'{cmd} {args_str}'
                
                # Send the request to the server
                s.send(request.encode('utf-8'))
                
                # Receive the response from the server
                fromServer = s.recv(DATA_LIMIT).decode('utf-8')
                response = json.loads(fromServer)
                
                # Handle the response based on the command
                if cmd in ['ls']:
                    print_ls_response(response)
                elif cmd in ['lsr']:
                      print_lsr_response(response)
                elif cmd in ['cd']:
                    print_cd_response(response)
        # Prompt the user for the next command           
        mesg = input("Enter choice: ")
        
    if mesg == 'q':
        # Send quit command to the server
        s.send(mesg.encode('utf-8'))
        
    

