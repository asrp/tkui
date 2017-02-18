uiroot = UI(Tk, packanchor='n', name='root', title='TkUIMaker', children=[
           UI(Frame, packside='left', children=[
             UI(Frame, packside='top', children=[
               UI(BoxedList, name='history'),
               UI(Frame, packside='left', children=[
                 UI(Label, text='Exec: '),
                 UI(Entry, defaulttext='', name='exec')]),
               UI(Frame, packside='left', children=[
                 UI(Button, text='Generate UI code', command=gencode),
                 UI(Button, text='Reload', command=reload),
                 UI(Button, text='Printmarker', command=printmarker)])]),
             UI(Frame, packside='top', children=[
               UI(BoxedList, width=12, name='uilist'),
               UI(Frame, packside='left', children=[
                 UI(Entry, width=10, name='child params'),
                 UI(Button, text='+', command=addwidget),
                 UI(Button, text='+c', command=addchild),
                 UI(Button, text='-', command=delwidget)])]),
             UI(Frame, packside='top', children=[
               UI(BoxedList, width=12, name='undolist'),
               UI(Frame, packside='left', children=[
                 UI(Button, text='undo', command=undo),
                 UI(Button, text='redo', command=redo)])])]),
           UI(Frame, packside='left', children=[
             UI(BoxedTree, name='tree'),
             UI(Frame, packside='top', children=[
               UI(Frame, packside='left', children=[
                 UI(Button, text='^', command=move_up),
                 UI(Button, text='v', command=move_down),
                 UI(Button, text='<', command=move_left),
                 UI(Button, text='>', command=move_right)]),
               UI(BoxedBool, text='Auto update', name='autoparam'),
               UI(BoxedDict, name='params'),
               UI(BoxedList, name='bind')])]),
           UI(Frame, geometry='place', name='markers'),
           UI(Frame, geometry='place', name='overlay', children=[
             UI(Canvas, width=0, bg='red', name='rectangle', height=0)])])