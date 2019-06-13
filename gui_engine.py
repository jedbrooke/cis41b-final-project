from bs4 import BeautifulSoup as bs
import tkinter as tk
from tkinter import Canvas

def display_results(images):
    #for image in images:
    #generate html for the images, pass that to gui Window

    pass

def generate_tag_count_graph(tag_counts):
    #plot the tags based on occurrence
    #tag_counts is tuple of list of tags and list of counts
    pass

"""utility functions"""

def get_xml(path):
    file = open(path)
    soup = bs(file,"lxml")
    return soup

def bool_from_str(s):
    return s.lower() == "true"

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

BUTTON_ARGS = {
    "link":str,
    "action":str,
    "btype":str,
    "title":str
}

ELEMENT_ARGS = {
    "grid":GRID_ARGS,
    "listbox":LISTBOX_ARGS,
    "button":BUTTON_ARGS,
}

def get_element_args(tag,element):
    return dict(\
        [(arg,get_attribute(tag,arg,kind))\
        for arg,kind in ELEMENT_ARGS[element].items()\
        if get_attribute(tag,arg,kind) is not None])

def get_grid_args(tag):
    return get_element_args(tag,"grid")

def get_listbox_args(tag):
    return get_element_args(tag,"listbox")

def get_button_args(tag):
    return get_element_args(tag,"button")

class Button():
    def __init__(self, link=None, action=None, btype=None, title=None):
        self.link = link
        self.action = action
        self.btype = btype
        self.title = title
        print(link and not btype)
        if link and not btype:
            self.btype = "link"
        print("creating button",self.link,self.btype)
        

class Window():
    """docstring for Window"""
    def __init__(self,soup=None,path=None,main=False,master=None):
        self.HEAD_ACTIONS = {
            "title":self.set_title,
            "geometry":self.set_geometry
        }
        
        self.BODY_ACTIONS = {
            "button":self.create_button,
            "label":self.create_label,
            "div":self.create_frame,
            "scrollbox":self.create_scrollbox,
            "listbox":self.create_listbox,
        }


        self.buttons = {}

        if main:
            self.win = tk.Tk()
        else:
            self.win = tk.Toplevel()
            self.win.transient(master=master)
            self.win.grab_set()
            self.win.focus_set()
        self.main_frame = tk.Frame(self.win)
        #self.win.resizable(False,False)
        if soup is None and path is not None:
            _initPath(path)
        elif soup is not None and path is None:
            self.soup = soup

        self.buildElements()
        self.main_frame.grid()
        self.win.mainloop()

    def _initPath(self,path):
            self.soup = get_xml(path)   

    def buildElements(self):
        self.buildHead(self.soup.head)
        self.buildBody(self.soup.body,self.main_frame)

    def buildHead(self,soup):
        for tag in soup:
            if tag.name is not None:
                self.HEAD_ACTIONS[tag.name](tag)

    def buildBody(self,data,container):
        for tag in data:
            if tag.name is not None:
                self.BODY_ACTIONS[tag.name](tag,container)

    def buildList(self,elements,listbox):
        listbox.insert(tk.END,*[item.text for item in elements.find_all("li")])


    def set_title(self,title):
        self.win.title(title.text)

    def set_geometry(self,geometry):
        self.win.geometry(geometry.text)

    def create_label(self,label,parent):
        tk.Label(parent,text=label.text.strip()).grid(get_grid_args(label))

    def create_button(self,button,parent):
        b = tk.Button(parent,text=button.text.strip())
        b.grid(get_grid_args(button))
        link = get_attribute(button,"link")
        if link:
            self.buttons[str(b)] = Button(**get_button_args(button))
            b.bind("<Button-1>",self.button_clicked)



    def create_frame(self,frame,parent):
        if get_attribute(frame,"scrolling",bool_from_str):
            self.create_scrollframe(frame,parent)
        else:
            tk_frame = tk.Frame(parent)
            self.buildBody(frame,tk_frame)
            tk_frame.grid(get_grid_args(frame))

    def create_listbox(self,listbox,parent): 
        if get_attribute(listbox,"scrolling",bool_from_str):
            self.create_scrollbox(listbox,parent)
        else :
            tk_listbox = tk.Listbox(parent,**get_listbox_args(listbox))
            self.buildList(listbox,tk_listbox)
            tk_listbox.grid(get_grid_args(listbox))
            
    def create_scrollframe(self,scrollframe,parent):
        outer_frame = tk.Frame(parent,relief=tk.GROOVE,bd=1)
        outer_frame.grid(get_grid_args(scrollframe))

        canvas = tk.Canvas(outer_frame,highlightthickness=0)
        inner_frame = tk.Frame(canvas)
        scrollbar = tk.Scrollbar(outer_frame,orient=tk.VERTICAL,command=canvas.yview)
        canvas['yscrollcommand']=scrollbar.set

        scrollbar.grid(row=0,column=1,sticky=tk.N+tk.S)
        canvas.grid(row=0,column=0,sticky=tk.W)
        canvas.create_window((0,0),window=inner_frame,anchor='nw')

        canvas.bind("<Configure>",lambda e: canvas.configure(scrollregion=canvas.bbox("all")))

        self.buildBody(scrollframe,inner_frame)

    def create_scrollbox(self,scrollbox,parent):
        frame = tk.Frame(parent)
        scrollbar = tk.Scrollbar(frame,orient=tk.VERTICAL)
        scrollbar.grid(row=0,column=1,sticky=tk.N+tk.S)
        listbox = tk.Listbox(frame,**get_listbox_args(scrollbox),yscrollcommand=scrollbar.set)
        listbox.grid(row=0,column=0,sticky=tk.N+tk.S+tk.E+tk.W)
        self.buildList(scrollbox,listbox)
        scrollbar['command'] = listbox.yview
        frame.grid(get_grid_args(scrollbox))


    def on_click(self,event):
        caller = event.widget
        print(caller)

    def button_clicked(self,event):
        button = self.buttons[str(event.widget)]
        BUTTON_TYPE_ACTIONS[button.btype](self,button)
        

    def back_button(self,button):
        self.win.destroy()

    def link_clicked(self,button):
        Window(get_xml(f"gui_pages/{button.link}"),master=self.win)

BUTTON_TYPE_ACTIONS = {
    "back":Window.back_button,
    "link":Window.link_clicked,
}

def main():
    Window(get_xml("gui_pages/main.html"),main=True)

if __name__ == '__main__':
    main()