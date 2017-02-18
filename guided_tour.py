import Tkinter as tk
from Tkinter import Tk, Frame, Button
import tkMessageBox, tkFont
import tkui
from tkui import Entry, BoxedList, BoxedTree, BoxedBool, ScrolledText, gencode
from uielem import uidict, UI, bindlist
from undoable import observed_list, observed_tree
import ttk
import re
import sys
import os
import logging

class TkGuide:
    def __init__(self, terp):
        self.step_index = 0
        self.hint_index = 0
        self.executed = set()
        self.terp = terp

    def start_step(self):
        uidict["guide"].delete(1.0, "end")
        # Hack! Should be elsewhere
        if self.step_index == 0:
            self.image = tk.PhotoImage(file=os.path.join("docs", "platypus_logo.png")).subsample(2)
            uidict["guide"].image_create('end', image=self.image)
            uidict["guide"].insert('end', "\n")
        add_tagged(uidict["guide"], limited_markdown(self.step.message.strip()))
        self.hint_index = 0
        if self.hint_index < len(self.step.hint):
            uidict["hint terp"].text = self.step.hint[self.hint_index]

    @property
    def step(self):
        return steps[self.step_index]

    def next_hint(self, event):
        self.hint_index += 1
        self.terp.sendexec(event)
        if self.hint_index < len(self.step.hint):
            uidict["hint terp"].text = self.step.hint[self.hint_index]

    def tree_change(self, widget, event, *args, **kwargs):
        # Hack! Should be elsewhere
        logging.info("Tree change", widget, event, args, kwargs)
        if self.step.condition == "uilist":
            if event in ["append", "insert"] and args[-1] == uilist:
                uiroot.elem.after(50, self.next)
        elif self.step.condition == "history":
            if event in ["insert", "append"] and args[-1].kwargs.get("name") == "history":
                uiroot.elem.after(50, self.next)

    def next(self):
        if self.step.post and self.step_index not in self.executed:
            self.step.post(uiroot)
            self.executed.add(self.step_index)
        self.step_index += 1
        self.start_step()

    def prev(self):
        self.step_index = max(0, self.step_index - 1)
        self.start_step()

    def jump_to(self, index):
        self.step_index = index
        self.start_step()

def setfonts():
    for fontname in tkFont.names():
        default_font = tkFont.nametofont(fontname)
        default_font.configure(size=14)

def select_callback(event):
    selection = event.widget.wselection()
    #if uidict["autoparam"].value and selection:
    #    widget = selection[0][1]
    #    uidict["params"]._dict.replace(widget.kwargs)

def hint_toggle(name, op, value):
    if value:
        uidict["hint terp"].ui.parent.repack()
    else:
        uidict["hint terp"].pack_forget()

def limited_markdown(text):
    text = re.sub("    (.*?)\n", "<block>    \\1\n<normal>", text)
    text = re.sub("`(.*?)`", "<code>\\1<normal>", text)
    text = re.sub("\*{2}(.+)\*{2}", "<bold>\\1<normal>", text)
    text = re.sub("\*(.+)\*", "<italic>\\1<normal>", text)
    tagged = ["<normal>"] + re.split("(<.*?>)", text)
    return zip(tagged[::2], tagged[1::2])

def add_tagged(widget, tagged):
    for tag, text in tagged:
        widget.insert('end', text, (tag,))

histfile = "tour_guide_history"
terp = tkui.TkTerp(histfile, globals())
tkguide = TkGuide(terp)
execfile("tour_functions.py")
execfile("tour_text.py")

if len(sys.argv) > 1:
    execfile(sys.argv[1])
else:
    uiroot = UI(Tk, packanchor='n', name='root', title='TkUI Guided Tour', children=[
           UI(Frame, packside='left', children=[
             UI(Frame, packside='top', children=[
               UI(tkui.ScrolledText, name='guide', height=8, width=40, font="Verdana 14", wrap=tk.WORD),
               UI(Button, text='Embark', name="embark", command=tkguide.next),
               UI(Frame, packside='left', name="hint frame", children=[
                 UI(tkui.BoxedBool, text='Hint', name='hint'),
                 UI(tkui.Entry, text='', name='hint terp')]),
               ])]),
           UI(Frame, packside='left', name="hidden", children=[
             UI(tkui.Entry, text='', name='tkterp'),
             UI(Frame, packside='top', name='uilistframe', children=[
               UI(tkui.BoxedList, width=12, name='uilist'),
               UI(Frame, packside='left', children=[
                 UI(tkui.Entry, width=10, name='child params'),
                   UI(Button, text='+', command=addwidget),
                   UI(Button, text='+c', command=addchild),
                   UI(Button, text='-', command=delwidget)])]),
             UI(tkui.BoxedTree, name="tree"),
           ])])

uiroot.makeelem()
setfonts()
terp.bind_keys(uidict["tkterp"])
uidict['hint terp'].bind('<Return>', tkguide.next_hint)
uidict['hint terp'].bind('<KP_Enter>', tkguide.next_hint)
tkuilist = observed_list(["Entry"])

treeelem = uidict["tree"]
treeelem._tree.append(uiroot)
treeelem._tree.elem = None
treeelem.redraw()
style = ttk.Style(uidict["root"])
style.configure('Treeview', rowheight=14*2)
treeelem.column("#0", minwidth=0, width=800)
uitree = tkui.UITree(uiroot, treeelem)
uidict["tree"].bind('<<TreeviewSelect>>', select_callback)
#uidict["params"]._dict.callbacks.append(update_param)
tkuitree = treeelem.ui
uilist = uidict["uilistframe"].ui

undolog = tkui.UndoLog()
undolog.add(uiroot)

uidict["root"].bind("<Button-3>", tkui.click)

uiroot.callbacks.append(tkguide.tree_change)
tkguide.start_step()
uidict["hint"].callbacks.append(hint_toggle)
uidict["hidden"].pack_forget()
uidict["hint terp"].pack_forget()
if len(sys.argv) == 1:
    uidict["hint frame"].pack_forget()
uidict["guide"].tag_configure("<bold>", font="Verdana 15 bold")
uidict["guide"].tag_configure("<normal>", font="Verdana 14")
uidict["guide"].tag_configure("<block>", font="Monospace 13")
uidict["guide"].tag_configure("<code>", font="Monospace 13")
uidict["root"].mainloop()
