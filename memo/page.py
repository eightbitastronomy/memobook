'''Page classes for Memobook'''

import enum
import tkinter
from tkinter import Frame, Toplevel, Entry, Button, BooleanVar, TclError, messagebox
import memo.hscroll as hscroll
import memo.note as note
from memo.imagecanvas import ImageCanvas
from memo.pdfcanvas import PDFCanvas


#class SimpleQueue(list):
#    pointer = -1
#    last = -1
#    def __init__(self,q=None):
#        if q:
#            list.__init__(self,q)
#            self.pointer = q.pointer
#            self.last = q.last
#        else:
#            list.__init__(self)
#    def push(self,item):
#        self.append(item)
#        last += 1
#    def pop(self,
        


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
    def toggle_search(self,val=None):
        pass
    def set_search(self):
        pass
    def stop_search(self):
        pass
    def start_search(self):
        pass
    def set_font(self,fam,sz,wt):
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
    __showsearch = False
    __search_hook = None
    __search_hook_phrase = None
    __search_hook_subst = None
    __search_mark_begin = ""
    __search_mark_end = ""
    __search_research = False
    __search_hook_case = None
    def __init__(self,win,**kwargs):
        self.tab = Frame(win)
        self.search = None
        self.tab.pack(fill='both',expand=tkinter.YES)
        tmp_height = 10
        tmp_width = 20
        if "height" in kwargs.keys():
            tmp_height = kwargs["height"]
        if "width" in kwargs.keys():
            tmp_width = kwargs["width"]
        if "hook" in kwargs.keys():
            self.__search_hook = kwargs["hook"]
        else:
            self.__search_hook = lambda: self.toggle_search()
        self.plate = hscroll.TextCompound(master=self.tab,
                                          wrap=tkinter.WORD,
                                          undo=True,
                                          height=tmp_height,
                                          width=tmp_width)
        if "note" in kwargs.keys():
            self._state = State.NBLNK
            self.note = kwargs["note"]
            self.plate.insert(tkinter.END,self.note.body)
        else:
            self.note = note.Note()
            self.note.mime = note.NoteMime.TEXT
        self.create_search_bar()
        if "search" in kwargs.keys():
            if kwargs["search"] == "stop":
                self.stop_search()
            else:
                self.start_search()
        if "case" in kwargs.keys():
            self.__search_hook_case = kwargs["case"]
        else:
            self.__search_hook_case = tkinter.BooleanVar()
        if "phrase" in kwargs.keys():
            self.__search_hook_phrase = kwargs["phrase"]
        else:
            self.__search_hook_phrase = ""
        if "subst" in kwargs.keys():
            self.__search_hook_subst = kwargs["subst"]
        else:
            self.__search_hook_subst = ""
        self.plate.pack(side=tkinter.BOTTOM,fill='both',expand=tkinter.YES)
        self.plate.bind("<Control-a>",lambda e: self.__highlight_all())
        self.plate.bind("<Control-f>",lambda e: self.__search_hook())

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
    def set_font(self,fam,sz,wt):
        self.plate.configure(font=(str(fam),int(sz),str(wt)))
    def append(self,mtrl):
        for item in mtrl:
            self.plate.insert(tkinter.END," @@" + str(item))
    def dump(self):
        return self.plate.get("1.0","end-1c")
    def create_search_bar(self):
        self.__bar = Frame(self.tab)
        self.__searchbanner = tkinter.Label(self.__bar,text="Find:")
        self.search = tkinter.Entry(self.__bar)
        self.search.bind("<Return>",lambda e: self.__search_forward(self.search.get()))
        self.__case_label = tkinter.Label(self.__bar,text="Case:")
        self.__case_check = tkinter.Checkbutton(self.__bar,
                                                text="",
                                                padx=0,
                                                pady=0,
                                                variable=self.__search_hook_case,
                                                onvalue=False,
                                                offvalue=True)
        self.__replacebanner = tkinter.Label(self.__bar,text="Replacement:")
        self.__replacefield = tkinter.Entry(self.__bar)
        self.__findbuttonforward = tkinter.Button(self.__bar,
                                                  pady=0,
                                                  padx=0,
                                                  text=">",
                                                  command=lambda: self.__search_forward(self.search.get()))
        self.__findbuttonreverse = tkinter.Button(self.__bar,
                                                  pady=0,
                                                  padx=0,
                                                  text="<",
                                                  command=lambda: self.__search_backward(self.search.get()))
        self.__replacebutton = tkinter.Button(self.__bar,
                                              pady=0,
                                              padx=0,
                                              text="Replace",
                                              command=lambda: self.__replace_single(self.search.get(),self.__replacefield.get()))
        self.__replacebuttonall = tkinter.Button(self.__bar,
                                                 pady=0,
                                                 padx=0,
                                                 text="All",
                                                 command=lambda: self.__replace_all(self.search.get(),self.__replacefield.get()))
        self.__closebutton = tkinter.Button(self.__bar,
                                            padx=0,
                                            pady=0,
                                            text="Close",
                                            command=lambda: self.__search_hook())
        self.__searchbanner.pack(side=tkinter.LEFT)
        self.search.pack(side=tkinter.LEFT,expand="true",fill="x")
        self.__case_label.pack(side=tkinter.LEFT)
        self.__case_check.pack(side=tkinter.LEFT)
        self.__findbuttonreverse.pack(side=tkinter.LEFT)
        self.__findbuttonforward.pack(side=tkinter.LEFT)
        self.__replacebanner.pack(side=tkinter.LEFT)
        self.__replacefield.pack(side=tkinter.LEFT,expand="true",fill="x")
        self.__replacebutton.pack(side=tkinter.LEFT)
        self.__replacebuttonall.pack(side=tkinter.LEFT)
        self.__closebutton.pack(side=tkinter.LEFT)
        self.__bar.pack(side=tkinter.TOP,fill="x")
    def __highlight_all( self ):
        self.plate.tag_add(tkinter.SEL,"1.0",tkinter.END)
        return "break"
    def toggle_search(self,val=None):
        if val:
            if val == "start":
                self.start_search()
                return
            if val == "stop":
                self.stop_search()
                return
        if self.__showsearch:
            self.stop_search()
        else:
            self.start_search()
    def start_search(self):
        self.__showsearch = True
        self.__bar.pack(fill="x")
        self.search.focus_set()
        if "found_begin" in self.plate.mark_names():
            self.plate.tag_remove(tkinter.SEL,"found_begin","found_end")
            self.plate.mark_unset("found_begin")
            self.plate.mark_unset("found_end")
    def stop_search(self):
        self.__showsearch = False
        self.__search_research = False
        self.__bar.pack_forget()
    def set_search(self):
        if self.__search_hook_phrase:
            self.search.delete(0,tkinter.END)
            self.search.insert(0,self.__search_hook_phrase.get())
        if self.__search_hook_subst:
            self.__replacefield.delete(0,tkinter.END)
            self.__replacefield.insert(0,self.__search_hook_subst.get())
    def __search_forward(self,phrase):
        foundlength = tkinter.IntVar()
        if (phrase is None) or (phrase is ""):
            return -1
        self.__search_hook_phrase.set(phrase)
        if self.__search_research == False:
            self.__search_mark_begin = self.plate.index("insert")
            self.__search_mark_end = tkinter.END
        else:
            self.__search_mark_begin = self.plate.index("found_end")
            self.plate.tag_remove(tkinter.SEL,"found_begin","found_end")
            self.__search_mark_end = tkinter.END
        self.plate.mark_set("mark_begin",self.__search_mark_begin)
        self.plate.mark_set("mark_end",self.__search_mark_end)
        loc = self.plate.search(phrase,
                                "mark_begin",
                                stopindex="mark_end",
                                forwards=True,
                                count=foundlength,
                                regexp=False,
                                nocase=self.__search_hook_case.get())
        if (loc == "") or (foundlength.get() == 0):
            if self.__search_mark_begin is not "1.0":
                self.__search_mark_begin = "1.0"
                self.plate.mark_set("mark_begin",self.__search_mark_begin)
                self.__search_mark_end = tkinter.END
                self.plate.mark_set("mark_end",self.__search_mark_end)
                loc = self.plate.search(phrase,
                                        "mark_begin",
                                        stopindex="mark_end",
                                        forwards=True,
                                        count=foundlength,
                                        regexp=False,
                                        nocase=self.__search_hook_case.get())
                if (loc == "") or (foundlength.get() == 0):
                    return 0
            else:
                return 0
        self.plate.mark_set("found_begin",loc)
        self.plate.mark_set("found_end","%s+%sc" % (loc,foundlength.get()))
        self.plate.tag_add(tkinter.SEL,"found_begin","found_end")
        self.plate.see(self.plate.index("found_end"))
        self.__search_research = True
        return 1
    def __search_backward(self,phrase):
        foundlength = tkinter.IntVar()
        if (phrase is None) or (phrase is ""):
            return
        self.__search_hook_phrase.set(phrase)
        if self.__search_research == False:
            self.__search_mark_begin = "1.0"
            self.__search_mark_end = self.plate.index("insert")
        else:
            self.__search_mark_begin = self.plate.index("1.0")
            self.__search_mark_end = self.plate.index("found_begin")
            self.plate.tag_remove(tkinter.SEL,"found_begin","found_end")
        self.plate.mark_set("mark_end",self.__search_mark_begin)
        self.plate.mark_set("mark_begin",self.__search_mark_end)
        loc = self.plate.search(phrase,
                                "mark_begin",
                                stopindex="mark_end",
                                backwards=True,
                                count=foundlength,
                                regexp=False,
                                nocase=self.__search_hook_case.get())
        if (loc == "") or (foundlength.get() == 0):
            if self.__search_mark_end is not tkinter.END:
                self.__search_mark_begin = "1.0"
                self.plate.mark_set("mark_end",self.__search_mark_begin)
                self.__search_mark_end = tkinter.END
                self.plate.mark_set("mark_begin",self.__search_mark_end)
                loc = self.plate.search(phrase,
                                        "mark_begin",
                                        stopindex="mark_end",
                                        backwards=True,
                                        count=foundlength,
                                        regexp=False,
                                        nocase=self.__search_hook_case.get())
                if (loc == "") or (foundlength.get() == 0):
                    return
            else:
                return
        self.plate.mark_set("found_begin",loc)
        self.plate.mark_set("found_end","%s+%sc" % (loc,foundlength.get()))
        self.plate.tag_add(tkinter.SEL,"found_begin","found_end")
        self.plate.see(self.plate.index("found_end"))
        self.__search_research = True
    def __replace_single(self, phrase, substitute):
        if phrase is None or phrase == "":
            return
        if substitute is None or substitute == "":
            return
        self.__search_hook_subst.set(substitute)
        if not ("found_begin" in self.plate.mark_names()):
            if self.__search_forward(phrase) < 1:
                return
        answer = messagebox.askyesno(title="Find/Replace",
                                     message="Replace this instance?",
                                     default=messagebox.NO)
        if answer:
            self.plate.delete("found_begin","found_end")
            self.plate.insert("found_begin",substitute)
            self.plate.tag_remove(tkinter.SEL,"found_begin","found_end")
            self.plate.mark_unset("found_begin")
            self.plate.mark_unset("found_end")
            self.__search_research = False
        return
    def __replace_all(self, phrase, substitute):
        if phrase is None or phrase == "":
            return
        if substitute is None or substitute == "":
            return
        self.__search_hook_subst.set(substitute)
        while self.__search_forward(phrase) > 0:
            self.plate.delete("found_begin","found_end")
            self.plate.insert("found_begin",substitute)


