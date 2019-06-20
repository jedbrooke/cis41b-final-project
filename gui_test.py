from gui_engine import Form, Window, TagUtility, Button

class TestButton(Button):
    def __init__(self, *args, **kwargs):
        super().__init__(*args,**kwargs)

    def print_hello(self):
        print("hello")
        
class TestForm(Form):
    def __init__(self,*args,**kwargs):
        super().__init__(*args,**kwargs)

    def submit(self):
        field = self.get_field("user_text")
        text = "Hello, " + field.data.get()
        choice = self.get_field("radio-choose")
        print([c[0].get() for c in choice.data])
        print([c[1] for c in choice.data])
        choices = [c[1] for c in choice.data if c[0].get() != 0]
        text += ". You chose: " + ",".join(choices)
        lb_choices = [self.get_field("listbox_test").data[1][i] for i in self.get_field("listbox_test").data[0].curselection()]
        print(lb_choices)
        text += " and " + ",".join(lb_choices)
        print(text) 
        label = self.get_field("display_user_text")
        label.data.set(text)

def main():
    Window(TagUtility.get_html("gui_pages/testing.html"),main=True,form=TestForm,button=TestButton)

if __name__ == '__main__':
    main()