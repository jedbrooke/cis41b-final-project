import socket
import socket
import pickle

HOST = '127.0.0.1'
PORT = 5551

def get_choice(options):
    """ 
    Make sure user enters sane option 
    """
    print('1: send data')
    print('2: clear db')
    print('3: Check if db is trainable')
    print('4: train network')
    print('q: quit')
    choice = ''

    while choice not in tuple('1234q'):
        choice = input('Enter your choice: ')
    if choice == 'q':
        pass
    else:
        choice = [i for i in options.keys()][int(choice) - 1]
    
    return choice

def send_data(data_dict):
    data_dict['data'] = [['https://i.imgur.com/zQrpML1.jpg'],
                        ['dogs']]
    s.send(pickle.dumps(data_dict))

def clear_db(data_dict):
    s.send(pickle.dumps(data_dict))

def check_db_for_training(data_dict):
    s.send(pickle.dumps(data_dict))

def train_network(data_dict):
    s.send(pickle.dumps(data_dict))

with socket.socket() as s: # create a socket
    s.connect((HOST, PORT)) # connect to a server at a particular host and port
    print("Client connect to:", HOST, "port:", PORT)
    
    options = {'send_data': send_data, 
                'clear_db': clear_db,
                'check_if_trainable': check_db_for_training,
                'train': train_network,
                }
    choice = get_choice(options)

    while choice in options.keys() or choice == 'q':
        data_dict = {'command': choice}
        if choice == 'q':
            s.send(pickle.dumps(data_dict))
            break
        options[choice](data_dict)
        choice = get_choice(options)