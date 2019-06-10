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
LISTBOX_ARGS = {
	"height":int,
	"width":int,
	"selectmode":str,
}
def get_grid_args(tag):
	return dict(\
		[(arg,get_attribute(tag,arg,kind))\
	 	for arg,kind in GRID_ARGS.items()\
	  	if get_attribute(tag,arg,kind) is not None])

def get_listbox_args(tag):
	return dict(\
		[(arg,get_attribute(tag,arg,kind))\
	 	for arg,kind in LISTBOX_ARGS.items()\
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
			"scrollbox":self.create_scrollbox,
			"listbox":self.create_listbox,
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
	def buildList(self,elements,listbox):
		listbox.insert(tk.END,*[item.text for item in elements.find_all("li")])


	def set_title(self,title):
		self.title(title.text)

	def set_geometry(self,geometry):
		self.geometry(geometry.text)

	def create_label(self,label,parent):
		tk.Label(parent,text=label.text.strip()).grid(get_grid_args(label))

	def create_button(self,button,parent):
		tk.Button(parent,text=button.text.strip(),command=lambda:print("hello")).grid(get_grid_args(button))

	def create_frame(self,frame,parent):
		tk_frame = tk.Frame(parent)
		self.buildBody(frame,tk_frame)
		tk_frame.grid(get_grid_args(frame))

	def create_listbox(self,listbox,parent): 
		if get_attribute(listbox,"scroll",bool):
			self.create_scrollbox(listbox,parent)
		else :
			tk_listbox = tk.Listbox(parent,**get_listbox_args(listbox))
			self.buildList(listbox,tk_listbox)
			tk_listbox.grid(get_grid_args(listbox))
			


	def create_scrollbox(self,scrollbox,parent):
		frame = tk.Frame(parent)
		scrollbar = tk.Scrollbar(frame,orient=tk.VERTICAL)
		scrollbar.grid(row=0,column=1,sticky=tk.N+tk.S)
		listbox = tk.Listbox(frame,**get_listbox_args(scrollbox),yscrollcommand=scrollbar.set)
		listbox.grid(row=0,column=0,sticky=tk.N+tk.S+tk.E+tk.W)
		self.buildList(scrollbox,listbox)
		scrollbar['command'] = listbox.yview
		frame.grid(get_grid_args(scrollbox))





def main():
	window(get_xml("gui_pages/main.html")).mainloop()

main()