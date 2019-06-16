""" 
Tung X. Dao and Jasper Edbrooke
data.py handles the file storage and retrieval for the GUI
"""
import sqlite3
import sys
import os
import requests
import json

class SqlDb():
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
        else:
            self.conn = sqlite3.connect(self.DB_NAME)
            self.cur = self.conn.cursor()

    def add_to_db(self, image, metadata):
        pass


    def download_nimages_with_category(self, category, n, queue):
        """ 
        Downloads the images to the db with multithreading
        If image does not have tag, assume the tag is not in the immage
        Returns a generator that returns the images with their data
        """
        headers = {'Authorization': 'Client-ID ' + self.CLIENT}
        url = 'https://api.imgur.com/3/gallery/search/?q=cats'
        response = requests.request('GET', url, headers = headers)
        # r = requests.get("https://api.imgur.com/3/tags", headers={'Authorization': self.CLIENT})
        data = json.loads(response.text)
        data = data['data']
        i = 1
        for item in data:
            print(i)
            if 'images' in item.keys():
                for image in item['images']:
                    print(image['link'])
            else:
                print(item['link'])
            i += 1
        print()
        gen = [] # Some sort of generator
        return gen

    def get_images_from_category(self, tag):
        """ 
        returns that generagtor of images
        """

        gen = []
        return gen

    def get_image(self, img_id):
        pass

    def get_count_of_tag(self, tag):
        """ 
        REturns a tuple of tag and count
        """
        tag = []
        count = []
        return (tag, count)

    def change_tag(self): # optional
        """ 
        Change tag of images 
        """
        pass

    def get_categories(self):
        """ 
        Returns a list of all the categories on the db (also count of each category)
        """
        categories = []
        return categories

    def delete_images(self, img_list):
        """ 
        Deletes images from list
        """
        success = True
        return success


    def export_images(self, tag, directory):
        """ 
        Saves all the images with tag into directory        
        """
        success = True
        return success

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
                        nsfw INTEGER,
                        filetype INTEGER,
                        sizetype INTEGER,
                        FOREIGN KEY (filetype) REFERENCES Filetypes(id),
                        FOREIGN KEY (sizetype) REFERENCES Sizes(id)                  
                        );''')

            self.cur.execute('''CREATE TABLE Categories (
                        id INTEGER NOT NULL PRIMARY KEY,
                        category TEXT                        
                        );''')

            self.cur.execute('''CREATE TABLE Filetypes (
                        id INTEGER NOT NULL PRIMARY KEY,
                        filetype TEXT                        
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
    db.get_nimages_with_category('cats', 30)