import socket
import socket
import pickle

HOST = '127.0.0.1'
PORT = 5551

def get_choice():
    """ 
    Make sure user enters sane option 
    """
    print('1: send data')
    print('2: clear db')
    print('3: Check if db is trainable')
    print('4: train network')
    print('q: quit')
    choice = ''

    while choice not in tuple('psq'):
        choice = input('Enter your choice: ')
    
    return choice

def send_data():
    pass

def clear_db():
    pass

def check_db_for_training():
    pass

def train_network():
    pass

with socket.socket() as s: # create a socket
    s.connect((HOST, PORT)) # connect to a server at a particular host and port
    print("Client connect to:", HOST, "port:", PORT)
    
    options = {'send_data': send_data, 
                'clear_db': clear_db,
                'check_if_trainable': check_db_for_training,
                'train': train_network}
    choice = get_choice()

    while choice in options.keys():
        data_dict = {'type': choice}
        if choice == 'q':
            s.send(pickle.dumps(data_dict))
            break
        options[choice](data_dict)
        choice = get_choice()