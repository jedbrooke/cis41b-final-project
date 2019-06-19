""" 
Tung X. Dao and Jasper Edbrooke
This server handles database checking and downloading of the large full sized files
"""

import socket

HOST = 'localhost'
PORT = 5551

def get_info(info):
    pass

def clear_db():
    pass

def check_db_for_training():
    pass

def train_network():
    pass

if __name__ == "__main__":
    with socket.socket() as s:
        timeout = 20
        try:
            # Listen for the clients
            s.bind((HOST, PORT))
            print("The training session is at:", str(HOST)+":"+str(PORT), 'and will last for', str(timeout), 'seconds.')
            s.listen()
            (conn, addr) = s.accept()
            print(addr, 'connected.')

        except socket.timeout:
            print('time out')
            # break