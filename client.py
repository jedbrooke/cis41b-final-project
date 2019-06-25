"""
client.py
Written by Jasper Edbrooke
client.py has the Client class which handles the back end interactions of the client, including interactions with the database, and network to the server. 
client.py also houses all the implentations of the GUI Forms, Buttons, and Windows
"""
import socket
from gui_engine import Form, Window, TagUtility, Button, Field
import threading
import queue
import data
import tkinter as tk
import tkinter.filedialog as tkfd
import pickle
import matplotlib as mpl
mpl.use('TkAgg') # tell matplotlib to work with Tkinter
from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg
import matplotlib.pyplot as plt
from tkinter.ttk import Progressbar as Pbar
import os
import select

SERVER_ADDR = "127.0.0.1"
SERVER_PORT = 5551

class ResultsButton(Button):
    '''holds the functions for the buttons for the results.html page'''
    def __init__(self, *args, **kwargs):
        super().__init__(*args,**kwargs)
        
    def graph_results(self):
        '''opens the window that generates and displays the graph of common tags'''
        self.window.goto_link("graph_tags.html",category=self.window.category)

    def export_category(self):
        path = tkfd.askdirectory(parent=self.window.win)
        if path:
            Window.client.add_instruction("request_export",self.window.category,path)

class ServerButton(Button):
    """ServerButton holds the actions for the server menu buttons"""
    def __init__(self, *args, **kwargs):
        super().__init__(*args,**kwargs)

    def send_command(self,command):
        Window.client.add_instruction("send_command_to_server",command)
        self.window.goto_link("server_response.html")

class SearchForm(Form):
    """This form handles the user entered string and number to tell the database how many images to download"""
    def __init__(self,*args,**kwargs):
        super().__init__(*args,**kwargs)

    def submit(self):
        """gets the user inputs and passes it to the results window"""
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
            ## TODO: replace console log with tkmb
            print("invalid number, using default")
        print(settings)
        self.window.goto_link("results.html",category=category,settings=settings)

class ResultsForm(Form):
    """Results form handles the user selected images and updates the list accordingly"""
    def __init__(self,*args,**kwargs):
        super().__init__(*args,**kwargs)


    def submit(self):
        """submits user inputs to database in the form of a list of urls"""
        urls = [image[0][2] for image in self.window.image_data if image[1]]
        Window.client.add_instruction("send_reject_urls_to_db",urls)
        self.window.post()

class SettingsForm(Form):
    """Handles the search settings that the user can enter to refine their search criteria"""
    def __init__(self,*args,**kwargs):
        super().__init__(*args,**kwargs)

    def submit(self):
        """passes search settings to the client to pass back to the search window"""
        filter_nsfw = self.get_field("filter").data.get()
        blacklist = self.get_field("blacklist").data.get()
        print(filter_nsfw,blacklist)
        settings = {}
        settings["filter_nsfw"] = True if filter_nsfw == "on" else False
        settings["blacklist"] = [tag.strip() for tag in blacklist.split(",")]
        Window.client.data_queue.put(settings)
        self.window.win.destroy()

class ReviewForm(Form):
    """gets the category the user chose and passes it to the results window"""
    def __init__(self, *args, **kwargs):
        super().__init__(*args,**kwargs)

    def submit(self):
        category = self.window.categories[self.get_field("categories-list").data[0].curselection()[0]][0]
        self.window.goto_link("results.html",category=category)
        
class SettingsWindow(Window):
    """This window shows the user the settings they can change on the search parameters"""
    def __init__(self, *args, **kwargs):
        super().__init__(*args,**kwargs)

    def post(self):
        print("calling settings window post")
        self.form_type = SettingsForm
        self._initialize()
              
