import enum
import tkinter as tk
from tkinter import ttk
from tkinter import messagebox
from tkinter import scrolledtext
from tkinter import *
from note import Note
import hscroll



#shouldn't I return this to Enum from IntEnum?
class State(enum.IntEnum):
    BLNK = 0      # unaltered, blank page
    NBLNK = 1     # unaltered, page loaded with text, initial
    CLEAN = 2
    EDIT = 3      # page text has been altered



    
class Page():
    _blank=True
    _alt=False
    _state = State.BLNK
    _wrap="word"
    def __init__(self,win,nt=None):
        self.note = Note(nt)
        self.tab = Frame(win)
        self.tab.pack(fill='both',expand=YES)
        self.txt = hscroll.ScrolledTextH(master=self.tab,wrap=tk.WORD,undo=True,height=10,width=20)
        if nt is not None:
            self._state = State.NBLNK
            self.txt.insert(tk.END,nt.text)
        self.txt.pack(fill='both',expand=YES)
    def setnotblank(self):
        self._state = State.NBLNK
    def setblank(self):
        self._state = State.BLNK
    def blank(self):
        if self._state == State.BLNK:
            if self.txt.edit_modified():
                return False
            else:
                return True
        else:
            return False
    def changed(self):
        return self.txt.edit_modified()
    def togglewrap(self,wr=None):
        if wr and type(wr)==str:
            self._wrap = wr
            if self._wrap=="word":
                self.txt.hide_h()
            elif self._wrap=="none":
                self.txt.show_h()
        else:
            if self._wrap=="word":
                self._wrap="none"
                self.txt.show_h()
            else:
                self._wrap="word"
                self.txt.hide_h()
        self.txt.configure(wrap=self._wrap)
        


        
class NotebookPlus(CustomNotebook):

    _l = -1             # tracks num of blank tabs
    _pgs = []           # the pages associated with tabs
    _save_hook = None   # save page callback fctn
    _close_hook = None  # close page callback fctn
    _ctrl = None        # ExternalConfiguration pointer
    
    def __init__(self,*args,**kwargs):
        CustomNotebook.__init__(self,*args,**kwargs)

    def ruling(self,ctrl):
        self._ctrl = ctrl
        
    def set_save_hook(self, sh):
        self._save_hook = sh

    def set_close_hook(self, ch):
        self._close_hook = ch
        
    def blankpage(self,event):
        if (event==None) or (self.identify(event.x, event.y) == ""):
            self._l += 1
            newpg = Page(self)
            if self._ctrl:
                newpg.togglewrap(self._ctrl["wrap"])
            self._pgs.append( newpg )
            if self._l == 0:
                CustomNotebook.add( self,newpg.tab,text="Blank" )
            else:
                CustomNotebook.add( self,newpg.tab,text="Blank(" + str(self._l) + ")" )
            self.select( len(self._pgs)-1 )

    def newpage(self,nt):
        if nt is None:
            # no note? exit.
            self.blankpage(None)
            return
        if len(self._pgs)>0:
            # tabs are already present, focus on the last...
            curpg = self._pgs[self.index("current")]
        else:
            # no tabs are present, make a blank page and focus on it.
            self.blankpage(None)
            curpg = self._pgs[0]
        # from above, act according the page under focus:
        if curpg.blank():
            # if the page was blank, fill it with the input-note
            self._l -= 1
            curpg.note = Note(nt)
            curpg.txt.replace("1.0",tk.END,curpg.note.text)
            self.tab(self.index("current"),text=curpg.note.title)
            if self._ctrl:
                curpg.togglewrap(self._ctrl["wrap"])
            curpg.setnotblank()
            curpg.txt.edit_modified(False)
            return
        # if the page was not blank, add another tab/page for the input-note
        newpg = Page( self,nt )
        if self._ctrl:
            newpg.togglewrap(self._ctrl["wrap"])
        self._pgs.append( newpg )
        newpg.setnotblank()
        newpg.txt.edit_modified(False)
        CustomNotebook.add( self,newpg.tab,text=nt.title )
        self.select( len(self._pgs)-1 )

    def getnoteref(self,tabnum):
        if tabnum >= len(self._pgs):
            return None
        return self._pgs[tabnum].note

    def getpageref(self,tabnum):
        if tabnum >= len(self._pgs):
            return None
        return self._pgs[tabnum]

    def writetocurrent(self,s):
        self._pgs[self.index("current")].txt.insert(tk.END,s)

    def removepage(self,tabnum):
        if self._pgs[tabnum].changed():
            self._pgs[tabnum].note.text = self._pgs[tabnum].txt.get("1.0","end-1c")
        tearoff = self._pgs.pop(tabnum)
        self.forget(tabnum)
        self.event_generate("<<NotebookTabClosed>>")
        if len(self._pgs)==0:
            self._l = -1
        return tearoff.note

    def clearchanges(self,i):
        self._pgs[i].txt.edit_modified(False)

    def changed(self,i):
        if i >= len(self._pgs):
            return False
        return self._pgs[i].changed()

    def marks(self):
        # the alternative is to remove _mrks, strip newpage, and compile a list of marks here, on the fly, to be returned
        #return self._mrks
        marks_list = []
        for p in self._pgs:
            for t in p.note.tags:
                if t not in marks_list:
                    marks_list.append(t)
        return marks_list

    def togglewrap(self):
        if len(self._pgs)==1:
            self.togglewrapall()
        else:
            self._pgs[self.index("current")].togglewrap()
    
    def togglewrapall(self):
        buffer_wrap = None
        if self._ctrl:
            if self._ctrl["wrap"]=="word":
                self._ctrl["wrap"]="none"
            else:
                self._ctrl["wrap"]="word"
            buffer_wrap = self._ctrl["wrap"]
        for p in self._pgs:
            p.togglewrap(buffer_wrap)
        
    def add(self,child,**kw):
        #allows backward compatility with CustomNotebook
        self._tabs.append(child)
        self._texts.append(None)
        CustomNotebook.add(self,child,**kw)

    def on_close_release(self, event):
        """Called when the button is released over the close button"""
        if not self.instate(['pressed']):
            return
        element =  self.identify(event.x, event.y)
        index = self.index("@%d,%d" % (event.x, event.y))
        if "close" in element and self._active == index:
            self._close_hook()
        self.state(["!pressed"])
        self._active = None



        

