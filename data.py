""" 
Tung X. Dao and Jasper Edbrooke
data.py handles the file storage and retrieval for the GUI
"""
import sqlite3
import sys

class SqlDb():
    # Set up connection
    DBNAME = 'images.db'
    def __init__(self):
        """ 
        Set up db if none is found
        """
        # Check for existance of db
        self.create_db()

    def add_to_db(self, image, metadata):
        pass

    def get_image(self, img_id):
        pass

    def get_count_of_tag(self, tag):
        pass

    def delete_image(self, img_id):
        pass

    def create_db(self):
        self.conn = sqlite3.connect(self.DBNAME)
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
        #

if __name__ == "__main__":
    db = SqlDb()