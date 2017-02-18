# tkui - a visual introspective GUI maker with live editing of the GUI and its editor at the same time

## Installation and running

    pip install -r requirements.txt

which installs the dependencies [uielem](https://github.com/asrp/uielem) and [undoable](https://github.com/asrp/undoable). Run

    python guided_tour.py

to start the guided tour which gives an idea of how the pieces work.

To start the default editor instead:

    python tkui.py

Note that both need to be started from the `tkui` directory.

## Rationale and intended use

Its easier to make a GUI if you can visually see the result immediately and there are a few editors that allows this. But why should the GUI editor itself be off limits? What if you suddenly want to add many new objects of a certain type to your GUI? This is something that would need adding a feature to the editor. tkui lets you do this with no need to recompile, no need to even restart the program.

The guided tour explains this by showing it: The intended way to use tkui is to start `python tkui.py`, create a root `tk.Frame` or `tk.Toplevel` somewhere (anywhere) where the new UI you're making will be. Then add to that root element through, save everything under the root using the `gencode` function and then use the generated code for UI layout in your program.

For things with callbacks, edit `functions.py` (`tour_functions.py` in the guided tour) and reload it (using the "Reload" button or `execfile("functions")`). This way you can see right away if the new function works or not.

Some widgets are available for wrapping Python values directly (`BoxedList`, `BoxedBool`, `BoxedDict`).

## History

`tkui` is the result of a bad joke gone too far. Just wanted to see how self-referential I could make it. After that, a guided tour instead of documentation seemed self-referentially appropriate.

## Todo

- Finish explaining what everything does in the guided tour.
- Think of other visual representations of `list` and `dict`, especially `dict.
- Repackage a lot of the global state (into classes or other).
- Determine what works and doesn't work with undo/redo and make more things work.
