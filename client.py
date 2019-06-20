import socket
from gui_engine import Form, Window, TagUtility, Button
import threading
import queue
import time
import data
import tkinter as tk
import pickle
import matplotlib as mpl
mpl.use('TkAgg') # tell matplotlib to work with Tkinter
from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg
import matplotlib.pyplot as plt

SERVER_ADDR = "127.0.0.1"
SERVER_PORT = 5551

class MainButton(Button):
    def __init__(self, *args, **kwargs):
        super().__init__(*args,**kwargs)

    @staticmethod
    def print_hello():
        print("hello")

class ResultsButton(Button):
    def __init__(self, *args, **kwargs):
        super().__init__(*args,**kwargs)
        
    def graph_results(self):
        self.window.goto_link("graph_tags.html",category=self.window.category)

class SearchForm(Form):
    """docstring for Form"""
    def __init__(self,*args,**kwargs):
        super().__init__(*args,**kwargs)

    def submit(self):
        category = self.get_field("query").data.get()
        number = self.get_field("number").data.get()
        if not Window.client.data_queue.empty(): #if the queue is not empty, then grab the settings from there
            settings = Window.client.data_queue.get()
        else:
            settings = {}
        print(category,number)
        try:
            settings["n"] = int(number)
        except ValueError as e:
            print("invalid number, using default")
        print(settings)
        self.window.goto_link("results.html",category=category,settings=settings)


class ResultsForm(Form):
    def __init__(self,*args,**kwargs):
        super().__init__(*args,**kwargs)


    def submit(self):
        #send urls to database
        self.window.post()

class SettingsForm(Form):
    def __init__(self,*args,**kwargs):
        super().__init__(*args,**kwargs)

    def submit(self):
        filter_nsfw = self.get_field("filter").data.get()
        blacklist = self.get_field("blacklist").data.get()
        print(filter_nsfw,blacklist)
        settings = {}
        settings["filter_nsfw"] = True if filter_nsfw == "on" else False
        settings["blacklist"] = [tag.strip() for tag in blacklist.split(",")]
        Window.client.data_queue.put(settings)
        self.window.win.destroy()
        

class SettingsWindow(Window):
    def __init__(self, *args, **kwargs):
        super().__init__(*args,**kwargs)

    def post(self):
        print("calling settings window post")
        self.form_type = SettingsForm
        self._initialize()
              
class SearchWindow(Window):
    def __init__(self, *args, **kwargs):
        super().__init__(*args,**kwargs)

    def post(self):
        self.form_type = SearchForm
        self.windows = {
            "results.html" : ResultsWindow,
            "settings.html" : SettingsWindow
        }
        self._initialize()

