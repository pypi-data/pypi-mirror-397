from CTK_Color import CTK_Color
import customtkinter as ctk

win=ctk.CTk()
text=ctk.CTkTextbox(win)
text.pack()
CTK_Color(text,"for","bal","red").for_word()
CTK_Color(text,"print","edit","orange").for_word()
CTK_Color(text,"while","gang","blue").for_word()
CTK_Color(text,"boxer","baler","green").for_word()
win.mainloop()