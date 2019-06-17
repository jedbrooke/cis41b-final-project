""" 
Tung X. Dao and Jasper Edbrooke
data.py handles the file storage and retrieval for the GUI
"""
import sqlite3
import sys
import os
import requests
import json
from PIL import ImageTk, Image 

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


    def add_to_db(self, image, metadata):
        """ 
        Adds image to db
        image is an image binary
        """
        self.cur.execute('''INSERT INTO  Filetypes (filetype) VALUES (?) ''', (metadata['filetype'],))
        self.cur.executemany('''INSERT INTO  Categories (category) VALUES (?) ''', metadata['categories'])
        self.cur.execute('''INSERT INTO  Images (file, url, nsfw, sizetype) VALUES (?, ?, ?, ?); ''', (image, metadata['url'], metadata['nsfw'], metadata['sizetype']))
        img_id = self.cur.execute('''SELECT id FROM Images WHERE url = (?)''', (metadata['url'],)).fetchone()[0]
        sql_stmt = '''SELECT id FROM Categories WHERE category in ({})'''.format(','.join(['?']*len(metadata['categories'])))
        args = [i[0] for i in metadata['categories']]
        category_id = self.cur.execute(sql_stmt, args).fetchall()[0]
        img_cat_list = [(img_id, i[0]) for i in self.cur.execute(sql_stmt, args).fetchall()]
        self.cur.executemany('''INSERT INTO  Image_Categories (img_id, category_id) VALUES (?, ?) ''', img_cat_list)
        self.conn.commit() ## Is there overhead for doing this a lot?

    def download_nimages_with_category(self, category, n = 60, queue = None):
        """ 
        Downloads the images to the db with multithreading
        If image does not have tag, assume the tag is not in the immage
        Returns a generator that returns the images with their data
        """
        headers = {'Authorization': 'Client-ID ' + self.CLIENT}
        url = 'https://api.imgur.com/3/gallery/search/?q={}'.format(category)
        response = requests.request('GET', url, headers = headers)
        # r = requests.get("https://api.imgur.com/3/tags", headers={'Authorization': self.CLIENT})
        data = json.loads(response.text)
        data = data['data']
        i = 1
        for item in data:
            print(i)

            if 'images' in item.keys():
                album_categories = [(i['name'],) for i in item['tags']] 

                for image in item['images']:
                    url = image['link']
                    page = requests.get(url)
                    # with open('temp.jpg', 'wb') as f:
                    #     f.write(page.content)
                    if image['tags'] != []:
                        print('tag found in image and needs to be examined')
                        print(image['tags'])

                    metadata = {'url': url, 'nsfw': image['nsfw'], 'filetype': image['link'][-3:], 'sizetype': None, 'categories': album_categories}
                    
                    if metadata['categories'] == []: # Sometimes an album won't get tagged, but will show up in the title, force the category
                        metadata['categories'] = [category]

                    self.add_to_db(page.content, metadata)
            else:
                print(item['link'])
            i += 1
            if i > 5: break ## break
        
        return self.get_images_from_category(category)

    def get_images_from_category(self, category):
        """ 
        returns a generator of images and metadata
        """
        while True:
            results = self.cur.execute('''SELECT * FROM IMAGES ''').fetchall()
            if results:
                for result in results:
                    yield result
                break ## Should this be stop iteratrion?
            else:
                break ## Should this be stop iteratrion?

    def get_image(self, img_id):
        pass

    def get_count_of_tags(self, category = None):
        """ 
        Returns a list of tuples of tag and count
        """
        if category == None:
        # Get list of all tags
        self.cur.execute('''SELECT Categories.category, count(Image_Categories.category_id)
                            FROM Image_Categories JOIN Categories ON Image_Categories.category_id = Categories.id 
                            GROUP BY Image_Categories.category_id;''')
        return self.cur.fetchall()
        else: # only get tags associated with some tag
            self.cur.execute('''SELECT c.category, count(ic.category_id) 
                                FROM Images i JOIN Image_Categories ic ON i.id = ic.img_id JOIN Categories c ON ic.category_id = c.id 
                                WHERE i.id IN (SELECT i.id FROM Images i 
                                                JOIN Image_Categories ic ON i.id = ic.img_id JOIN Categories c ON ic.category_id = c.id 
                                                WHERE c.category = ?)
                                GROUP BY ic.category_id;''', (category,)) 


    def change_tag(self): # optional
        """ 
        Change tag of images 
        """
        pass

    def get_categories(self):
        """ 
        Returns a list of all the categories on the db (also count of each category)
        """
        return self.cur.execute('SELECT category FROM Categories;').fetchall()

    def delete_images(self, img_urls):
        """ 
        Deletes images from list, img_list is a list of urls
        """
        ### THIS NEEDS TO BE RESOLVED WITH CASCADE DELETE AND FIX THAT WEIRD MAIN TABLE
        for img_url in img_urls:
            self.cur.execute('DELETE FROM Images WHERE url = ?', (img_url,) )
        self.conn.commit()
        return False

    def export_images(self, category, directory = 'imgs'):
        """ 
        Saves all the images with tag into directory        
        """
        gen = self.get_images_from_category(category)
        for i in gen:
            filename = i[2][-11:] # This should be an RE
            with open(os.path.join(directory, filename), 'wb') as f:
                f.write(i[1])
                print('Saved image', filename)
        return True

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
                        url TEXT UNIQUE ON CONFLICT IGNORE,
                        nsfw INTEGER,
                        filetype INTEGER,
                        sizetype INTEGER,
                        FOREIGN KEY (filetype) REFERENCES Filetypes(id),
                        FOREIGN KEY (sizetype) REFERENCES Sizes(id)                  
                        );''')

            self.cur.execute('''CREATE TABLE Categories (
                        id INTEGER NOT NULL PRIMARY KEY,
                        category TEXT UNIQUE ON CONFLICT IGNORE                     
                        );''')

            self.cur.execute('''CREATE TABLE Filetypes (
                        id INTEGER NOT NULL PRIMARY KEY,
                        filetype TEXT UNIQUE ON CONFLICT IGNORE
                        );''') 

            self.cur.execute('''CREATE TABLE Image_Categories (
                        img_id INTEGER NOT NULL,
                        category_id INTEGER NOT NULL,
                        PRIMARY KEY (img_id, category_id) ON CONFLICT IGNORE,
                        FOREIGN KEY (img_id) REFERENCES Images(id) ON DELETE CASCADE,
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
    category = 'dogs'
    gen = db.download_nimages_with_category(category, 30)

    for i in gen:
        print(i[2])
    tag_counts = db.get_count_of_tags()
    print(tag_counts)
    list_of_categories = db.get_categories()
    print(list_of_categories)
    db.export_images(category)
    
