from bs4 import BeautifulSoup as bs
import tkinter as tk
from tkinter import Canvas
from PIL import ImageTk,Image 

def display_results(images):
    #for image in images:
    #generate html for the images, pass that to gui Window

    pass

def generate_tag_count_graph(tag_counts):
    #plot the tags based on occurrence
    #tag_counts is tuple of list of tags and list of counts
    pass

"""utility functions"""

class TagUtility():
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
    def __init__(self):
        pass

    @staticmethod
    def get_xml(path):
        file = open(path)
        soup = bs(file,"lxml")
        return soup

    @staticmethod
    def bool_from_str(s):
        return s.lower() == "true"

    @staticmethod
    def get_attribute(tag,attr,cast=str):
        try:
            return cast(tag[attr])
        except KeyError as e:
            return None

    @staticmethod
    def get_element_args(tag,element):
        return dict(\
            [(arg,TagUtility.get_attribute(tag,arg,kind))\
            for arg,kind in TagUtility.ELEMENT_ARGS[element].items()\
            if TagUtility.get_attribute(tag,arg,kind) is not None])

    @staticmethod
    def get_grid_args(tag):
        return TagUtility.get_element_args(tag,"grid")

    @staticmethod
    def get_listbox_args(tag):
        return TagUtility.get_element_args(tag,"listbox")

    @staticmethod
    def get_button_args(tag):
        return TagUtility.get_element_args(tag,"button")

    @staticmethod
    def get_image(src,target_size=250):
        img_pil = Image.open(src)
        width,height = img_pil.size
        ratio = width/height
        width_new = target_size
        height_new = target_size/ratio
        img_pil = img_pil.resize((int(width_new), int(height_new)), Image.ANTIALIAS)
        return ImageTk.PhotoImage(img_pil)

class Button():
    def __init__(self, link=None, action=None, btype=None, title=None):
        self.link = link
        self.action = action
        self.btype = btype
        self.title = title
        if link and not btype:
            self.btype = "link"
        elif action and not btype:
            self.btype = "action"

    #button actions
    @staticmethod
    def print_hello():
        print("hello")

class Form(tk.Frame):
    def __init__(self,parent=None,action=None,fields=[]):
        super().__init__(parent)
        self.action = action
        self.fields = fields

    def add_field(self,field):
        self.fields.append(field)
        if field.ftype == "for_label":
            var = [f for f in self.fields if f.name == field.data[0]][0]
            print(var.data)
            field.data[1]["textvariable"] = var.data

    def submit(self):
        try:
            getattr(self,self.action)()
        except Exception as e:
            self.print_all_fields()
            print(e)

    def print_all_fields(self):
        print(self.fields)

    #form submit functions
    def print_user_text(self):
        field = [field for field in self.fields if field.name == "user_text"][0]
        text = "Hello, " + field.data.get()
        print("Hello,",field.data.get())
        label = [field for field in self.fields if field.name == "display_user_text"][0]
        label.data.set(text)

