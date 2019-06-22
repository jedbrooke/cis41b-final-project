from bs4 import BeautifulSoup as bs
import tkinter as tk
from tkinter import Canvas
from tkinter import messagebox as tkmb
from PIL import ImageTk,Image
import os
from io import BytesIO

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

    FRAME_ARGS = {
        "height":int,
        "width":int,
    }

    ELEMENT_ARGS = {
        "grid":GRID_ARGS,
        "listbox":LISTBOX_ARGS,
        "button":BUTTON_ARGS,
        "frame":FRAME_ARGS,
    }

    def __init__(self):
        pass

    @staticmethod
    def get_html(path):
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
        except ValueError as e:
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
    def get_frame_args(tag):
        return TagUtility.get_element_args(tag,"frame")

    @staticmethod
    def get_image(src,target_size=250,mode='path'):
        if mode == "path": 
            img_pil = Image.open(src)
        elif mode == 'blob':
            img_pil = Image.open(BytesIO(src))
        width,height = img_pil.size
        ratio = width/height
        width_new = target_size
        height_new = target_size/ratio
        img_pil = img_pil.resize((int(width_new), int(height_new)), Image.ANTIALIAS)
        return ImageTk.PhotoImage(img_pil)

class Button():
    def __init__(self, link=None, action=None, btype=None, title=None, window=None):
        self.link = link
        self.action = action
        self.btype = btype
        self.title = title
        self.window = window
        if link and not btype:
            self.btype = "link"
        elif action and not btype:
            self.btype = "action"

    #button actions
    @staticmethod
    def quit():
        print("press the red button to close the window")

class Form():
    def __init__(self,action=None,window=None):
        self.fields = {}
        self.window = window

    def add_field(self,field):
        self.fields[field.name] = field
        if field.ftype == "for_label":
            var = [f for f in self.fields if f.name == field.data[0]][0]
            field.data[1]["textvariable"] = var.data

    def add_to_multiple_select(self,field_name,data):
        sel = self.get_field(field_name)
        sel.data.append(data)

    def get_field(self,name):
        return self.fields[name]

    def print_all_fields(self):
        print(*self.fields)

class Field():
    def __init__(self, ftype, name, data):
        self.ftype = ftype
        self.name = name
        self.data = data
    def __str__(self):
        return str([self.ftype,self.name,self.data])

