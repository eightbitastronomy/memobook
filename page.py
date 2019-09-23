'''Page classes for Memobook'''

import enum
import tkinter
from tkinter import Frame
import hscroll
import note
from scrolledcanvas import ScrolledCanvas


class State(enum.Enum):
    '''Enumeration of platen states for Page'''
    BLNK = 0      # unaltered, blank page
    NBLNK = 1     # unaltered, page loaded with text, initial
    CLEAN = 2
    EDIT = 3      # page text has been altered



class Page:
    '''Prototype for pages in memobook'''
    _blank = True
    _state = State.BLNK
    tab = None
    plate = None
    note = None
    def __init__(self,win,**kwargs):
        pass
    def setnotblank(self):
        self._state = State.NBLNK
    def setblank(self):
        self._state = State.BLNK
    def blank(self):
        if self._state == State.BLNK:
            return True
        return False
    def changed(self):
        pass
    def set_changed(self,ch):
        pass
    def toggle_wrap(self,wr=None):
        pass
    def append(self,mtrl):
        ### function for adding marks. Can't be implemented in ImagePage until
        ### a system for storing image-mark information is developed
        ### (e.g., a master xml which is read into the data binding)
        pass
    def dump(self):
        pass


    
class TextPage(Page):
    '''Text-encapsuling Page'''
    _wrap = "word"
    _alt = False
    def __init__(self,win,**kwargs):
        self.tab = Frame(win)
        self.tab.pack(fill='both',expand=tkinter.YES)
        tmp_height = 10
        tmp_width = 20
        if "height" in kwargs.keys():
            tmp_height = kwargs["height"]
        if "width" in kwargs.keys():
            tmp_width = kwargs["width"]
        self.plate = hscroll.TextCompound(master=self.tab,wrap=tkinter.WORD,undo=True,height=tmp_height,width=tmp_width)
        if "note" in kwargs.keys():
            self._state = State.NBLNK
            self.note = kwargs["note"]
            self.plate.insert(tkinter.END,self.note.body)
        else:
            self.note = note.Note()
        self.plate.pack(fill='both',expand=tkinter.YES)
    def blank(self):
        if self._state == State.BLNK:
            if self.plate.edit_modified():
                return False
            else:
                return True
        else:
            return False
    def changed(self):
        return self.plate.edit_modified()
    def set_changed(self,ch):
        self.plate.edit_modified(ch)
    def toggle_wrap(self,wr=None):
        if wr and type(wr)==str:
            self._wrap = wr
            if self._wrap=="word":
                self.plate.hide_h()
            elif self._wrap=="none":
                self.plate.show_h()
        else:
            if self._wrap=="word":
                self._wrap="none"
                self.plate.show_h()
            else:
                self._wrap="word"
                self.plate.hide_h()
        self.plate.configure(wrap=self._wrap)
    def append(self,mtrl):
        self.plate.insert(tkinter.END,mtrl)
    def dump(self):
        return self.plate.get("1.0","end-1c")


        
class ImagePage(Page):
    '''Image-encapsulating Page'''
    _zoom = 100.0
    _rot = 0.0
    def __init__(self,win,nt):
        ### tab and plate must be handled differently than for TextPage...
        ### b/c I built TextCompound and ScrolledCanvas in an inherently different way.
        self.plate = ScrolledCanvas(win,image=nt.body)
        self.tab = self.plate.get_frame()
        self.plate.pack(fill='both',expand=tkinter.YES)
        self.note = nt
    def changed(self):
        return False
    def dump(self):
        return None
    ### MUST IMPLEMENT append, which requires mark storage for images!