class SearchWindow(Window):
    """displays for the user search bar and serch options"""
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
    """This window shows the user the images in the category they have chosen, with the option to export the category, view the common tags, or to reject images in the category"""
    def __init__(self, *args, **kwargs):
        super().__init__(*args,**kwargs)
        self.image_size = 250
        self.windows = {
            "graph_tags.html":PlotWindow
        }

    def post(self,category=None,settings=None):
        """tells database to start downloading images, starts a progress bar while waiting"""
        if category:
            if settings:
                Window.client.add_instruction("send_query_to_db",category,settings)
            else:
                Window.client.add_instruction("get_images_from_category",category)
            self.button = ResultsButton
            self.form_type = ResultsForm
            self.category = category

        self.pbar = Pbar(self.win,mode='indeterminate')
        self.pbar.grid(padx=50, pady=50)
        self.pbar.start()

        t = threading.Thread(target=self.get_images, args=(category,settings))
        t.start()
        
    def get_images(self,category=None,settings=None):
        """gets the images from the database and puts them in a list to be replayed"""
        if category:
            self.image_data = []
            fetching = True
            while fetching:
                Window.client.add_instruction("get_image_from_generator",None)
                image = Window.client.data_queue.get()
                if not image:
                    fetching = False
                    continue
                self.image_data.append([image,False])
            initialize = True

        else:
            frame = self.get_frame_by_id("display")
            for child in frame.winfo_children():
                child.destroy()
            initialize = False

        
        self.win.after(10,lambda:self.generate_images(initialize))

    def generate_images(self,initialize=False):
        """displays the images from the category that the user has chosen"""
        if initialize:
            self._initialize()
        frame = self.get_frame_by_id("display")
        self.pbar.stop()
        self.pbar.destroy()
        columns = 3
        self.display_images = []
        self.boxes = {}

        grid_count = 0
        print("creating images")
        for i,image in enumerate(self.image_data):
            """image[1] is the is_rejected flag"""
            if image[1]:
                """if it's rejected we skip this image"""
                continue
            canvas = tk.Canvas(frame)
            """image[0] is the image, image[0][1] is the blob"""
            img = TagUtility.get_image(image[0][1],self.image_size,"blob")
            canvas.create_image(0,0,anchor=tk.N+tk.W,image=img)
            canvas.grid(row=grid_count//columns,column=grid_count%columns)
            canvas.bind("<Button-1>",self.image_selected)
            self.images.append(img)
            self.display_images.append(canvas)
            self.boxes[str(canvas)] = (i,grid_count)
            grid_count += 1

        frame.update()

    def image_selected(self,event):
        """callback for when an image is clicked, tells the list to reject it and draw a red X on the image to show the user"""
        img_index,grid_index = self.boxes[str(event.widget)]
        self.image_data[img_index][1] = True #set the remove flag to true
        self.display_images[grid_index].create_line(0,0,50,50,fill="red",width=5)
        self.display_images[grid_index].create_line(50,0,0,50,fill="red",width=5)
        self.display_images[grid_index].update()

class ReviewWindow(Window):
    """Shows user a list of available categories they can choose to reivew images in"""
    def __init__(self, *args, **kwargs):
        super().__init__(*args,**kwargs)

    def post(self):
        self.form_type = ReviewForm
        self.windows = {
            "results.html":ResultsWindow
        }
        self._initialize()
        tk_listbox = self.get_frame_by_id("categories-list")
        Window.client.add_instruction("get_categories",None)
        self.categories = Window.client.data_queue.get()
        tk_listbox.insert(tk.END,*self.categories)
        #add the list of categories to the list box
        self.form.add_field(Field("listbox","categories-list",[tk_listbox,self.categories]))

class PlotWindow(Window):
    """Shows the graph of common tags for the category"""
    def __init__(self, *args, **kwargs):
        super().__init__(*args,**kwargs)

    def post(self,category):
        """Inintializes the window and the plot graph"""
        self._initialize()
        print("post in PlotWindow")
        Window.client.add_instruction("get_tag_counts",category)
        data = Window.client.data_queue.get()
        data.sort(key=lambda val: val[1])
        frame = self.get_frame_by_id("plot")
        tags = [d[0] for d in data][-15:]
        counts = [d[1] for d in data][-15:]
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

class ServerWindow(Window):
    """Server window is a menu for the interactions with the server"""
    def __init__(self, *args, **kwargs):
        super().__init__(*args,**kwargs)

    def post(self):
        self.button = ServerButton
        self.windows = {
            "select.html":SelectWindow,
            "server_response.html":ServerResponseWindow,
        }
        self._initialize()

class ServerResponseWindow(Window):
    """Displays the server's response to the user in the gui"""
    def __init__(self, *args, **kwargs):
        super().__init__(*args,**kwargs)

    
    def post(self):
        print("initializing response window")
        self._initialize()
        threading.Thread(target=self.get_server_response).start()
        

    def get_server_response(self):
        print("waiting for data",Window.client.data_queue.empty()) 
        response = Window.client.data_queue.get()
        self.win.after(10,lambda:self.show_label(*response))


    responses = {
        "send_data":["There was an error processing the data","Data sent successfully",],
        "clear_db":["There was an error clearing the database","Database cleared successfully"],
        "check_if_trainable":["The Dataset you have selected is not trainable","The Dataset you have selected is trainable!"],
        "train":["The Dataset you have selected is not trainable","Training in progress. Please come back in a few hours."],
        "shut_down":["There are other clients on the server, server will not close","Server is shutting down"],
        "connection_lost":["Error: the connection to the server has been lost"]

    }

    def show_label(self,command,result,*args):
        tk.Label(self.get_frame_by_id("display"),text=ServerResponseWindow.responses[command][result]).grid()
        if len(args) is not 0:
            tk.Label(self.get_frame_by_id("display"),text=",".join(args)).grid()

class SelectWindow(Window):
    """Prompts the user to select the categories they want"""
    def __init__(self, *args, **kwargs):
        super().__init__(*args,**kwargs)

    def post(self,*args):
        self.form_type = SelectForm
        self.windows = {
            "server_response.html":ServerResponseWindow
        }
        self._initialize()
        tk_listbox = self.get_frame_by_id("categories-list")
        Window.client.add_instruction("get_categories",None)
        self.categories = Window.client.data_queue.get()
        tk_listbox.insert(tk.END,*self.categories)
        #add the list of categories to the list box
        self.form.add_field(Field("listbox","categories-list",[tk_listbox,self.categories]))

class SelectForm(Form):
    """gets the categories that the user selects and sends them to the server"""
    def __init__(self, *args, **kwargs):
        super().__init__(*args,**kwargs)



    def submit(self):
        choices_list = self.get_field("categories-list").data[1]
        self.categories = [choices_list[i][0] for i in self.get_field("categories-list").data[0].curselection()]
        urls = []
        tags = []
        #get all the image urls to send
        print("category is",self.categories)
        for category in self.categories:
            Window.client.add_instruction("get_images_from_category",category)
            fetching = True
            while fetching:
                Window.client.add_instruction("get_image_from_generator",None)
                image = Window.client.data_queue.get()
                if not image:
                    fetching = False
                    continue
                urls.append(image[2])
                tags.append(category)

        Window.client.add_instruction("send_command_to_server","send_data",(urls,tags))
        self.window.goto_link("server_response.html") 
        

class Client():
    def __init__(self):
        #initialize instruction dictionary for db_thread
        self.instructions = {
            "quit":self.quit,
            "initialize_db":self.initialize_db,
            "send_query_to_db":self.send_query_to_db,
            "get_image_from_generator":self.get_image_from_generator,
            "get_tag_counts":self.get_tag_counts,
            "request_export":self.request_export,
            "send_reject_urls_to_db":self.send_reject_urls_to_db,
            "get_categories":self.get_categories,
            "get_images_from_category":self.get_images_from_category,
            "send_command_to_server":self.send_command_to_server
        }

        #instructions queue will hold the request from the GUI and tell the db_thread to execute them
        self.instructions_queue = queue.Queue()
        self.instructions_queue.put(("initialize_db",(None,)))
        #data queue is to pass data between the client/db_thread and the gui thread
        self.data_queue = queue.Queue()
        self.is_running = True
        db_thread = threading.Thread(target=self.run)
        db_thread.start()
        
        #prepare the window types for the sub windows
        windows = {
            "search.html":SearchWindow,
            "review.html":ReviewWindow,
            "server.html":ServerWindow,
        }

        #set the static reference to the client so the gui knows about the client thread
        Window.set_client(self)
        try:
            self.socket = socket.socket()
            self.socket.connect((SERVER_ADDR,SERVER_PORT))
            self.socket.setblocking(0)
            self.server = True
        except ConnectionRefusedError as e:
            self.server = False
        #instantiate the new window
        start_page = "main.html" if self.server else "main_no_server.html"
        path = os.path.join("gui_pages",start_page)
        w = Window(TagUtility.get_html(path),main=True,windows=windows)
        
        #start the mainloop in the window, the main thread will be the gui thread from here
        w.start()


        print("quitting")
        #tell db_thread to stop
        self.instructions_queue.put(("quit",(None,)))
        #wait for it to stop
        db_thread.join()
        self.socket.close()

    def send_query_to_server(self,query,*args):
        self.socket.send(pickle.dumps((query,(*args))))

    def send_query_to_db(self,q,settings):
        print(q,settings)
        self.images = self.db.download_nimages_with_category(q,**settings)
        #images is a generator of the image blobs and some other info

    def send_reject_urls_to_db(self,urls):
        self.db.reject_images(urls)

    def request_export(self,category,directory):
        self.db.export_images(category,directory)

    def get_tag_counts(self,category=None):
        self.data_queue.put(self.db.get_count_of_tags(category))

    def get_categories(self,*args):
        self.data_queue.put(self.db.get_categories())

    def initialize_db(self,*args):
        self.db = data.SqlDb()

    def quit(self,*args):
        self.is_running = False

    def get_image_from_generator(self,*args):
        try:
            self.data_queue.put(next(self.images))
        except Exception as e:
            self.data_queue.put(False)
        
    def get_images_from_category(self,category):
        print(category)
        self.images = self.db.get_images_from_category(category)

    def run(self):
        while self.is_running:
            function,args = self.instructions_queue.get()
            self.instructions[function](*args)

    def add_instruction(self,instruction,*args):
        self.instructions_queue.put((instruction,(*args,)))

    #network functions:
    def send_command_to_server(self,command,data=None):
        if self.server:
            data_dict = {"command": command}

            if data is not None:
                data_dict["data"] = data

            self.socket.send(pickle.dumps(data_dict))

            #server returns a boolean based on success or fail
            print("waiting for response from server")
            #lines 472 - 474 borrowed from Stack Overflow https://stackoverflow.com/questions/2719017/how-to-set-timeout-on-pythons-socket-recv-method
            ready = select.select([self.socket],[],[],10)
            if ready[0]:
                response = pickle.loads(self.socket.recv(1024))
            else:
                response = (False,)
                command = "connection_lost"
            print("got response")
            if (command == "shut_down" and response) or not ready[0]:
                self.server = False
        else:
            response = (False,)
            command = "connection_lost"


        print(response)
        self.data_queue.put((command,*response))
    

if __name__ == '__main__':
    client = Client()
