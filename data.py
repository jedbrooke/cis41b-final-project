""" 
Tung X. Dao and Jasper Edbrooke
data.py handles the file storage and retrieval for the GUI
"""
import sqlite3
import sys
import os

class SqlDb():
    # Set up connection
    DB_NAME = 'images.db'
    CLIENT = 'd46861ef7ecb2dc'
    CLIENT_SECRET = '8889ad15753f373b14b2cfb74de86004837c7137'
    
    def __init__(self):
        """ 
        Set up db if none is found
        """
        if not os.path.isfile(self.DB_NAME):
            self.create_db()
            print('created new db')

    def add_to_db(self, image, metadata):
        pass

    def get_image(self, img_id):
        pass

    def get_count_of_tag(self, tag):
        pass

    def delete_image(self, img_id):
        pass

    def create_db(self):
        self.conn = sqlite3.connect(self.DB_NAME)
        self.cur = self.conn.cursor()

        tables = ['Images', 'Image_Categories', 'Categories']

        for table in tables:
            # self.cur.execute('DROP TABLE IF EXISTS ?', (table,)) # Why does this not work?
            self.cur.execute('DROP TABLE IF EXISTS {};'.format(table))

        # Create tables
        try:
            self.cur.execute('''CREATE TABLE Images (
                        id INTEGER NOT NULL PRIMARY KEY,
                        file BLOB,
                        url TEXT,
                        nsfw INTEGER                        
                        );''')

            self.cur.execute('''CREATE TABLE Categories (
                        id INTEGER NOT NULL PRIMARY KEY,
                        category TEXT                        
                        );''')

            self.cur.execute('''CREATE TABLE Image_Categories (
                        img_id INTEGER NOT NULL,
                        category_id INTEGER NOT NULL,
                        FOREIGN KEY (img_id) REFERENCES Images(id),
                        FOREIGN KEY (category_id) REFERENCES Categories(id)
                        );''')
        except sqlite3.OperationalError as e:
            print(str(e))
            raise SystemExit
        
        self.conn.commit()

    def __del__(self):
        self.conn.commit()
        self.conn.close()

if __name__ == "__main__":
    db = SqlDb()