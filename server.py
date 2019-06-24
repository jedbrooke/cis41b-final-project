""" 
Tung X. Dao and Jasper Edbrooke
This server handles database checking and downloading of the large full sized files
"""

import socket
import serverdb
import pickle
import threading
import queue

HOST = 'localhost'
PORT = 5551

class Server():
    MAX_CLIENTS = 4
    def __init__(self, timeout = 60):
        """
        The server handles up to MAX_CLIENTS connecting at a time and accepts commands.
        This server runs forever and does not get shut down.
        """
        threads = []
        self.instructions_queue = queue.Queue()
        self.is_running = True
        self.options = {'send_data': self.get_data_from_client, 
                        'clear_db': self.clear_db,
                        'check_if_trainable': self.check_db_for_training,
                        'train': self.train_network}

        # Start queue handler thread
        db_thread = threading.Thread(target=self.run)
        db_thread.start()
        
        with socket.socket() as s:
            try:
                # Listen for the clients
                s.bind((HOST, PORT))
                print("The training session is at:", str(HOST)+":"+str(PORT), 'and will last for', str(timeout), 'seconds.')
                s.listen()

                for i in range(self.MAX_CLIENTS):
                    (conn, addr) = s.accept()
                    
                    print(addr, 'connected.')
                    t = threading.Thread(target = self.get_client_choice, args = (s, conn))
                    threads.append(t)
                    t.start()
            except socket.timeout:
                print('time out')
                # break

    def run(self):
        """  
        Thread that handles the requests to the db, which in this implementation handles a single instruction thread.
        """
        self.db = serverdb.SqlDb()
        while self.is_running:
            function, args = self.instructions_queue.get()
            self.options[function](*args)

    def add_instruction(self,instruction,*args):
        """ 
        Adds instructions to the db queue 
        """
        self.instructions_queue.put((instruction, (*args,)))

    def get_client_choice(self, s, conn):
        """  
        Get client choice and add to queue
        """
        while True:
            from_client = pickle.loads(conn.recv(1024))

            if from_client['command'] == 'q':
                break
            else:                        
                self.add_instruction(from_client['command'], from_client, conn)        

    def get_data_from_client(self, req, conn):
        """  
        Gets the information of which files to download from client
        """
        print('Getting data from client')
        urls = req['data'][0]
        tags = req['data'][1]

        # download and add urls and tags to DB
        print('downloading to db')
        for url, tag in zip(urls, tags):
            self.db.add_to_db(url, tag)        

    def clear_db(self, req, conn):
        """  
        Resets the db
        """
        print('Restting db.')
        self.db.create_db()
        print('DB reset successful.')

    def check_db_for_training(self, req, conn):
        """  
        Checks the db for sufficient data to start training
        Suppose sufficient data is >= 2 categories and >= 10 images for testing purposes
        """
        n_categories = self.db.cur.execute('''SELECT COUNT(c.id) FROM categories c;''').fetchone()[0]
        n_images = self.db.cur.execute('SELECT COUNT(i.id) FROM Images i;').fetchone()[0]
        
        ready = False
        if n_categories < 2 and n_images < 10:
            print('DB needs more categories and images')
        elif n_images < 10: # Check this n_images condition
            print('DB needs more images')
        elif n_categories < 2:
            print('DB needs more categories')
        else:
            print('DB is good to go')
            ready = True

        return ready

    def train_network(self, req, conn):
        """  
        Check if sufficient data in the local db and then print message about training
        """
        if self.check_db_for_training(req, conn):
            print('Training in progress. Please come back in a few hours.')
        else:
            print('Not enough data available. Please run db check.')

if __name__ == "__main__":
    s = Server()
