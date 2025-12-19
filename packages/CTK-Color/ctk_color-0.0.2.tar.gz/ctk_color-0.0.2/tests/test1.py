from CTK_Color import CTk_Color
import customtkinter as ctk

win=ctk.CTk()
text=ctk.CTkTextbox(win)
text.pack()
CTk_Color(text,"box","big","red").for_line()
win.mainloop()