class ResultsWindow(Window):

    def __init__(self, *args, **kwargs):
        super().__init__(*args,**kwargs)
        self.image_size = 250
        self.windows = {
            "graph_tags.html":PlotWindow
        }

    def post(self,category=None,settings=None):
        if category:
            Window.client.add_instruction("send_query_to_db",category,settings)
            self.button = ResultsButton
            self.form_type = ResultsForm
            self.category = category
            
        t = threading.Thread(target=self.get_images, args=(category,settings))
        t.start()
        
    def get_images(self,category=None,settings=None):
        if category:
            self.image_data = []
            timed_out = False
            for i in range(settings['n']):
                Window.client.add_instruction("get_image_from_generator",None)
                try:
                    self.image_data.append([Window.client.data_queue.get(timeout=20),False])
                except queue.Empty as e:
                    print("timed out")
                    print(e)
                    timed_out = True
                    break

            initialize = True


        else:
            frame = self.get_frame_by_id("display")
            for child in frame.winfo_children():
                child.destroy()
            initialize = False

        
        self.win.after(100,lambda: self.generate_images(initialize))

    def generate_images(self,init=False):
        if init:
            self._initialize()
        frame = self.get_frame_by_id("display")
        columns = 3
        self.display_images = []
        self.boxes = {}

        grid_count = 0
        print("creating images")
        for i,image in enumerate(self.image_data):
            if image[1]:
                continue
            canvas = tk.Canvas(frame)
            img = TagUtility.get_image(image[0][1],self.image_size,"blob")
            canvas.create_image(0,0,anchor=tk.N+tk.W,image=img)
            canvas.grid(row=grid_count//columns,column=grid_count%columns)
            canvas.bind("<Button-1>",self.image_selected)
            self.images.append(img)
            self.display_images.append(canvas)
            self.boxes[str(canvas)] = i
            grid_count += 1

        frame.update()

    def image_selected(self,event):
        index = self.boxes[str(event.widget)]
        self.image_data[index][1] = True #set the remove flag to true
        self.display_images[index].create_line(0,0,50,50,fill="red",width=5)
        self.display_images[index].create_line(50,0,0,50,fill="red",width=5)
        self.display_images[index].update()

class PlotWindow(Window):
    def __init__(self, *args, **kwargs):
        super().__init__(*args,**kwargs)

    def post(self,category):
        self._initialize()
        print("post in PlotWindow")
        Window.client.add_instruction("get_categories",category)
        data = Window.client.data_queue.get()
        data.sort(key=lambda val: val[1])
        frame = self.get_frame_by_id("plot")
        tags = [d[0] for d in data]
        counts = [d[1] for d in data]
        print(tags)
        print(counts)
        fig = plt.figure(figsize=(12,8))
        plt.barh(tags,counts,align="center")
        plt.yticks(wrap=True, fontsize=10, verticalalignment="center")
        plt.title(f"Common tags for {category}")
        plt.xlabel("tags")
        plt.ylabel("occurences")
        canvas = FigureCanvasTkAgg(fig,master=frame)
        canvas.get_tk_widget().grid()
        canvas.draw()
        frame.update()
        

class Client():
    def __init__(self):
        #self.socket = socket.socket()
        self.instructions = {
            "quit":self.quit,
            "initialize_db":self.initialize_db,
            "send_query_to_db":self.send_query_to_db,
            "get_image_from_generator":self.get_image_from_generator,
            "get_categories":self.get_categories,
        }
        self.instructions_queue = queue.Queue()
        self.instructions_queue.put(("initialize_db",(None,)))
        self.data_queue = queue.Queue()
        self.is_running = True
        db_thread = threading.Thread(target=self.run)
        db_thread.start()
        windows = {
            "search.html":SearchWindow
        }

        Window.set_client(self)
        w = Window(TagUtility.get_html("gui_pages/main.html"),main=True,windows=windows)
        w.start()

        print("quitting")
        self.instructions_queue.put(("quit",(None,)))
        db_thread.join()

        '''
        with self.socket:
             self.socket.connect((SERVER_ADDR,SERVER_PORT))
        '''

    def send_query_to_server(self,query,*args):
        self.socket.send(pickle.dumps((query,(*args))))

    def send_query_to_db(self,q,settings):
        #images = self.db.get_nimages_with_category()
        print("querying db")
        print(q,settings)
        self.images = self.db.download_nimages_with_category(q,**settings)
        #images is a list/generator of the image blobs
        #pass images ot gui
        pass

    def request_export(self,category):
        #self.db.export_images(category,directory)
        pass


    def recieve_images(self):
        self.socket.recv()
        return images

    def recieve_tags(category):
        self.socket.recv()
        return tags

    def send_train(category):
        self.socket.send()
        self.socket.recv()
        return data

    def get_categories(self,category=None):
        self.data_queue.put(self.db.get_count_of_tags(category))


    def generate_tag_count_graph(self,tag_counts):
        #plot the tags based on occurrence
        #tag_counts is tuple of list of tags and list of counts
        pass

    def initialize_db(self,*args):
        self.db = data.SqlDb()

    def quit(self,*args):
        self.is_running = False
        print("shutting down")

    def get_image_from_generator(self,*args):
        self.data_queue.put(next(self.images))
        pass

    def run(self):
        print("running" if self.is_running else "not running")
        while self.is_running:
            print("waiting for instructions")
            function,args = self.instructions_queue.get()
            print("running",function)
            self.instructions[function](*args)
        print("running finished")

    def add_instruction(self,instruction,*args):
        self.instructions_queue.put((instruction,(*args,)))
    

if __name__ == '__main__':
    client = Client()
