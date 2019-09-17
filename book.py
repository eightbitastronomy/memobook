import enum
import PIL
from PIL import Image as im
from PIL import ImageTk
import base64
import io
#import tkinter as tk
from tkinter import ttk
from tkinter import messagebox
from tkinter import scrolledtext
from tkinter.font import *
from tkinter import *
from note import Note
from page import *
import hscroll
from config import TAB_SIZE



#shouldn't I return this to Enum from IntEnum?
class State(enum.IntEnum):
    BLNK = 0      # unaltered, blank page
    NBLNK = 1     # unaltered, page loaded with text, initial
    CLEAN = 2
    EDIT = 3      # page text has been altered





class NotebookCloseTab(ttk.Notebook):
    
    def __init__(self, *args, **kwargs):
        self.__set_style()
        kwargs["style"] = "NotebookCloseTab"
        ttk.Notebook.__init__(self, *args, **kwargs)
        self._active = None
        self.bind("<ButtonPress-1>", self.on_close_press, True)
        self.bind("<ButtonRelease-1>", self.on_close_release)

    def on_close_press(self, event):
        element = self.identify(event.x, event.y)
        if "close" in element:
            index = self.index("@%d,%d" % (event.x, event.y))
            self.state(['pressed'])
            self._active = index

    def on_close_release(self, event):
        if not self.instate(['pressed']):
            return
        element =  self.identify(event.x, event.y)
        index = self.index("@%d,%d" % (event.x, event.y))
        if "close" in element and self._active == index:
            self.forget(index)
            self.event_generate("<<NotebookTabClosed>>")
        self.state(["!pressed"])
        self._active = None

    def __set_style(self):
        style = ttk.Style()
        ### use of tkinter.font produced NO EFFECT. ###
        #custom_font = tkinter.font.Font(family="Noto Sans",size=16,weight=tkinter.font.BOLD)
        #style.configure('NotebookCloseTab.Tab',font=custom_font)
        ### use of simple font tuplets (family,size,weight), did produce an effect. ###
        #style.configure('NotebookCloseTab.Tab',font=("Comfortaa",10,tkinter.font.BOLD))
        ### However, to achieve my goal, a style mapping did the trick: ### 
        style.map('NotebookCloseTab.Tab',foreground=[('selected','#000000'),('!selected','#666666')])
        close_img = im.open(io.BytesIO(base64.b64decode('''
        R0lGODlhCAAIAMIBAAAAADs7O4+Pj9nZ2Ts7Ozs7Ozs7Ozs7OyH+EUNyZWF0ZWQg
        d2l0aCBHSU1QACH5BAEKAAQALAAAAAAIAAgAAAMVGDBEA0qNJyGw7AmxmuaZhWEU
        5kEJADs=
        ''')))
        close_tk_img = ImageTk.PhotoImage(close_img.resize((TAB_SIZE,TAB_SIZE)),name="close_img")
        closeactive_img = im.open(io.BytesIO(base64.b64decode('''
        R0lGODlhCAAIAMIEAAAAAP/SAP/bNNnZ2cbGxsbGxsbGxsbGxiH5BAEKAAQALAAA
        AAAIAAgAAAMVGDBEA0qNJyGw7AmxmuaZhWEU5kEJADs=
        ''')))
        closeactive_tk_img = ImageTk.PhotoImage(closeactive_img.resize((TAB_SIZE,TAB_SIZE)),name="closeactive_img")
        closepressed_img = im.open(io.BytesIO(base64.b64decode('''
        R0lGODlhCAAIAMIEAAAAAOUqKv9mZtnZ2Ts7Ozs7Ozs7Ozs7OyH+EUNyZWF0ZWQg
        d2l0aCBHSU1QACH5BAEKAAQALAAAAAAIAAgAAAMVGDBEA0qNJyGw7AmxmuaZhWEU
        5kEJADs=
        ''')))
        closepressed_tk_img = ImageTk.PhotoImage(closepressed_img.resize((TAB_SIZE,TAB_SIZE)),name="closepressed_img")
        self.images = (close_tk_img,closeactive_tk_img,closepressed_tk_img)
        style.element_create("close", "image", "close_img",
                             ("active", "pressed", "!disabled", "closepressed_img"),
                             ("active", "!disabled", "closeactive_img"), border=TAB_SIZE, sticky='')
        style.layout("NotebookCloseTab", [("NotebookCloseTab.client", {"sticky": "nswe"})])
        style.layout("NotebookCloseTab.Tab", [
            ("NotebookCloseTab.tab", {
                "sticky": "nswe",
                "children": [
                    ("NotebookCloseTab.padding", {
                        "side": "top",
                        "sticky": "nswe",
                        "children": [
                            ("NotebookCloseTab.focus", {
                                "side": "top",
                                "sticky": "nswe",
                                "children": [
                                    ("NotebookCloseTab.label", {"side": "left", "sticky": ''}),
                                    ("NotebookCloseTab.close", {"side": "left", "sticky": ''}),
                                ]
                            })
                        ]
                    })
                ]
            })
        ])
    

        
        


        
