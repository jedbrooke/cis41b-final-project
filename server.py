""" 
Tung X. Dao
This server handles database checking and downloading of the large full sized files
"""

import socket
import serverdb
import pickle
import threading
import queue
import sys

HOST = 'localhost'
PORT = 5551

class Server():
    MAX_CLIENTS = 4

    def __init__(self, timeout = 5):
        """
        The server handles up to MAX_CLIENTS connecting at a time and accepts commands.
        This server runs forever and does not get shut down unless a command to shut down is sent when there is only 1 client connected
        """
        print('Main thread:', threading.get_ident())

        threads = []
        self.instructions_queue = queue.Queue()
        self.is_running = True
        self.options = {'send_data': self.get_data_from_client, 
                        'clear_db': self.clear_db,
                        'check_if_trainable': self.check_db_for_training,
                        'train': self.train_network,
                        # 'shut_down': self.shut_down
                        }
        self.n_connected_clients = 0
        self.lock = threading.Lock()

        # Start queue handler thread
        db_thread = threading.Thread(target=self.run)
        # db_thread.setDaemon(True)
        db_thread.start()
        threads.append(db_thread)
        
        with socket.socket() as s:
            s.settimeout(timeout)
            # Listen for the clients
            s.bind((HOST, PORT))
            print("The training session is at:", str(HOST)+":"+str(PORT), 'with an exit timeout of', str(timeout), 'seconds.')
            s.listen()
            
            while self.is_running and self.n_connected_clients <= self.MAX_CLIENTS:
                try: 
                    (conn, addr) = s.accept()
                    with self.lock:
                        self.n_connected_clients += 1
                    print(addr, 'connected.')
                    t = threading.Thread(target = self.get_client_choice, args = (s, conn))
                    threads.append(t)
                    t.start()
                except socket.timeout:
                    pass
                    # print('time out')
                    # break  
        
        t.join()
        print('exit')             

    def run(self):
        """  
        Thread that handles the requests to the db, which in this implementation handles a single instruction thread.
        """
        print('Run thread:', threading.get_ident())
        self.db = serverdb.SqlDb()

        while self.is_running:
            try:
                function, args = self.instructions_queue.get(timeout=1)
                self.options[function](*args)
            except queue.Empty:
                # print(str(e))
                pass

        # Close connection with db by deleting the db object
        del self.db
        print('run ended')

    def add_instruction(self,instruction,*args):
        """ 
        Adds instructions to the db queue 
        """
        self.instructions_queue.put((instruction, (*args,)))

    def get_client_choice(self, s, conn):
        """  
        Get client choice and add to queue
        """
        while self.is_running:
            from_client = pickle.loads(conn.recv(1024))

            if from_client['command'] == 'q':
                with self.lock:
                    self.n_connected_clients -= 1
                break
            elif from_client['command'] == 'shut_down':
                self.shut_down(conn)
            else:                        
                self.add_instruction(from_client['command'], from_client, conn)        

    def get_data_from_client(self, req, conn):
        """  
        Gets the information of which files to download from client
        """
        msg = 'Getting data from client'
        conn.send(pickle.dumps(msg))
        print(msg)
        urls = req['data'][0]
        tags = req['data'][1]

        # download and add urls and tags to DB
        msg = 'downloading to db'
        conn.send(pickle.dumps(msg))
        print(msg)
        for url, tag in zip(urls, tags):
            self.db.add_to_db(url, tag)        

    def clear_db(self, req, conn):
        """  
        Resets the db
        """
        msg = 'Restting db.'
        conn.send(pickle.dumps(msg))
        print(msg)
        self.db.create_db()
        msg = 'DB reset successful.'
        conn.send(pickle.dumps(msg))
        print(msg)

    def check_db_for_training(self, req, conn):
        """  
        Checks the db for sufficient data to start training
        Suppose sufficient data is >= 2 categories and >= 10 images for testing purposes
        """
        n_categories = self.db.cur.execute('''SELECT COUNT(c.id) FROM categories c;''').fetchone()[0]
        n_images = self.db.cur.execute('SELECT COUNT(i.id) FROM Images i;').fetchone()[0]
        
        ready = False
        if n_categories < 2 and n_images < 10:
            msg = 'DB needs more categories and images'
            conn.send(pickle.dumps(msg))
            print(msg)
        elif n_images < 10: # Check this n_images condition
            msg = 'DB needs more images'
            conn.send(pickle.dumps(msg))
            print(msg)
        elif n_categories < 2:
            msg = 'DB needs more categories'
            conn.send(pickle.dumps(msg))
            print(msg)
        else:
            msg = 'DB is good to go'
            conn.send(pickle.dumps(msg))
            print(msg)
            ready = True

        return ready

    def train_network(self, req, conn):
        """  
        Check if sufficient data in the local db and then print message about training
        """
        if self.check_db_for_training(req, conn):
            msg = 'Training in progress. Please come back in a few hours.'
            conn.send(pickle.dumps(msg))
            print(msg)
        else:
            msg = 'Not enough data available. Please run db check.'
            conn.send(pickle.dumps(msg))
            print(msg)
    
    def shut_down(self, conn):
        if self.n_connected_clients <= 1:
            status = True
            self.is_running = False
            conn.send(pickle.dumps(status))
            print('Good bye')
            # quit()
        else:
            status = False
            print('There are', self.n_connected_clients, 'clients still connected.')
            conn.send(pickle.dumps(status))

if __name__ == "__main__":
    s = Server()
