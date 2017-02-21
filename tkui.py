import logging
import traceback
import Tkinter as tk
from uielem import uidict, UI, bindlist
from ScrolledText import ScrolledText as TkScrolledText
import tkMessageBox, tkFont
import ttk
from undoable import observed_list, observed_dict, observed_tree, UndoLog
import time
import os

class Entry(tk.Entry, object):
    def __init__(self, *args, **kwargs):
        text = kwargs.pop("defaulttext", "")
        self.autosize = kwargs.pop("autosize", False)
        tk.Entry.__init__(self, *args, **kwargs)
        self.text = text
        #self.bind('<Alt-e>', terp.sendexec)
        self.bind('<Control-a>', self.select_all)

    def select_all(self, event):
        self.selection_range(0, 'end')
        return "break"

    def get_text(self):
        return self.get()

    def set_text(self, text=""):
        self.delete(0, tk.END)
        self.insert(tk.END, text)
        if self.autosize:
            self["width"] = len(text)

    text = property(get_text, set_text)

class ScrolledText(TkScrolledText, object):
    def __init__(self, *args, **kwargs):
        text = kwargs.pop("defaulttext", "")
        self.autosize = kwargs.pop("autosize", False)
        TkScrolledText.__init__(self, *args, **kwargs)
        self.text = text
        self.bind('<Control-a>', self.select_all)

    def select_all(self, event):
        event.widget.tag_add("sel", "1.0", "end")
        return "break"

    def get_text(self):
        return self.get(1.0, 'end')

    def set_text(self, text=""):
        self.delete(1.0, "end")
        self.insert("end", text)
        if self.autosize:
            self["width"] = len(text)

    text = property(get_text, set_text)

class BoxedBool(tk.Checkbutton, object):
    def __init__(self, *args, **kwargs):
        self.var = kwargs["variable"] = tk.IntVar()
        self.var.set(kwargs.pop("value", 0))
        self.var.trace("w", self.callback)
        self.callbacks = []
        tk.Checkbutton.__init__(self, *args, **kwargs)

    def callback(self, name, index, op):
        logging.debug("Bool callback %s %s %s", name, op, self.value)
        for callback in self.callbacks:
            callback(name, op, self.value)

    def get_value(self):
        return bool(self.var.get())

    def set_value(self, value):
        self.var.set(value)
        if self.value:
            self.select()
        else:
            self.deselect()

    value = property(get_value, set_value)

class BoxedList(tk.Listbox):
    def __init__(self, *args, **kwargs):
        logging.debug("Creating BoxedList with %s %s", args, kwargs)
        self._list = kwargs.pop("_list", observed_list())
        self._list.callbacks.append(self.callback)
        tk.Listbox.__init__(self, *args, **kwargs)
        self.redraw()

    def reset(self, newlist):
        self._list.callbacks.remove(self.callback)
        self._list = newlist
        self._list.callbacks.append(self.callback)
        self.redraw()

    def callback(self, _list, event, *args):
        if event == "append":
            value, = args
            self.insert(tk.END, value)
        elif event == "pop":
            index, = args
            if index == -1:
                index = len(self._list)
            self.delete(index)
        elif event == "replace":
            self.redraw()
        elif event == "extend":
            self.redraw()
        elif event == "__setitem__":
            index, value = args
            if index < 0:
                index = len(_list) + index
            self.delete(index)
            self.insert(index, _list[index])
            self.see(index)

    def redraw(self):
        self.delete(0, tk.END)
        for item in self._list:
            self.insert(tk.END, item)

    def append(self, item):
        self.insert(tk.END, item)

    def lselection(self):
        return [self._list[int(index)] for index in self.curselection()]