class Field():
    def __init__(self, ftype, name, data):
        self.ftype = ftype
        self.name = name
        self.data = data


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
            "img":self.create_image,
            "form":self.create_form,
            "input":self.create_input,
        }

        self.buttons = {}
        self.images = []
        self.form = None

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
            self.soup = TagUtility.get_xml(path)   

    def buildElements(self):
        self.buildHead(self.soup.head)
        self.buildBody(self.soup.body,self.main_frame)

    def buildHead(self,soup):
        for tag in soup:
            if tag.name is not None:
                self.HEAD_ACTIONS[tag.name](tag)

    def buildBody(self,data,container):
        elements = []
        for tag in data:
            if tag.name is not None:
                elements.append(self.BODY_ACTIONS[tag.name](tag,container))
        return elements

    def buildList(self,elements,listbox):
        listbox.insert(tk.END,*[item.text for item in elements.find_all("li")])


    def set_title(self,title):
        self.win.title(title.text)

    def set_geometry(self,geometry):
        self.win.geometry(geometry.text)

    def create_label(self,label,parent):
        l = tk.Label(parent,text=label.text.strip())
        l.grid(TagUtility.get_grid_args(label))
        if TagUtility.get_attribute(label,"for"):
            name = TagUtility.get_attribute(label,"name")
            label_for = TagUtility.get_attribute(label,"for")
            self.form.add_field(Field("for_label",name,[label_for,l]))
        ltype = TagUtility.get_attribute(label,"type")
        if ltype and ltype == "display":
            name = TagUtility.get_attribute(label,"name")
            tksv =  tk.StringVar()
            l["textvariable"] = tksv
            self.form.add_field(Field("label",name,tksv))
        return l

    def create_button(self,button,parent):
        b = tk.Button(parent,text=button.text.strip())
        b.grid(TagUtility.get_grid_args(button))
        self.buttons[str(b)] = Button(**TagUtility.get_button_args(button))
        b.bind("<Button-1>",self.button_clicked)
        return b

    def create_frame(self,frame,parent):
        if TagUtility.get_attribute(frame,"scrolling",TagUtility.bool_from_str):
            return self.create_scrollframe(frame,parent)
        else:
            tk_frame = tk.Frame(parent)
            elements = self.buildBody(frame,tk_frame)
            tk_frame.grid(TagUtility.get_grid_args(frame))
            return (tk_frame,elements)


    def create_form(self,form,parent):
        self.form = Form(parent=parent,action=TagUtility.get_attribute(form,"action"))
        elements = self.buildBody(form,self.form)
        self.form.grid(TagUtility.get_grid_args(form))
        return (self.form,elements)


    def create_listbox(self,listbox,parent): 
        if TagUtility.get_attribute(listbox,"scrolling",TagUtility.bool_from_str):
            return self.create_scrollbox(listbox,parent)
        else :
            tk_listbox = tk.Listbox(parent,**TagUtility.get_listbox_args(listbox))
            self.buildList(listbox,tk_listbox)
            tk_listbox.grid(TagUtility.get_grid_args(listbox))
            return tk_listbox

            
    def create_scrollframe(self,scrollframe,parent):
        outer_frame = tk.Frame(parent,relief=tk.GROOVE,bd=1)
        outer_frame.grid(TagUtility.get_grid_args(scrollframe))

        canvas = tk.Canvas(outer_frame,highlightthickness=0)
        inner_frame = tk.Frame(canvas)
        scrollbar = tk.Scrollbar(outer_frame,orient=tk.VERTICAL,command=canvas.yview)
        canvas['yscrollcommand']=scrollbar.set

        scrollbar.grid(row=0,column=1,sticky=tk.N+tk.S)
        canvas.grid(row=0,column=0,sticky=tk.W)
        canvas.create_window((0,0),window=inner_frame,anchor='nw')

        canvas.bind("<Configure>",lambda e: canvas.configure(scrollregion=canvas.bbox("all")))

        return (outer_frame,self.buildBody(scrollframe,inner_frame))

    def create_scrollbox(self,scrollbox,parent):
        frame = tk.Frame(parent)
        scrollbar = tk.Scrollbar(frame,orient=tk.VERTICAL)
        scrollbar.grid(row=0,column=1,sticky=tk.N+tk.S)
        listbox = tk.Listbox(frame,**TagUtility.get_listbox_args(scrollbox),yscrollcommand=scrollbar.set)
        listbox.grid(row=0,column=0,sticky=tk.N+tk.S+tk.E+tk.W)
        self.buildList(scrollbox,listbox)
        scrollbar['command'] = listbox.yview
        frame.grid(TagUtility.get_grid_args(scrollbox))
        return frame

    def create_image(self,tag,parent):
        src = TagUtility.get_attribute(tag,"src")
        canvas = tk.Canvas(parent)
        canvas.grid()
        img = TagUtility.get_image(src,250)
        canvas.create_image(0,0,anchor=tk.N+tk.W, image=img)
        self.images.append(img)
        return canvas



    def on_click(self,event):
        caller = event.widget

    def button_clicked(self,event):
        button = self.buttons[str(event.widget)]
        BUTTON_TYPE_ACTIONS[button.btype](self,button)
        

    def back_button(self,button):
        self.win.destroy()

    def link_clicked(self,button):
        Window(TagUtility.get_xml(f"gui_pages/{button.link}"),master=self.win)

    def button_action(self,button):
        try:
            getattr(Button,button.action)()
        except Exception as e:
            print(e)

    def create_input(self,input_tag,parent):
        return INPUT_TYPE_ACTIONS[TagUtility.get_attribute(input_tag,"type")](self,input_tag,parent)

    def create_text_input(self,input_tag,parent):
        var = tk.StringVar()
        entry = tk.Entry(parent,textvariable=var)
        entry.grid()
        self.form.add_field(Field(str,TagUtility.get_attribute(input_tag,"name"),var))
        return entry

    def create_submit_input(self,input_tag,parent):
        button = tk.Button(parent, command=lambda : self.form.submit(), text="Submit")
        button.grid(TagUtility.get_grid_args(input_tag))
        return button


BUTTON_TYPE_ACTIONS = {
    "back":Window.back_button,
    "link":Window.link_clicked,
    "action":Window.button_action,
}

INPUT_TYPE_ACTIONS = {
    "text":Window.create_text_input,
    "submit":Window.create_submit_input,
}

def main():
    Window(TagUtility.get_xml("gui_pages/main.html"),main=True)

if __name__ == '__main__':
    main()