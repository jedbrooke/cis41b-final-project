import socket
import gui_engine as GUI

import sqldb

SERVER_ADDR = "127.0.0.1"
SERVER_PORT = 5551

class SearchForm(GUI.Form):
	"""docstring for Form"""
	def __init__(self, arg):
		super(Form, self).__init__()
		self.arg = arg

	def submit(self):
		


class client():
	def __init__(self):
		self.socket = socket.socket()
		self.gui = window(get_xml("gui_pages/main.html"),main=True)
		self.db = db()

		with self.socket:
			self.socket.connect((SERVER_ADDR,SERVER_PORT))

	def send_query_to_server(q,settings):
		self.socket.send()

	def send_query_to_db(q,settings):
		images = db.get_nimages_with_category()
		#images is a list/generator of the ImageTk.PhotoImage()'s
		#pass images ot gui
		pass

	def request_export(category):
		db.export_images(category,directory)


	def recieve_images():
		self.socket.recv()
		return images

	def recieve_tags(category):
		self.socket.recv()
		return tags

	def send_train(category):
		self.socket.send()
		self.socket.recv()
		return data

	def get_categories():
		pass

	def display_results(images):
	    #for image in images:
	    #generate html for the images, pass that to gui Window

	    pass

	def generate_tag_count_graph(tag_counts):
	    #plot the tags based on occurrence
	    #tag_counts is tuple of list of tags and list of counts
	    pass






if __name__ == '__main__':
	main()
