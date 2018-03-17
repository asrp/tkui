def addwidget(*args):
    uitree.addwidget(*args, kwargs=eval(uidict["child params"].text or "{}"))

def addchild(*args):
    uitree.addwidget(location="child", *args)

def delwidget(*args):
    uitree.delwidget(*args)

def move_up(*args):
    undolog.start_group("move")
    uitree.move_by(-1, *args)
    undolog.end_group("move")

def move_down(*args):
    undolog.start_group("move")
    uitree.move_by(1, *args)
    undolog.end_group("move")

def move_left(*args):
    undolog.start_group("move")
    uitree.reparent("left", *args)
    undolog.end_group("move")

def move_right(*args):
    undolog.start_group("move")
    uitree.reparent("right", *args)
    undolog.end_group("move")

def undo(*args):
    undolog.undo()

def redo(*args):
    undolog.redo()

def reload():
    execfile(os.path.join(os.path.dirname(__file__), "functions.py"), globals())

def printmarker():
    args, kwargs = markerargs()
    kwargstr = ["%s = %s" % (k, v) for k, v in kwargs.items()]
    print "f(%s)" % ", ".join(map(str, args + kwargstr))

def startrect(event):
    global startxy
    x, y = xy(event)
    startxy = x, y
    uidict["rectangle"].place(x=x, y=y, anchor="nw")
    tk.Misc.lift(uidict["rectangle"])
    uidict["rectangle"]["width"] = 0
    uidict["rectangle"]["height"] = 0

def moverect(event):
    x, y = xy(event)
    uidict["rectangle"]["width"] = x - startxy[0]
    uidict["rectangle"]["height"] = y - startxy[1]

def box(widget):
    return (widget.winfo_x(), widget.winfo_y(),
            widget.winfo_width(), widget.winfo_height())

def contains(box1, box2):
    x1, y1, w1, h1 = box1
    x2, y2, w2, h2 = box2
    return x1 <= x2 <= x2 + w2 <= x1 + w1 and y1 <= y2 <= y2 + h2 <= y1 + h1

def endrect(event):
    tk.Misc.lower(uidict["rectangle"])
    uidict["tree"].selection_set_by_items(rectselection())

def rectselection():
    rbox = box(uidict["rectangle"])
    toplevel = uidict["rectangle"].ui.toplevel.ui
    def condition(widget):
        return contains(rbox, box(widget.elem))
    return [elem for elem in toplevel.tops(condition) if not elem == uidict["rectangle"].ui]
