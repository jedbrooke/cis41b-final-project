from bs4 import BeautifulSoup as bs
import tkinter as tk

"""utility functions"""

def get_xml(path):
	file = open(path)
	soup = bs(file,"lxml")
	return soup

def get_attribute(tag,attr,cast=str):
	try:
		return cast(tag[attr])
	except KeyError as e:
		return None
GRID_ARGS = {
	"padx":int,
	"pady":int,
	"sticky":str,
	"row":int,
	"column":int,
}
def get_grid(tag):
	return dict([(arg,get_attribute(tag,arg,kind))\
	 for arg,kind in GRID_ARGS.items()\
	  if get_attribute(tag,arg,kind) is not None])


class window(tk.Tk):
	"""docstring for window"""
	def __init__(self,soup=None,path=""):
		self.HEAD_ACTIONS = {
			"title":self.set_title,
			"geometry":self.set_geometry
		}
		
		self.BODY_ACTIONS = {
			"button":self.create_button,
			"label":self.create_label,
			"frame":self.create_frame,
		}
		super().__init__()
		self.grab_set()
		self.focus_set()
		if soup is None and path is not "":
			_initPath(path)
		elif soup is not None and path is "":
			self.soup = soup

		self.buildElements()

	def _initPath(self,path):
			self.soup = get_xml(path)	

	def buildElements(self):
		self.buildHead(self.soup.head)
		self.buildBody(self.soup.body,self)

	def buildHead(self,soup):
		for tag in soup:
			if tag.name is not None:
				self.HEAD_ACTIONS[tag.name](tag)
	def buildBody(self,soup,parent):
		for tag in soup:
			if tag.name is not None:
				self.BODY_ACTIONS[tag.name](tag,parent)

	def set_title(self,title):
		self.title(title.text)

	def set_geometry(self,geometry):
		self.geometry(geometry.text)

	def create_label(self,label,parent):
		tk.Label(parent,text=label.text.strip()).grid(get_grid(label))

	def create_button(self,button,parent):
		tk.Button(parent,text=button.text.strip(),command=lambda:print("hello")).grid(get_grid(button))

	def create_frame(self,frame,parent):
		tk_frame = tk.Frame(parent)
		self.buildBody(frame,tk_frame)
		tk_frame.grid(get_grid(frame))



def main():
	window(get_xml("gui_pages/main.html")).mainloop()

main()