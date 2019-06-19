""" 
Tung X. Dao and Jasper Edbrooke
This server handles database checking and downloading of the large full sized files
"""

import socket
import serverdata
import pickle

HOST = 'localhost'
PORT = 5551

class Server():
    def __init__(self, timeout = 60):
        with socket.socket() as s:
            try:
                # Listen for the clients
                s.bind((HOST, PORT))
                print("The training session is at:", str(HOST)+":"+str(PORT), 'and will last for', str(timeout), 'seconds.')
                s.listen()
                (conn, addr) = s.accept()
                print(addr, 'connected.')
                options = {'send_data': self.get_data_from_client, 
                           'clear_db': self.clear_db,
                           'check_if_trainable': self.check_db_for_training,
                           'train': self.train_network}

                while True:
                    from_client = pickle.loads(conn.recv(1024))

                    if from_client['type'] == 'q':
                        break
                    else:                        
                        options[from_client['type']](from_client, conn)   

            except socket.timeout:
                print('time out')
                # break

    def get_data_from_client(self, args):
    """  
    Gets the information of which files to download from client
    """
    pass

    def clear_db(self, db):
    """  
    Resets the db
    """
    db.create_db()

    def check_db_for_training(self):
    """  
    Checks the db for sufficient data to start training
    Suppose sufficient data is >= 2 categories and >= 10 images for testing purposes
    """
    pass

    def train_network(self):
    """  
    Check if sufficient data in the local db and then print message about training
    """
    pass

if __name__ == "__main__":
    s = Server()