### the following is code that I copied from a stackoverflow thread...I was too lazy to do it myself... ###
### cannot recall if I made any minor changes to it ###


class CustomNotebook(ttk.Notebook):
    """A ttk Notebook with close buttons on each tab"""
    
    __initialized = False

    def __init__(self, *args, **kwargs):
        if not self.__initialized:
            self.__initialize_custom_style()
            self.__inititialized = True

        kwargs["style"] = "CustomNotebook"
        ttk.Notebook.__init__(self, *args, **kwargs)
        
        self._active = None
        
        self.bind("<ButtonPress-1>", self.on_close_press, True)
        self.bind("<ButtonRelease-1>", self.on_close_release)

    def on_close_press(self, event):
        """Called when the button is pressed over the close button"""
            
        element = self.identify(event.x, event.y)
            
        if "close" in element:
            index = self.index("@%d,%d" % (event.x, event.y))
            self.state(['pressed'])
            self._active = index

    def on_close_release(self, event):
        """Called when the button is released over the close button"""
        if not self.instate(['pressed']):
            return

        element =  self.identify(event.x, event.y)
        index = self.index("@%d,%d" % (event.x, event.y))

        if "close" in element and self._active == index:
            self.forget(index)
            self.event_generate("<<NotebookTabClosed>>")

        self.state(["!pressed"])
        self._active = None

    def __initialize_custom_style(self):
        style = ttk.Style()
        self.images = (
            tk.PhotoImage("img_close", data='''
            R0lGODlhCAAIAMIBAAAAADs7O4+Pj9nZ2Ts7Ozs7Ozs7Ozs7OyH+EUNyZWF0ZWQg
            d2l0aCBHSU1QACH5BAEKAAQALAAAAAAIAAgAAAMVGDBEA0qNJyGw7AmxmuaZhWEU
            5kEJADs=
            '''),
            tk.PhotoImage("img_closeactive", data='''
            R0lGODlhCAAIAMIEAAAAAP/SAP/bNNnZ2cbGxsbGxsbGxsbGxiH5BAEKAAQALAAA
            AAAIAAgAAAMVGDBEA0qNJyGw7AmxmuaZhWEU5kEJADs=
            '''),
            tk.PhotoImage("img_closepressed", data='''
            R0lGODlhCAAIAMIEAAAAAOUqKv9mZtnZ2Ts7Ozs7Ozs7Ozs7OyH+EUNyZWF0ZWQg
            d2l0aCBHSU1QACH5BAEKAAQALAAAAAAIAAgAAAMVGDBEA0qNJyGw7AmxmuaZhWEU
            5kEJADs=
            ''')
        )

        style.element_create("close", "image", "img_close",
                             ("active", "pressed", "!disabled", "img_closepressed"),
                             ("active", "!disabled", "img_closeactive"), border=8, sticky='')
        style.layout("CustomNotebook", [("CustomNotebook.client", {"sticky": "nswe"})])
        style.layout("CustomNotebook.Tab", [
            ("CustomNotebook.tab", {
                "sticky": "nswe",
                "children": [
                    ("CustomNotebook.padding", {
                        "side": "top",
                        "sticky": "nswe",
                        "children": [
                            ("CustomNotebook.focus", {
                                "side": "top",
                                "sticky": "nswe",
                                "children": [
                                    ("CustomNotebook.label", {"side": "left", "sticky": ''}),
                                    ("CustomNotebook.close", {"side": "left", "sticky": ''}),
                                ]
                            })
                        ]
                    })
                ]
            })
        ])