class ImagePage(Page):
    '''Image-encapsulating Page'''
    def __init__(self,win,nt,**kwargs):
        ### tab and plate must be handled differently than for TextPage...
        ### b/c I built TextCompound and ImageCanvas in an inherently different way.
        if "size" in kwargs.keys():
            self.plate = ImageCanvas(win,source=nt.body,fontadjust=kwargs["size"])
        else:
            self.plate = ImageCanvas(win,source=nt.body)
        self.tab = self.plate.get_frame()
        self.plate.pack(fill='both',expand=tkinter.YES)
        self.note = nt
    def changed(self):
        return False
    def dump(self):
        return None
    def append(self,mtrl):
        ### 'append' for Image is actually a 'replace' action
        self.note.tags = note.Tag()
        for item in mtrl:
            self.note.tags.silent.append(str(item))


class PDFPage(Page):
    '''PDF-encapsulating Page'''
    def __init__(self,win,nt,**kwargs):
        ### tab and plate must be handled differently than for TextPage...
        if "size" in kwargs.keys():
            self.plate = PDFCanvas(win,source=nt.body,fontadjust=kwargs["size"])
        else:
            self.plate = PDFCanvas(win,source=nt.body)
        self.tab = self.plate.get_frame()
        self.plate.pack(fill='both',expand=tkinter.YES)
        self.note = nt
    def changed(self):
        return False
    def dump(self):
        return None
    def append(self,mtrl):
        ### 'append' for Image is actually a 'replace' action
        self.note.tags = note.Tag()
        for item in mtrl:
            self.note.tags.silent.append(str(item))