class Book(NotebookCloseTab):

    _l = -1             # tracks num of blank tabs
    _pgs = []           # the pages associated with tabs
    _save_hook = None   # save page callback fctn
    _close_hook = None  # close page callback fctn
    _ctrl = None        # Configuration pointer
    
    def __init__(self,*args,**kwargs):
        NotebookCloseTab.__init__(self,*args,**kwargs)
        self.__blanktext(None)
        self.__ready(self._pgs[0])
        
    def ruling(self,ctrl):
        self._ctrl = ctrl
        
    def set_save_hook(self, sh):
        self._save_hook = sh

    def set_close_hook(self, ch):
        self._close_hook = ch
        
    def __blanktext(self,event):
        if (event==None) or (self.identify(event.x, event.y) == ""):
            self._l += 1
            newpg = TextPage(self)
            if self._ctrl:
                newpg.toggle_wrap(self._ctrl["wrap"])
            self._pgs.append( newpg )
            if self._l == 0:
                NotebookCloseTab.add( self,newpg.tab,text="Blank" )
            else:
                NotebookCloseTab.add( self,newpg.tab,text="Blank(" + str(self._l) + ")" )
            self.select( len(self._pgs)-1 )

    def newpage(self,nt):
        if nt is None:
            # no note? Error, or called by a double-click event (binding in memobook). Exit.
            self.__blanktext(None)
            blank = self._pgs[len(self._pgs)-1]
            self.__ready(blank)
            return
        if len(self._pgs)>0:
            # tabs are already present, focus on the last...
            curpg = self._pgs[self.index("current")]
        else:
            # no tabs are present, make a blank page and focus on it.
            self.__blanktext(None)
            curpg = self._pgs[0]
        # from above, act according the page under focus:
        if curpg.blank():
            # if the page was blank, fill it with the input-note
            self._l -= 1
            curpg.note = Note(nt)
            curpg.plate.replace("1.0",tkinter.END,curpg.note.body)
            self.tab(self.index("current"),text=curpg.note.title)
            if self._ctrl:
                curpg.toggle_wrap(self._ctrl["wrap"])
            curpg.setnotblank()
            curpg.set_changed(False)
            self.__ready(curpg)
            self.showchangestate(curpg)
            return
        # if the page was not blank, add another tab/page for the input-note
        newpg = TextPage( self,note=nt )
        if self._ctrl:
            newpg.toggle_wrap(self._ctrl["wrap"])
        self._pgs.append( newpg )
        newpg.setnotblank()
        newpg.set_changed(False)
        NotebookCloseTab.add( self,newpg.tab,text=nt.title )
        self.__ready(newpg)
        self.showchangestate(newpg)
        self.select( len(self._pgs)-1 )

    def __ready(self,pg):
        pg.plate.set_hook(lambda:self.showchangestate(pg))
        pg.plate.focus_set()
        
    def getnoteref(self,tabnum):
        if tabnum >= len(self._pgs):
            return None
        return self._pgs[tabnum].note

    def getpageref(self,tabnum):
        if tabnum >= len(self._pgs):
            return None
        return self._pgs[tabnum]

    def writetocurrent(self,s):
        self._pgs[self.index("current")].append(s)

    def removepage(self,tabnum):
        if self._pgs[tabnum].changed():
            # with Text & Image Page, only TextPage can have a true value
            self._pgs[tabnum].note.body = self._pgs[tabnum].plate.get("1.0","end-1c")
        tearoff = self._pgs.pop(tabnum)
        self.forget(tabnum)
        self.event_generate("<<NotebookTabClosed>>")
        if len(self._pgs)==0:
            self._l = -1
        return tearoff.note

    def clearchanges(self,i):
        self._pgs[i].set_changed(False)
        self.showchangestate(self._pgs[i])

    def showchangestate(self,page):
        for i in range(0,len(self._pgs)):
            if page == self._pgs[i]:
                    break
        title = self.tab(i,"text").strip("*")
        if page.changed():
            self.tab(i,text="*"+title)
        else:
            self.tab(i,text=title)

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
            self._pgs[self.index("current")].toggle_wrap()
    
    def togglewrapall(self):
        if self._ctrl:
            if self._ctrl["wrap"]=="word":
                self._ctrl["wrap"]="none"
            else:
                self._ctrl["wrap"]="word"
        for p in self._pgs:
            p.toggle_wrap(self._ctrl["wrap"])

    def on_close_release(self, event):
        if not self.instate(['pressed']):
            return
        element =  self.identify(event.x, event.y)
        index = self.index("@%d,%d" % (event.x, event.y))
        if "close" in element and self._active == index:
            self._close_hook()
        self.state(["!pressed"])
        self._active = None
