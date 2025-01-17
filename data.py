""" 
Tung X. Dao
data.py handles the file storage and retrieval for the GUI
"""
import sqlite3
import sys
import os
import requests
import json
from PIL import ImageTk, Image
import re 

class SqlDb():
    DB_NAME = 'images.db'
    CLIENT = 'd46861ef7ecb2dc'

    def __init__(self):
        """ 
        Set up db if none is found
        """
        if not os.path.isfile(self.DB_NAME):
            self.create_db()
            print('created new db')
        else:
            self.conn = sqlite3.connect(self.DB_NAME) # pylint: disable=maybe-no-member
            self.cur = self.conn.cursor()

        # self. = https://api.imgur.com/oauth2/authorize?client_id=YOUR_CLIENT_ID&response_type=REQUESTED_RESPONSE_TYPE&state=APPLICATION_STATE

        # Do other stuff

    def add_to_db(self, image, metadata):
        """ 
        Adds image to db
        image is an image binary
        """
        try:
            # Insert filetype
            self.cur.execute('''INSERT INTO  Filetypes (filetype) VALUES (?) ''', (metadata['filetype'],))

            # Insert Categories
            self.cur.executemany('''INSERT INTO  Categories (category) VALUES (?) ''', metadata['categories'])

            # Insert image and metadata
            self.cur.execute('''INSERT INTO  Images (file, url, nsfw, sizetype, reject) VALUES (?, ?, ?, ?, ?); ''', (image, metadata['url'], metadata['nsfw'], metadata['sizetype'], 0))

            # Get filetype and category ids
            filetype_id = self.cur.execute('''SELECT id FROM Filetypes WHERE filetype = (?)''', (metadata['filetype'],)).fetchone()[0]
            self.cur.execute('''UPDATE Images SET filetype = ? WHERE url = ?''', (filetype_id, metadata['url']))

            img_id = self.cur.execute('''SELECT id FROM Images WHERE url = (?)''', (metadata['url'],)).fetchone()[0]
            sql_stmt = '''SELECT id FROM Categories WHERE category in ({})'''.format(','.join(['?']*len(metadata['categories'])))
            args = [i[0] for i in metadata['categories']]
            img_cat_list = [(img_id, i[0]) for i in self.cur.execute(sql_stmt, args).fetchall()]
            self.cur.executemany('''INSERT INTO  Image_Categories (img_id, category_id) VALUES (?, ?) ''', img_cat_list)

            self.conn.commit() ## Is there overhead for doing this a lot?
        except sqlite3.OperationalError as e: # pylint: disable=maybe-no-member
            print(str(e))
            return e

    def download_nimages_with_category(self, category, n = 60, queue = None, filter_nsfw = True, blacklist = None):
        """ 
        Downloads the images to the db with multithreading
        If image does not have tag, assume the tag is not in the immage
        Returns a generator that returns the images with their data
        """
        if not blacklist :
            blacklist = []

        page_no = 0
        i = 1

        while i < n:
            headers = {'Authorization': 'Client-ID ' + self.CLIENT}
            url = 'https://api.imgur.com/3/gallery/search/top/all/{}?q={} ext: jpg NOT album'.format(page_no, category)
            response = requests.request('GET', url, headers = headers)
            data = json.loads(response.text)
            data = data['data']

            if not data:
                print('no results found')
                return False
            
            for image in data:
                # Reject albums
                if image['link'][-3:] != 'jpg':
                    continue

                # Reject NSFW if flag
                if image['nsfw'] and filter_nsfw:
                    print('Skipping NSFW Image')
                    continue

                # Skip image if already in db
                if self.cur.execute('SELECT EXISTS(SELECT 1 from Images WHERE url = ?)', (image['link'],)).fetchone()[0]:
                    print('Image in DB already.')
                    continue

                album_categories = [(i['name'],) for i in image['tags']] 
                # Sometimes an album won't get tagged, but will show up in the title, force the category
                if not album_categories:
                    album_categories = [(category,)]

                if set([i['name'] for i in image['tags']]).intersection(set(blacklist)):
                    print('Skipping image on blacklist')
                    continue

                url = image['link']
                url_thumb = url[:-4] + 'm' + url[-4:]
                page = requests.get(url_thumb)
                metadata = {'url': url, 'nsfw': image['nsfw'], 'filetype': image['link'][-3:], 'sizetype': 'm', 'categories': album_categories, 'reject': 0}
                
                # # Sometimes an album won't get tagged, but will show up in the title, force the category
                # if metadata['categories'] == []:
                #     metadata['categories'] = [(category,)]
                
                # Some images don't have the tag, but show up in the results because the word appears in the title
                if category not in metadata['categories']: 
                    metadata['categories'].append((category,))

                self.add_to_db(page.content, metadata)
                print('Downloaded', i, 'images of', n)
                i += 1

                if i > n: 
                    break   

            if i > n: 
                break 
            # Get the next page of images
            page_no += 1
        
        return self.get_images_from_category(category)

    def get_images_from_category(self, category):
        """ 
        returns a generator of images and metadata
        """
        while True:
            results = self.cur.execute('''SELECT * FROM Images i JOIN Image_Categories ic ON i.id = ic.img_id
                                            JOIN Categories c ON ic.category_id = c.id 
                                            WHERE c.category = ? AND IFNULL(i.reject, 0) = 0''', (category,)).fetchall()
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
            return self.cur.fetchall()

    def change_tag(self): # optional
        """ 
        Change tag of images 
        """
        pass
    
    def get_categories(self, count = False):
        """ 
        Returns a list of all the categories on the db (also count of each category)
        """
        if count:
            return self.cur.execute('''SELECT c.category, COUNT(ic.category_id) AS category_count
                                FROM Categories c JOIN Image_Categories ic ON c.id = ic.category_id 
                                GROUP BY ic.category_id
                                ORDER BY category_count;''').fetchall()
        else: 
            return self.cur.execute('''SELECT c.category
                                FROM Categories c JOIN Image_Categories ic ON c.id = ic.category_id 
                                GROUP BY ic.category_id
                                ORDER BY COUNT(ic.category_id) DESC;''').fetchall()

    def delete_images(self, img_urls):
        """ 
        Deletes images from list, img_list is a list of urls
        """
        ### THIS COULD BE RESOLVED WITH CASCADE DELETE AND ONLY IF THAT WEIRD MAIN TABLE ISSUE IS FIXED
        for img_url in img_urls:
            self.cur.execute('DELETE FROM Images WHERE url = ?', (img_url,) )
        self.conn.commit()
        return False

    def reject_images(self, img_urls):
        """  
        Set some list of imgurls to reject
        """
        for img_url in img_urls:
            self.cur.execute('''UPDATE Images SET reject = 1 WHERE url = ?;''', (img_url,))
        self.conn.commit()

    def export_images(self, category, directory = 'imgs'):
        """ 
        Saves all the images with tag into directory        
        """
        gen = self.get_images_from_category(category)

        if not os.path.exists(os.path.join(directory, category)):
            os.makedirs(os.path.join(directory, category))

        for i in gen:
            m = re.search(r"[\w]*\.[\w]*$", i[2])
            filename = i[2][m.start():m.end()] # This should be an RE

            with open(os.path.join(directory, category, filename), 'wb') as f:
                f.write(i[1])
                print('Saved image', filename)

        return True

    def create_db(self):
        self.conn = sqlite3.connect(self.DB_NAME) # pylint: disable=maybe-no-member
        self.cur = self.conn.cursor()   

        tables = ['Images', 'Image_Categories', 'Categories','Filetypes']

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
                        reject INTEGER,
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
        except sqlite3.OperationalError as e: # pylint: disable=maybe-no-member
            print(str(e))
            raise SystemExit
        
        self.conn.commit()

    def __del__(self):
        self.conn.commit()
        self.conn.close()

if __name__ == "__main__":
    db = SqlDb()
    category = 'de anza student'
    gen = db.download_nimages_with_category(category, 10, filter_nsfw=True, blacklist=['aww'])

    category = 'dogs'
    gen = db.download_nimages_with_category(category, 10, filter_nsfw=True, blacklist=['aww'])

    # for i in gen:
    #     print(i[2])

    print('Count of Tags related to category:')
    print(db.get_count_of_tags(category))
    print('All Categories:')
    print(db.get_categories())
    print('Categories and counts:')
    print(db.get_categories(count = True))
    print('Exporting images:')
    db.export_images(category)

    category = 'cats'
    gen = db.download_nimages_with_category(category, 10, blacklist= ['dogs', 'aww'])

    # for i in gen:
    #     print(i[2])
    
    print('Count of Tags related to category:')
    print(db.get_count_of_tags(category))
    print('All Categories:')
    print(db.get_categories())
    print('Categories and counts:')
    print(db.get_categories(count = True))
    print('Exporting images:')
    db.export_images(category)
    