class BoxedDict(tk.Frame):
    def __init__(self, *args, **kwargs):
        logging.debug("Creating BoxedDict with %s %s", args, kwargs)
        self._dict = kwargs.pop("_dict", observed_dict())
        self._dict.callbacks.append(self.callback)
        self.width = kwargs.pop("ewidth", 5)
        tk.Frame.__init__(self, *args, **kwargs)
        self.entries = {}

    def reset(self, newdict):
        self._dict.callbacks.remove(self.callback)
        self._dict = newdict
        self._dict.callbacks.append(self.callback)
        self.redraw()

    def addkeys(self, widget, entrytype, key):
        for k in ['<Return>', '<Up>', '<Down>']:
            widget.bind(k, lambda e, key=key: self.keypress(e, entrytype, key))

    def keypress(self, event, entrytype, key):
        logging.debug("Pressed %s: %s" % (entrytype, key))
        if event.keysym == "Return":
            newkey = self.entries[key][0].elem.text
            logging.debug("New key %s", newkey)
            if newkey != key:
                value = self.entries[key][1].elem.text
                if key != "":
                    del self._dict[key]
                if newkey != "":
                    self._dict[newkey] = value
                    self.entries[newkey][0].elem.focus()
                if key == "" and newkey != "":
                    self.entries[key][0].elem.text = ""
                    self.entries[key][1].elem.text = ""
                    self.entries[key][0].elem.lift()
                    self.entries[key][1].elem.lift()
            elif entrytype == "value":
                self._dict[key] = self.entries[key][1].elem.text
        elif event.keysym == "Down":
            newwidget = event.widget.tk_focusNext().tk_focusNext()
            if newwidget in [s for w in self.pack_slaves() for s in w.pack_slaves()]:
                newwidget.focus()
        elif event.keysym == "Up":
            newwidget = event.widget.tk_focusPrev().tk_focusPrev()
            if newwidget in [s for w in self.pack_slaves() for s in w.pack_slaves()]:
                newwidget.focus()

    def callback(self, _dict, event, *args):
        logging.debug("Event %s", event)
        if event == "__setitem__":
            key, value = args
            # TODO: Bad! Fix using undocallback?
            if key not in self.entries:
                logging.debug("Adding to row %s", len(self._dict))
                self.addentry(key, value, len(self.ui) - 1)
            else:
                self.entries[key][1].elem.text = self._dict[key]
        elif event == "pop" or event == "__delitem__":
            key = args[0]
            self.ui.remove(self.entries[key])
            self.entries[key].elem.destroy()
            del self.entries[key]
        elif event == "clear":
            for entry in self.entries.values():
                self.ui.remove(entry)
            self.entries.clear()
        elif event == "replace":
            self.redraw()

    def addentry(self, key, value, index="end"):
        frame = UI(tk.Frame, packside=tk.LEFT, children=[
            UI(Entry, width=self.width, defaulttext=key),
            UI(Entry, width=self.width, defaulttext=value)])
        self.ui.add(frame, index)
        self.entries[key] = frame
        self.addkeys(frame[0].elem, "key", key)
        self.addkeys(frame[1].elem, "value", key)

    def redraw(self):
        for child in self.pack_slaves():
            child.destroy()
        self.key_entries = {}
        self.value_entries = {}
        for i, key in enumerate(sorted(self._dict.keys())):
            self.addentry(key, uneval(self._dict[key]))
        self.addentry("", "")
        self.ui.repack()

class TkTerp:
    def __init__(self, histfile=None, globs=None):
        self.histfile = histfile
        if histfile and os.path.isfile(histfile):
            self.history = observed_list(open(histfile).read().splitlines())
        else:
            self.history = observed_list()
        self.histindex = len(self.history)
        self.globs = globs if globs is not None else {}
        self.history.append("")

    def sendexec(self, event):
        command = event.widget.text
        print ">>> %s" % command
        globs = self.globs if self.globs else globals()
        try:
            co = compile(command, "<ui>", "single")
            exec co in globs
        except:
            traceback.print_exc()
        if len(self.history) > 1 and command == self.history[-2]:
            self.history[-1] = ""
            self.histindex = len(self.history) - 1
        else:
            self.history[-1] = command
            self.histindex = len(self.history)
            self.history.append("")
        event.widget.text = ""

    def hist(self, event):
        if event.keysym == "Up":
            if self.histindex == len(self.history) - 1:
                self.history[-1] = event.widget.text
            self.histindex = max(0, self.histindex - 1)
        elif event.keysym == "Down":
            self.histindex = min(len(self.history) - 1, self.histindex + 1)
        event.widget.text = self.history[self.histindex]

    def save(self):
        if self.histfile:
            open(self.histfile, "w").write("\n".join(self.history[:-1]))

    def bind_keys(self, elem):
        elem.bind('<Return>', self.sendexec)
        elem.bind('<KP_Enter>', self.sendexec)
        elem.bind('<Up>', self.hist)
        elem.bind('<Down>', self.hist)

