from collections import namedtuple

Step = namedtuple("Step", "message condition post hint")

def step1(uiroot):
    uidict["embark"].ui.parent.remove(uidict["embark"].ui)
    uiroot[0][0].append(uidict['tkterp'].ui)
    uidict["hint frame"].ui.parent.repack()

def step2(uiroot):
    uidict["uilist"].reset(tkuilist)
    uidict["tree"].selection_set_by_items([uidict["uilistframe"].ui])

def step3(uiroot):
    uidict["child params"].text = '{"name": "history"}'

def step4(uiroot):
    uidict["child params"].text = ''

steps = [Step("""
Welcome to the Inquisitive Platypus! I will be your guide today on your passage to Tkui. Once everyone is in and comfortably seated, we can begin our journey.
""", None, step1, []),
Step("""
Before we arrive on Tkui, let's review some safety precautions.

I will give each of you a portable interpreter, a "TkTerp" in the local dialect. If you ever get lost or get into a bind, you can always type Python commands in there to be evaluated.

Try typing

    1+1

in there now and pressing enter. You should see the output in your console or terminal.

You can use the arrow keys in the TkTerp to browse your command history.

Once you're done familiarizing yourself with your TkTerp, type

    tkguide.next()

in it. `tkguide.prev()` lets you go back a step.

You will use your TkTerp a lot in the beginning but less and less as we see more places.

[If you need a hint, check the "Hint" checkbox to see a hint of what to type next. Press enter inside the Hint's TkTerp to run the hinted command and see the next command.]
""", None, None, ["1+1", "tkguide.next()"]),

Step("""
First up is the uilist. Any UI maker will want to add and remove elements from their UI and that is all done here. Um...hmm...I'm sure it was supposed to be here. Well, we can't be far.

[If you think the uilist should **east**, type

    uiroot[0].append(uilist)

in your TkTerp and if you think its **west** of here, type

    uiroot[0].insert(0, uilist)

in your TkTerp.]
""", "uilist", step2, ["uiroot[0].append(uilist)"]),

Step("""
Right, here we are. So as I was saying.

To add an element, select its type from the list and click on the "+" button. Try adding an Entry now.

New elements are added as the next sibling of the **currently selected** element. To select an element, right click on it.

To delete an element, right click to select it and click the "-" button.

You can also use your TkTerp to do the same. Just treat element containers like tk.Frame and tk.Toplevel like lists.

To add,

    uiroot[0].append(UI(Entry, defaulttext='Hello world'))

To remove

    uiroot[0].pop()

We will come back to the language of the Tkuis eventually.

Type `tkguide.next()` when you are done.
""", None, step3,
"""uiroot[0].append(UI(Entry, defaulttext='Hello world'))
uiroot[0].pop()
tkguide.next()""".split("\n")),

Step("""
Take a moment to notice the structure which houses the uilist. Its a modern-era tkui.BoxedList.

Any changes to the list this element is reflected visually. Try adding an element to it using your TkTerp now.

    uidict["uilist"]._list.append("BoxedList")

Then try removing and putting it back.

    uidict["uilist"]._list.pop()

For easier reference, let's name this list

    tkuilist = uidict["uilist"]._list
    tkuilist.append("BoxedList")

and make our first BoxedList. Select it from the uilist, right click an element you want the list to be placed next to and then click "+".

The element created get passed the dictionnary to the left of the "+" button. Here we are setting its name to "history" for reference by uidict later.
""", "history", step4,
"""uidict["uilist"]._list.append("BoxedList")
uiroot[0].insert(1, UI(tkui.BoxedList, name="history"))""".split("\n")),

Step("""
Let's set it to track your TkTerp's command history.

    uidict["history"].reset(terp.history)

You can now add the full list of available elements by typing

    uidict["uilist"]._list.extend(tkui.tkuilist)

Type `tkguide.next()` when you are done.

If you are tired of typing `tkguide.next()` (or finding it in your history), you can add a button to call that function. Add a Button with these parameters

    {"command": tkguide.next, "text": "next"}

*or* create the button and add it through the interpreter.

    UI(Button, command=tkguide.next, text="next")

(Either `append` or `insert` this to some node. A node can be reference either by multiple indices from `uiroot` or `uielem`.)
""", None, None,
"""uidict["history"].reset(terp.history)
uidict["uilist"]._list.extend(tkui.tkuilist)
tkguide.next()""".split("\n")),

Step("""
Up ahead is the Tkuian forest.

[Add the `tkuitree` anywhere, such as with]

    uiroot[0].append(tkuitree)

As you can see in front of you is a BoxedTree. Within it, we can see all elements. As an everlight, it highlights the currently selected element all year round.

Try right clicking on some elements and observe how its highlight changes. The tree is tall so you might have to look up and down by scrolling the scroll wheel inside the tree. You can also left click an item in the tree to select them.

Type `tkguide.next()` when you are done.
""", None, None,
"""uiroot[0].append(tkuitree)
tkguide.next()
""".split("\n")),

Step("""
Now's the perfect time to take a lunch break and record our journey.

    gencode(uiroot, "my_tour.py")

which can be later recalled using

    python guided_tour.py my_tour.py

instead of `python guided_tour.py`. This only loads the layout of the UI, their content need to be filled again with

    tkguide.jump_to(7)
    uidict["history"].reset(terp.history)
    uidict["uilist"]._list.extend(tkui.tkuilist)

(Remember the first line to be able to get to these instructions to follow them later.)

For convenience, add a button to do that.

    UI(tk.Button, text="save", command=save)

Use a tex editor to edit (or add) the function `save` in `tour_functions.py` to

    def save():
        gencode(uiroot, "my_tour.py")

Save `tour_functions.py` and reload it

    execfile("tour_functions.py")

Type `tkguide.next()` when you are done.
""", None, None,
"""gencode(uiroot, "my_tour.py")
uiroot[0][0].append(UI(tk.Button, text="save", command=save))
execfile("tour_functions.py")
tkguide.next()""".split("\n")),

Step("""
Now I know there are many UI enthousiats that come to Tkui and for the ones among us today, so while you see if you like the Tkui cuisine, let me say a few words about that.

The idea of Tkui is to make the UI *and* the UI maker at the same time. Or rather, just make a single UI with the parts intended users of your application contained in a tk.Frame or tk.Toplevel and when you are done, generate the code for that tk.Frame or tk.Toplevel (using `gencode(elem, "some_file.py")`).

But honestly, if you ask me, why not keep the entire editor but keep it invisible until the user clicks some "edit" button? What if the user just wants to change the button layout a bit? Why ask them to recompile or even restart your program?

How about we all add a canvas for an UI?

    UI(tk.Frame, name="user root")

Even if you are not interested in UI making, you could put some souvenirs in there to bring back.
""", None, None,
"""uiroot[0].insert(0, UI(tk.Frame, name="user root"))
tkguide.next()""".split("\n")),

Step("""
We're approaching the center of Tkui's jungle. To your right is a forest rea-ranger's cabin. Four buttons attached to the `move_up`, `move_down`, `move_left` and `move_right` functions lets them easily rearrange elements in the UI tree.

Add these buttons now. Feel free to pick different text and add a Frame around them.

    UI(Button, text='^', command=move_up)
    UI(Button, text='v', command=move_down)
    UI(Button, text='<', command=move_left)
    UI(Button, text='>', command=move_right)

Select an element (using either right-click or the UI tree) and click the up (`^`) or down (`v`) button.

Left "dedents" the selected element in the tree and right (`>`) "indents" it.

Rearrange the tree as you like and then `tkguide.next()` to move forward.
""", None, None,
"""uiroot[0][1].append(UI(Frame, name="rearrange", packside="left"))
uidict["rearrange"].ui.append(UI(Button, text='^', command=move_up))
uidict["rearrange"].ui.append(UI(Button, text='v', command=move_down))
uidict["rearrange"].ui.append(UI(Button, text='<', command=move_left))
uidict["rearrange"].ui.append(UI(Button, text='>', command=move_right))
tkguide.next()""".split("\n")),

Step("""
This brings us to the abrupt end of our tour. There are still many parts of tkui we haven't seen. If you'd like to know when our evening and other routes will be available, please send and e-mail to

asrp email com (with an @ and . added between)

to be added to our newsletter.
""", None, None, [""])
]

["""
The massive contraption facing us is a water clock and they have quite a bit of history.

[Author's note: Undo/redo very much not fully tested.]
"""]
