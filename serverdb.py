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
import re 
import data

class SqlDb(data.SqlDb):
    DB_NAME = 'serverimages.db'

    def __init__(self):
        """ 
        Set up db if none is found
        """
        super().__init__()


    def add_to_db(self, image_url, tag):
        """ 
        Adds image to db from url
        """
        try:
            # Download image from url
            page = requests.get(image_url)
            image = page.content
            metadata = {'categories': tag,
                        'nsfw': None,
                        'sizetype': None,
                        'url': image_url}

            # Add image to db
            # self.cur.execute('''INSERT INTO  Filetypes (filetype) VALUES (?) ''', (metadata['filetype'],))
            self.cur.execute('''INSERT INTO  Categories (category) VALUES (?) ''', (metadata['categories'],))
            self.cur.execute('''INSERT INTO  Images (file, url, nsfw, sizetype) VALUES (?, ?, ?, ?); ''', (image, metadata['url'], metadata['nsfw'], metadata['sizetype']))
            img_id = self.cur.execute('''SELECT id FROM Images WHERE url = (?)''', (metadata['url'],)).fetchone()[0]
            sql_stmt = '''SELECT id FROM Categories WHERE category = ?'''
            # args = [i[0] for i in metadata['categories']]

            img_cat_tuple = (img_id, self.cur.execute(sql_stmt, (metadata['categories'],)).fetchone()[0])
            # img_cat_list = (img_id, i[0]) for i in self.cur.execute(sql_stmt, metadata['categories']).fetch()
            self.cur.execute('''INSERT INTO  Image_Categories (img_id, category_id) VALUES (?, ?) ''', img_cat_tuple)
            self.conn.commit() ## Is there overhead for doing this a lot?
            print('added image to db')

        except sqlite3.OperationalError as e: # pylint: disable=maybe-no-member
            print(str(e))
            return e

    def download_nimages_with_category(self, category, n = 60, queue = None, filter_nsfw = True, blacklist = None):
        """ 
        Downloads the images to the db with multithreading?
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
            
            for image in data:
                # Reject albums
                if image['link'][-3:] != 'jpg':
                    continue
                if image['nsfw'] and filter_nsfw:
                    print('Skipping NSFW Image')
                    continue

                album_categories = [(i['name'],) for i in image['tags']] 

                if set(album_categories).intersection(set(blacklist)):
                    print('Skipping image on blacklist')
                    continue

                url = image['link']
                page = requests.get(url)
                metadata = {'url': url, 'nsfw': image['nsfw'], 'filetype': image['link'][-3:], 'sizetype': None, 'categories': album_categories, 'reject': 0}
                
                # Sometimes an album won't get tagged, but will show up in the title, force the category
                if metadata['categories'] == []:
                    metadata['categories'] = [(category,)]
                
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

if __name__ == "__main__":
    db = SqlDb()
    category = 'dogs'
    gen = db.download_nimages_with_category(category, 100)

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
    gen = db.download_nimages_with_category(category, 100)

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
    