class BoxedTree(ttk.Treeview):
    def __init__(self, *args, **kwargs):
        logging.debug("Creating BoxedTree with %s %s", args, kwargs)
        self._tree = kwargs.pop("_tree", observed_tree())
        self._tree.undocallbacks.append(self.callback)
        ttk.Treeview.__init__(self, *args, **kwargs)
        self.redraw()

    def reset(self, newtree):
        self._tree.undocallbacks.remove(self.callback)
        self._tree = newtree
        self._tree.undocallbacks.append(self.callback)
        self.redraw()

    def callback(self, _tree, undo, redo):
        event, args = redo[0], redo[1:]
        logging.debug("** BoxedTree callback %s %s %s", event, _tree, args)
        if event == "remove":
            child, = args
            logging.debug("treeindex %s", _tree.treeindex)
            #if hasattr(child, "treeindex"):
            #    print child.treeindex
            # Not sure why it stopped working or why this works now!
            if hasattr(child, "treeindex"):
                self.detach(child.treeindex)
        elif event == "pop":
            index, = args
            oldvalue = undo[1]
            # TODO: Fix (should maybe call remove but then needs to not remove twice from list). This is the old fixed point problem.
            if hasattr(oldvalue, "elem"):
                oldvalue.elem.pack_forget()
            self.detach(oldvalue.treeindex)
            del self.widget[oldvalue.treeindex]
            oldvalue.treeindex = None
            #_tree.remove(oldvalue)
            #self.detach(_tree.children[index].treeindex)
        elif event == "reparent":
            newparent, = args
            # Hack TODO: Fix.
            if hasattr(_tree, "treeindex") and _tree.treeindex != None:
                self.reattach(_tree.treeindex, newparent.treeindex, "end")
            else:
                self.addtreeelem(_tree, parent=newparent.treeindex)
        elif event == "insert":
            index, child = args
            #print child.treeindex, _tree.treeindex, index
            # Hack TODO: Fix.
            if hasattr(child, "treeindex") and child.treeindex != None:
                self.reattach(child.treeindex, _tree.treeindex, index)
            else:
                self.addtreeelem(child, parent=_tree.treeindex, index=index)
        elif event == "append":
            child, = args
            index = len(child.parent)
            if hasattr(child, "treeindex") and child.treeindex != None:
                self.reattach(child.treeindex, _tree.treeindex, index)
            else:
                self.addtreeelem(child, parent=_tree.treeindex, index=index)

    def redraw(self):
        map(self.delete, self.get_children())
        self.widget = {}
        self.addtreeelem(self._tree)

    def addtreeelem(self, elem, parent="", index="end"):
        index = self.insert(parent, index, text=str(elem), open=True)
        self.widget[index] = elem
        elem.treeindex = index
        for subelem in elem:
            self.addtreeelem(subelem, index)

    def selectiondict(self):
        return {index: self.widget[index] for index in self.selection()}

    def wselection(self):
        return [self.widget[index] for index in self.selection()]

    def selection_set(self, *args, **kwargs):
        return ttk.Treeview.selection_set(self, *args, **kwargs)

    def selection_set_by_items(self, wrappers):
        keys = [k for k, v in self.widget.items() if v in wrappers]
        if keys:
            self.selection_set(keys[0])
            for key in keys[1:]:
                self.selection_add(key)
        #return self.selection_set(keys)

