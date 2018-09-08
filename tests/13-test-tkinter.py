from PIL import ImageTk, Image
from tkinter import Tk, Label, Frame

root = Tk()

history = []


def keyup(e):
    print(e.keycode)
    if e.keycode in history:
        history.pop(history.index(e.keycode))


def keydown(e):
    if not e.keycode in history:
        history.append(e.keycode)


frame = Frame(root, width=1, height=1)
frame.bind("<KeyPress>", keydown)
frame.bind("<KeyRelease>", keyup)
frame.pack()

path = "testimg.jpg"

# Creates a Tkinter-compatible photo image, which can be used everywhere Tkinter expects an image object.
img = ImageTk.PhotoImage(Image.open(path))
panel = Label(root, image=img)

# The Pack geometry manager packs widgets in rows or columns.
panel.pack(side="bottom", fill="both", expand="yes")

frame.focus_set()
root.mainloop()
