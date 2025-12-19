import customtkinter as ctk
import tkinter as tk

class CTK_Color():
    def __init__(self,text_box,text,tag,color,end="none"):
        self.text_box=text_box
        self.text=text
        self.tag=tag
        self.color=color
        self.end=end

    def for_word(self):
        self.text_box.bind("<KeyPress>",lambda event:self.coloring_word(event))

    def coloring_word(self,event):
        start_index="1.0"
        while True:
            start_index=self.text_box.search(self.text,start_index,self.text_box.index(tk.INSERT))
            if not start_index:
                break
            ending_index=f"{start_index}+{len(self.text)}c"
            self.text_box.tag_add(self.tag, start_index, ending_index)
            start_index = ending_index
            self.text_box.tag_config(self.tag, foreground=self.color)

    def for_line(self):
        self.text_box.bind("<KeyPress>",lambda event:self.coloring_line(event))

    def coloring_line(self,event):
        start_index="1.0"
        while True:
            start_index=self.text_box.search(self.text,start_index,self.text_box.index(tk.INSERT))
            if not start_index:
                break
            if self.end=="none":
                start=start_index.split(".")[0]
                ending_index=f"{start}.end"
            else:
                ending_index=self.text_box.search(self.end,start_index,self.text_box.index(tk.INSERT))
            self.text_box.tag_add(self.tag, start_index, ending_index)
            start_index = ending_index
            self.text_box.tag_config(self.tag, foreground=self.color)