class UITree:
    def __init__(self, root, tree):
        self.root = root
        self.tree = tree
        self.indexof = {}

    def addwidget(self, location="sibling", kwargs=None, *args):
        if kwargs is None:
            kwargs = {}
        widget = self.tree.wselection()[0]
        uiname = uidict["uilist"]._list[int(uidict["uilist"].curselection()[0])]
        logging.debug("Adding %s %s %s %s %s", widget, kwargs, uiname, eval(uiname), uidict["child params"].text.split(","))
        # Need to think of something safer than eval.
        if location == "child":
            newelem = UI(eval(uiname), **kwargs)
            widget.add(newelem, 0)
        elif widget.parent != self.tree._tree:
            newelem = UI(eval(uiname), **kwargs)
            newindex = widget.parent.index(widget) + 1
            widget.parent.add(newelem, newindex)
        else:
            # Make sure to have a name to retrieve this one!
            logging.debug("Adding new toplevel")
            newelem = UI(eval(uiname), **kwargs)
            fakeroot.append(newelem)
            newelem.makeelem()
            newelem.elem.bind("<Button-3>", click)
            newelem.elem.bind("<B3-Motion>", drag)

    def delwidget(self, *args):
        widget = self.tree.wselection()[0]
        widget.parent.remove(widget)

    def move_by(self, diff, *args):
        widget = self.tree.wselection()[0]
        logging.debug("Moving %s by %s" % (widget, diff))
        newindex = widget.parent.move_by(widget, diff)

    def reparent(self, direction, *args):
        widget = self.tree.wselection()[0]
        logging.debug("reparenting %s", widget)
        if direction == "left":
            newparent = widget.parent.parent
            newindex = newparent.index(widget.parent) + 1
        elif direction == "right":
            parent = widget.parent
            newparent = sibling = parent[parent.index(widget) - 1]
            newindex = len(widget.parent)
        widget.setparent(newparent, newindex)
        recursive_lift(widget)

def gencode(root=None, filename="generated_tree.py", prefix="uiroot = "):
    if root is None:
        root = uiroot
    code = "%s%s" % (prefix, root.code(len(prefix)).strip())
    open(filename, "w").write(code)

def uneval(v):
    if type(v) in [int, float, str]:
        return repr(v)
    elif hasattr(v, "__call__"):
        return v.__name__
    else:
        return "%s()" % v.__class__.__name__

def update_param(event, _dict, *args):
    logging.debug("update %s %s %s", event, _dict, args)
    if event == "set":
        key, oldvalue = args
        widget = uidict["tree"].wselection()[0]
        widget.update(key, eval(_dict[key]))
    elif event == "create":
        key, value, oldvalue = args
        widget = uidict["tree"].wselection()[0]
        widget.update(key, eval(_dict[key]))

def select_callback(event):
    selection = event.widget.wselection()
    if uidict["autoparam"].value and selection:
        widget = selection[0]
        uidict["params"]._dict.replace(widget.kwargs)

def selection():
    return uidict["tree"].wselection()

def recursive_lift(widget):
    if widget.elemtype.__name__ == "Canvas":
        tk.Misc.lift(widget.elem)
    else:
        widget.elem.lift()
    for child in widget:
        recursive_lift(child)

def click(event):
    global startdragtime
    widget = event.widget
    logging.debug("clicked at %s %s on top of %s", event.x, event.y, widget)
    logging.debug("%s %s", type(widget), widget.__class__)
    key = [k for k, v in uidict["tree"].widget.items() if v.elem == widget][0]
    uidict["tree"].selection_set(key)
    #recursive_lift(widget.ui)
    startdragtime = time.time()
    return "break"

startdragtime = 0
dragdelay = 0.5

def xy(event, widget=None):
    if widget == None:
        widget = event.widget
    x = event.x_root - widget.ui.toplevel.winfo_rootx()
    y = event.y_root - widget.ui.toplevel.winfo_rooty()
    return (x, y)

def drag(event):
    if time.time() - startdragtime > dragdelay:
        widget = uidict["tree"].wselection()[0]
        #widget.elem.pack_forget()
        x, y = xy(event, widget.elem)
        recursive_lift(widget)
        widget.elem.place(x=x, y=y)

def mark(event):
    x, y = xy(event)
    logging.debug("mark %s %s", x, y)
    marker = UI(Entry, defaulttext = str(len(uidict["markers"].ui)),
                bg="blue", fg="white", autosize=True)
    uidict["markers"].ui.add(marker)
    marker.elem.place(x=x, y=y)

def simplify(selection):
    if type(selection) == dict:
        selection = selection.values()
    if len(selection) == 1:
        return selection[0]
    return selection

