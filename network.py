""" 
Tung X. Dao and Jasper Edbrooke
This server handles database checking and downloading of the large full sized files
"""

import socket

HOST = 'localhost'
PORT = 5551


def get_info_from_client(info):
    """  
    Gets the information of which files to download from client
    """
    pass

def clear_db(db):
    """  
    Resets the db
    """
    db.create_db()

def check_db_for_training():
    """  
    Checks the db for sufficient data to start training
    Suppose sufficient data is >= 2 categories and >= 10 images for testing purposes
    """
    pass

def train_network():
    """  
    Check if sufficient data in the local db and then print message about training
    """
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