class Window():
    """docstring for Window"""
    client = None
    def __init__(self,soup=None,path=None,main=False,master=None,form=None,button=None,windows=None):
        self.HEAD_ACTIONS = {
            "title":self.set_title,
            "geometry":self.set_geometry
        }
        
        self.BODY_ACTIONS = {
            "button":self.create_button,
            "label":self.create_label,
            "div":self.create_frame,
            "scrollbox":lambda *args, **kwargs: self.create_listbox(scrolling=True,*args,**kwargs),
            "listbox":self.create_listbox,
            "img":self.create_image,
            "form":self.create_form,
            "input":self.create_input,
            "select":self.create_select,
            "option":self.create_option,
        }

        self.buttons = {}
        self.button = button if button else Button
        self.images = []
        self.form_type = form if form else Form
        self.frames = {}
        self.windows = windows
        self.isMain = main
        self.master = master


        if main:
            self.win = tk.Tk()
            self.win.protocol("WM_DELETE_WINDOW", self.shut_down)
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

        if main:
            self._initialize()

    def start(self):
        self.win.mainloop()
        print("mainloop over")

    def _initialize(self):
        self.form = self.form_type(window=self)
        self.buildElements()
        self.main_frame.grid()

    def _initPath(self,path):
            self.soup = TagUtility.get_html(path)

    def shut_down(self):
        print("quitting in window")
        self.win.quit()

    def post(self):
           self._initialize()   

    def buildElements(self):
        self.buildHead(self.soup.head)
        self.buildBody(self.soup.body,self.main_frame)

    def buildHead(self,soup):
        for tag in soup:
            if tag.name is not None:
                self.HEAD_ACTIONS[tag.name](tag)

    def buildBody(self,data,container,*args,**kwargs):
        elements = []
        for tag in data:
            if tag.name is not None:
                elements.append(self.BODY_ACTIONS[tag.name](tag,container,*args,**kwargs))
        return elements

    def buildList(self,elements,listbox):
        l = [item.text for item in elements.find_all("li")]
        listbox.insert(tk.END,*l)
        return l


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
        if len(button.find_all("img")) != 0:
            icon = TagUtility.get_image(src=button.find_all("img")[0]["src"],target_size=20)
            b = tk.Button(parent,image=icon,text=button.text.strip(),height=20,width=20)
            self.images.append(icon)
        else: 
            b = tk.Button(parent,text=button.text.strip())
        b.grid(TagUtility.get_grid_args(button))
        self.buttons[str(b)] = self.button(**TagUtility.get_button_args(button),window=self)
        b.bind("<Button-1>",self.button_clicked)
        return b

    def create_frame(self,frame,parent,*args,**kwargs):
        if TagUtility.get_attribute(frame,"scrolling",TagUtility.bool_from_str):
            return self.create_scrollframe(frame,parent,*args,**kwargs)
        else:

            tk_frame = tk.Frame(parent)
            elements = self.buildBody(frame,tk_frame,*args,**kwargs)
            tk_frame.grid(TagUtility.get_grid_args(frame))
            frame_id = TagUtility.get_attribute(frame,"id")
            if not frame_id:
                frame_id = str(tk_frame)
            self.frames[frame_id] = tk_frame
            return (tk_frame,elements)


    def create_form(self,form,parent):
        form_frame = tk.Frame(parent)
        elements = self.buildBody(form,form_frame)
        form_frame.grid(TagUtility.get_grid_args(form))
        frame_id = TagUtility.get_attribute(form,"id")
        if not frame_id:
            frame_id = str(form_frame)
        self.frames[frame_id] = form_frame
        return (form_frame,elements)


    def create_listbox(self,listbox,parent,scrolling=False):
        if TagUtility.get_attribute(listbox,"scrolling",TagUtility.bool_from_str)\
         or scrolling:
            frame = tk.Frame(parent)
            parent = frame
            scrolling = True

        tk_listbox = tk.Listbox(parent,**TagUtility.get_listbox_args(listbox))
        list_items = self.buildList(listbox,tk_listbox)

        list_id = TagUtility.get_attribute(listbox,"id")
        if not list_id:
            list_id = str(tk_listbox)
        self.frames[list_id] = tk_listbox

        if self.form:
            name = TagUtility.get_attribute(listbox,"name")
            self.form.add_field(Field("listbox",name,[tk_listbox,list_items]))

        if scrolling:
            scrollbar = tk.Scrollbar(frame,orient=tk.VERTICAL)
            scrollbar.grid(row=0,column=1,sticky=tk.N+tk.S)
            tk_listbox['yscrollcommand'] = scrollbar.set
            tk_listbox.grid(row=0,column=0,sticky=tk.N+tk.S+tk.E+tk.W)
            scrollbar['command'] = tk_listbox.yview
            frame.grid(TagUtility.get_grid_args(listbox))
            return frame
        else :
            tk_listbox.grid(TagUtility.get_grid_args(listbox))
            return tk_listbox

            
    def create_scrollframe(self,scrollframe,parent,*args,**kwargs):
        outer_frame = tk.Frame(parent,relief=tk.GROOVE,bd=1)
        outer_frame.grid(TagUtility.get_grid_args(scrollframe))

        canvas = tk.Canvas(outer_frame,highlightthickness=0)
        inner_frame = tk.Frame(canvas)
        scrollbar = tk.Scrollbar(outer_frame,orient=tk.VERTICAL,command=canvas.yview)
        canvas['yscrollcommand']=scrollbar.set

        scrollbar.grid(row=0,column=1,sticky=tk.N+tk.S)
        canvas.grid(row=0,column=0,sticky=tk.W)
        canvas.create_window((0,0),window=inner_frame,anchor='nw')


        canvas.bind("<Configure>",lambda e: canvas.configure(scrollregion=canvas.bbox("all"),**TagUtility.get_frame_args(scrollframe)))

        frame_id = TagUtility.get_attribute(scrollframe,"id")
        if not frame_id:
            frame_id = str(inner_frame)
        self.frames[frame_id] = inner_frame
        outer_frame_id = "outer-"+frame_id
        self.frames[outer_frame_id] = outer_frame
        canvas_id = frame_id+"-canvas"
        self.frames[canvas_id] = canvas

        return (outer_frame,self.buildBody(scrollframe,inner_frame,*args,**kwargs))

    # def create_scrollbox(self,scrollbox,parent,tk_listbox): REMOVED

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
        self.master.grab_set()
        self.master.focus_set()
        self.win.destroy()

    def link_clicked(self,button):
        self.goto_link(button.link)

    def goto_link(self,link,destroy=False,*args,**kwargs):
        path = f"gui_pages/{link}"
        print("link clicked:",link)
        if os.path.isfile(path):
            try:
                window = self.windows[link]
            except Exception as e:
                window = Window
            w = window(TagUtility.get_html(path),master=self.win)
            w.post(*args,**kwargs)

        else :
            tkmb.showerror(title="Page not Found", message=f"Error: \"{path}\" does not exist!")
        if destroy:
            self.win.destroy()

    def button_action(self,button):
        try:
            getattr(button,button.action)()
        except Exception as e:
            print(e)

    def create_input(self,input_tag,parent):
        return INPUT_TYPE_ACTIONS[TagUtility.get_attribute(input_tag,"type")](self,input_tag,parent)

    def create_text_input(self,input_tag,parent):
        var = tk.StringVar()
        default = TagUtility.get_attribute(input_tag,"default")
        if default:
            var.set(default)
        entry = tk.Entry(parent,textvariable=var)
        entry.grid(TagUtility.get_grid_args(input_tag))
        self.form.add_field(Field(str,TagUtility.get_attribute(input_tag,"name"),var))
        return entry

    def create_submit_input(self,input_tag,parent):
        button = tk.Button(parent, command=lambda : self.form.submit(), text="Submit")
        button.grid(TagUtility.get_grid_args(input_tag))
        return button

    def create_radio_input(self,input_tag,parent):
        pass

    def create_select(self,select,parent):
        multiple = TagUtility.get_attribute(select,"multiple",TagUtility.bool_from_str)
        name = TagUtility.get_attribute(select,"name")
        if multiple:
            self.form.add_field(Field("multiple_select",name,[]))
            self.create_frame(select,parent,multiple=True,name=name)
        else:
            tksv = tk.StringVar()
            tksv.set(select.find_all("option")[0]['value'])
            self.form.add_field(Field("select",name,tksv))
            self.create_frame(select,parent,variable=tksv,multiple=False)

    def create_option(self,option,parent,variable=None,multiple=False,name=None):
        value = TagUtility.get_attribute(option,"value")
        text = option.text.strip()
        if not value:
            value = text
        if multiple:
            tkiv = tk.IntVar()
            self.form.add_to_multiple_select(name,(tkiv,value))
            b = tk.Checkbutton(parent,text=text,variable=tkiv)

        else:
            b = tk.Radiobutton(parent,text=text,variable=variable,value=value)

        b.grid(TagUtility.get_grid_args(option))

        if len(option.find_all()) is 0:
            return b
        else :
            return (b,self.buildBody(option,parent))

    def get_frame_by_id(self,_id):
        return self.frames[_id]

    def post(self):
        self._initialize()

    @staticmethod
    def set_client(_client):
        Window.client = _client
       
BUTTON_TYPE_ACTIONS = {
    "back":Window.back_button,
    "link":Window.link_clicked,
    "action":Window.button_action,
}

INPUT_TYPE_ACTIONS = {
    "text":Window.create_text_input,
    "radio":Window.create_radio_input,
    "submit":Window.create_submit_input,
}