def markereval(marker):
    xy = (marker.winfo_rootx(), marker.winfo_rooty())
    marker.lower()
    widget = marker.winfo_containing(*xy)
    marker.lift()
    if widget is None:
        return None
    if isinstance(widget, BoxedList):
        return simplify(widget.lselection())
    elif isinstance(widget, Entry):
        # Should this be evaluated?
        return entry.text
    elif isinstance(widget, BoxedTree):
        return simplify(widget.wselection())

def markerargs():
    kwargs = {}
    for marker in uidict["markers"].ui:
        kwargs[marker.elem.text] = markereval(marker.elem)
    numkeys = [int(key) for key in kwargs if key.isdigit()]
    args = [None for i in xrange(max(numkeys + [-1]) + 1)]
    for key in numkeys:
        args[key] = kwargs.pop(str(key))
    return args, kwargs

def marker_info(event):
    x = event.x_root - event.widget.ui.toplevel.winfo_rootx()
    y = event.y_root - event.widget.ui.toplevel.winfo_rooty()
    marker = uidict["markers"].ui[0].elem
    xy = (marker.winfo_rootx() - marker.ui.toplevel.winfo_rootx(),
          marker.winfo_rooty() - marker.ui.toplevel.winfo_rooty())
    widget = marker.winfo_containing(*xy)
    logging.debug("marker info: %s", (marker.winfo_geometry(), marker.winfo_ismapped(), marker.winfo_manager()))

def setfonts():
    for fontname in tkFont.names():
        default_font = tkFont.nametofont(fontname)
        default_font.configure(size=14)

# Get all widgets from Tkinter
tkuilist = ["tk.%s" % e for e in dir(tk) if e.capitalize() == e and
            len(e) > 2 and not e.startswith("_")]
tkuilist += ["Entry", "BoxedBool", "BoxedList", "BoxedDict", "BoxedTree"]
tkuilist = observed_list(tkuilist)

if __name__ == "__main__":
    #logging.basicConfig(level=logging.DEBUG)

    from Tkinter import Tk, Label, Frame, Button, Canvas
    histfile = "tkui_history"
    terp = TkTerp(histfile)

    def quit():
        logging.info("Shutting down...")
        terp.save()
        uidict["root"].destroy()

    execfile("functions.py")
    execfile("generated_tree.py")
    uiroot.makeelem()

    uidict["uilist"].reset(tkuilist)
    paramdict = observed_dict({"test": 3, "foo": "bar"})
    uidict["params"].reset(paramdict)
    uidict["bind"].reset(bindlist)
    uidict["history"].reset(terp.history)

    fakeroot = observed_tree()
    fakeroot.append(uiroot)
    fakeroot.elem = None
    uidict["tree"].reset(fakeroot)
    #uidict["tree"].reset(uiroot)
    tree = uidict["tree"]
    style = ttk.Style(uidict["root"])
    style.configure('Treeview', rowheight=14*2)
    tree.column("#0", minwidth=0, width=800)
    uitree = UITree(uiroot, tree)
    uidict["tree"].bind('<<TreeviewSelect>>', select_callback)
    uidict["params"]._dict.callbacks.append(update_param)

    for marker in uidict["markers"].ui:
        marker.elem.place_forget()

    undolog = UndoLog()
    undolog.add(uiroot)
    uidict["undolist"].reset(undolog.root)

    setfonts()

    terp.bind_keys(uidict['exec'])
    uidict["root"].protocol("WM_DELETE_WINDOW", quit)
    uidict["root"].bind("<Button-3>", click)
    uidict["root"].bind("<B3-Motion>", drag)
    uidict['root'].bind('<Control-q>', mark)
    uidict["root"].bind("<Shift-Button-3>", startrect)
    uidict["root"].bind("<Shift-B3-Motion>", moverect)
    uidict["root"].bind("<Shift-ButtonRelease-3>", endrect)
    #uidict["root"].bind("<Control-ButtonRelease-1>", releasecb)
    #print "BINDINGS", uidict["root"].event_info('<<undo>>')
    #Cannot get list of bound events, have to track them ourselves.
    #uiroot[1][1][1].elem.config(command = lambda e: None)
    uidict["root"].mainloop()
