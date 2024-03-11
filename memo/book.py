###############################################################################################
#  book.py: the notebook/tabs object
#
#  Author: Miguel Abele
#  Copyrighted by Miguel Abele, 2020.
#
#  License information:
#
#  This file is a part of Memobook Note Suite.
#
#  Memobook Note Suite is free software; you can redistribute it and/or
#  modify it under the terms of the GNU General Public License
#  as published by the Free Software Foundation; either version 3
#  of the License, or (at your option) any later version.
#
#  Memobook Note Suite is distributed in the hope that it will be useful,
#  but WITHOUT ANY WARRANTY; without even the implied warranty of
#  MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
#  GNU General Public License for more details.
#
#  You should have received a copy of the GNU General Public License
#  along with this program; if not, write to the Free Software
#  Foundation, Inc., 51 Franklin Street, Fifth Floor, Boston, MA  02110-1301, USA.
###############################################################################################




'''Classes for a frontend tabbed notebook pane.
   Requires backend file/data handling.'''




from base64 import b64decode
from io import BytesIO
from tkinter import ttk, BooleanVar,StringVar
from PIL import Image as im
from PIL import ImageTk
from memo.note import NoteMime
from memo.page import TextPage, ImagePage, PDFPage
from memo.config import TAB_SIZE
from memo.debug import dprint






class NotebookCloseTab(ttk.Notebook):
    
    '''Notebook with style modifications: a close button on each tab'''

    def __init__(self, *args, **kwargs):
        dprint(3, "\nNotebookCloseTab::__init")
        self.__set_style()
        kwargs["style"] = "NotebookCloseTab"
        ttk.Notebook.__init__(self, *args, **kwargs)
        self._active = None
        self.bind("<ButtonPress-1>", self.on_close_press, True)
        self.bind("<ButtonRelease-1>", self.on_close_release)

        
    def on_close_press(self, event):
        '''Callback function for pressing close-button on tab'''
        dprint(3, "\nNotebookCloseTab::on_close_press")
        element = self.identify(event.x, event.y)
        if "close" in element:
            index = self.index("@%d,%d" % (event.x, event.y))
            self.state(['pressed'])
            self._active = index

            
    def on_close_release(self, event):
        '''Callback function for releasing close-button on tab'''
        dprint(3, "\nNotebookCloseTab::on_close_release")
        if not self.instate(['pressed']):
            return
        element = self.identify(event.x, event.y)
        index = self.index("@%d,%d" % (event.x, event.y))
        if "close" in element and self._active == index:
            self.forget(index)
            self.event_generate("<<NotebookTabClosed>>")
        self.state(["!pressed"])
        self._active = None
        

    def __set_style(self):
        '''Helper method: set up style characteristics, pictures for notebook'''
        dprint(3, "\nNotebookCloseTab::__set_style")
        style = ttk.Style()
        ### use of tkinter.font produced NO EFFECT. ###
        #custom_font = tkinter.font.Font(family="Noto Sans",size=16,weight=tkinter.font.BOLD)
        #style.configure('NotebookCloseTab.Tab',font=custom_font)
        ### use of simple font tuplets (family,size,weight), did produce an effect. ###
        #style.configure('NotebookCloseTab.Tab',font=("Comfortaa",10,tkinter.font.BOLD))
        ### However, to achieve my goal, a style mapping did the trick: ###
        style.map('NotebookCloseTab.Tab',
                  foreground=[('selected', '#000000'), ('!selected', '#666666')])
        close_img = im.open(BytesIO(b64decode('''
        R0lGODlhCAAIAMIBAAAAADs7O4+Pj9nZ2Ts7Ozs7Ozs7Ozs7OyH+EUNyZWF0ZWQg
        d2l0aCBHSU1QACH5BAEKAAQALAAAAAAIAAgAAAMVGDBEA0qNJyGw7AmxmuaZhWEU
        5kEJADs=
        ''')))
        close_tk_img = ImageTk.PhotoImage(close_img.resize((TAB_SIZE,TAB_SIZE)),
                                          name="close_img")
        closeactive_img = im.open(BytesIO(b64decode('''
        R0lGODlhCAAIAMIEAAAAAP/SAP/bNNnZ2cbGxsbGxsbGxsbGxiH5BAEKAAQALAAA
        AAAIAAgAAAMVGDBEA0qNJyGw7AmxmuaZhWEU5kEJADs=
        ''')))
        closeactive_tk_img = ImageTk.PhotoImage(closeactive_img.resize((TAB_SIZE,TAB_SIZE)),
                                                name="closeactive_img")
        closepressed_img = im.open(BytesIO(b64decode('''
        R0lGODlhCAAIAMIEAAAAAOUqKv9mZtnZ2Ts7Ozs7Ozs7Ozs7OyH+EUNyZWF0ZWQg
        d2l0aCBHSU1QACH5BAEKAAQALAAAAAAIAAgAAAMVGDBEA0qNJyGw7AmxmuaZhWEU
        5kEJADs=
        ''')))
        closepressed_tk_img = ImageTk.PhotoImage(closepressed_img.resize((TAB_SIZE,TAB_SIZE)),
                                                 name="closepressed_img")
        self.images = (close_tk_img, closeactive_tk_img, closepressed_tk_img)
        style.element_create("close",
                             "image",
                             "close_img",
                             ("active", "pressed", "!disabled", "closepressed_img"),
                             ("active", "!disabled", "closeactive_img"),
                             border=TAB_SIZE,
                             sticky='')
        style.layout("NotebookCloseTab",
                     [("NotebookCloseTab.client", {"sticky": "nswe"})])
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

    '''Notebook class for use with Memobook'''

    _l = -1                 # tracks num of blank tabs
    _pgs = None             # the pages associated with tabs
    _save_hook = None       # save page callback fctn
    _close_hook = None      # close page callback fctn
    _ctrl = None            # Configuration pointer
    __show_search = "stop"  # toggle for search bar; used for tabs created after search is started
    __search_phrase = None
    __search_subst = None
    __search_case = None

    
    def __init__(self, *args, **kwargs):
        dprint(3, "\nBook::__init__")
        if "ruling" in kwargs:
            self._ctrl = kwargs["ruling"]
            del kwargs["ruling"]
        self._pgs = []
        NotebookCloseTab.__init__(self, *args, **kwargs)
        self.__search_case = BooleanVar()
        self.__search_phrase = StringVar()
        self.__search_subst = StringVar()
        self.bind("<<NotebookTabChanged>>", lambda e:self.__switched_tabs())
        if self._ctrl:
            self.__blanktext(None)
            self.__ready(self._pgs[0])

            
    def ruling(self, ctrl):
        '''Set reference to configuration object, "ctrl"'''
        dprint(3, "\nBook::ruling")
        self._ctrl = ctrl

    def set_save_hook(self, sh):
        '''Set callback function for writing tab contents to disk'''
        dprint(3, "\nBook::set_save_hook")
        self._save_hook = sh
        

    def set_close_hook(self, ch):
        '''Set callback function for closing tab and its contents'''
        dprint(3, "\nBook::set_close_hook")
        self._close_hook = ch
        

    def __switched_tabs(self):
        '''Show search bar if tabs were switched while search is ongoing'''
        dprint(3, "\nBook::__switched_tabs")
        if self.__show_search == "start":
            self._pgs[self.index("current")].set_search()

            
    def __blanktext(self, event):
        '''Create tab with blank TextPage'''
        dprint(3, "\nBook::__blanktext")
        if (event is None) or (self.identify(event.x, event.y) == ""):
            self._l += 1
            newpg = TextPage(self,
                             hook=lambda: self.toggle_search(),
                             search=self.__show_search,
                             case=self.__search_case,
                             phrase=self.__search_phrase,
                             subst=self.__search_subst)
            newpg.set_font(self._ctrl["font"]["family"],
                           self._ctrl["font"]["size"],
                           self._ctrl["font"]["weight"])
            if self._ctrl:
                newpg.toggle_wrap(self._ctrl["wrap"])
            self._pgs.append( newpg )
            if self._l == 0:
                NotebookCloseTab.add(self,
                                     newpg.tab,
                                     text="Blank")
            else:
                NotebookCloseTab.add(self,
                                     newpg.tab,
                                     text="Blank(" + str(self._l) + ")")
            self.select(len(self._pgs)-1)

            
    def newpage(self, nt):
        '''Create tab and load with appropriate Page-type and contents''' 
        dprint(3, "\nBook::newpage::")
        if nt is None:
            # Error, or called by a double-click event (binding in memobook). Blank-text and return.
            dprint(3, "note arg is None")
            self.__blanktext(None)
            blank = self._pgs[len(self._pgs)-1]
            self.__ready(blank)
            return
        if self._pgs:
            dprint(3, "Pages (_pgs) are present")
            # tabs are already present, focus on the last...
            curindex = self.index("current")
            curpg = self._pgs[curindex]
            if curpg.blank():
                dprint(3, "\nBook::newpage::current page is blank")
                # blank page? drop it and move on
                self._pgs.pop(curindex)
                self.forget(curindex)
                self.event_generate("<<NotebookTabClosed>>")
                self._l -= 1
            else:
                dprint(3, "\nBook::newpage::current page is not blank")
        # make a new page based on mime-type
        newpg = None
        if nt.mime == NoteMime.TEXT:
            newpg = TextPage(self,
                             note=nt,
                             hook=lambda: self.toggle_search(),
                             search=self.__show_search,
                             case=self.__search_case,
                             phrase=self.__search_phrase,
                             subst=self.__search_subst)
            newpg.set_font(self._ctrl["font"]["family"],
                           self._ctrl["font"]["size"],
                           self._ctrl["font"]["weight"])
            if self._ctrl:
                newpg.toggle_wrap(self._ctrl["wrap"])
        if nt.mime == NoteMime.IMAGE:
            newpg = ImagePage(self,
                              nt,
                              size=int(self._ctrl["style"]["font"]["size"]))
        if nt.mime == NoteMime.PDF:
            newpg = PDFPage(self,
                            nt,
                            size=int(self._ctrl["style"]["font"]["size"]))
        self._pgs.append(newpg)
        newpg.setnotblank()
        newpg.set_changed(False)
        NotebookCloseTab.add(self,
                             newpg.tab,
                             text=nt.title)
        self.__ready(newpg)
        self.showchangestate(newpg)
        self.select(len(self._pgs)-1)
        

    def __ready(self, pg):
        '''Make tab and contents visible and set callback for state changes'''
        dprint(3, "\nBook::__ready")
        pg.plate.set_hook(lambda: self.showchangestate(pg))
        pg.plate.focus_set()
        

    def getnoteref(self, tabnum):
        '''Return note associated with tab'''
        dprint(3, "\nBook::getnoteref")
        if tabnum >= len(self._pgs):
            return None
        return self._pgs[tabnum].note
    

    def getpageref(self, tabnum):
        '''Return page associated with tab'''
        dprint(3, "\nBook::getpageref")
        if tabnum >= len(self._pgs):
            return None
        return self._pgs[tabnum]
    

    def writetocurrent(self, s):
        '''Write string to page platen via append method'''
        dprint(3, "\nBook::writetocurrent")
        self._pgs[self.index("current")].append(s)

        
    def removepage(self, tabnum):
        '''Remove tab from book'''
        dprint(3, "\nBook::removepage")
        if self._pgs[tabnum].changed():
            # with Text & Image Page, only TextPage can have a true value
            self._pgs[tabnum].note.body = self._pgs[tabnum].plate.get("1.0", "end-1c")
        tearoff = self._pgs.pop(tabnum)
        self.forget(tabnum)
        self.event_generate("<<NotebookTabClosed>>")
        if len(self._pgs) == 0:
            self._l = -1
        return tearoff.note
    

    def clearchanges(self, i):
        '''Set change-state to false and remove visible "changed" marker from tab'''
        dprint(3, "\nBook::clearchanges")
        self._pgs[i].set_changed(False)
        self.showchangestate(self._pgs[i])

        
    def showchangestate(self, page):
        '''Display visible "changed" marker on tab if appropriate'''
        dprint(3, "\nBook::showchangestate")
        for i in range(0, len(self._pgs)):
            if page == self._pgs[i]:
                break
        title = self.tab(i, "text").strip("*")
        if page.changed():
            self.tab(i, text="*"+title)
        else:
            self.tab(i, text=title)

            
    def changed(self, i):
        '''Test for changes to page contents: false if not changed'''
        dprint(3, "\nBook::changed")
        if i >= len(self._pgs):
            return False
        return self._pgs[i].changed()

    
    def marks(self):
        '''Collect and return all marks associated with current tabs'''
        dprint(3, "\nBook::marks")
        # the alternative is to remove _mrks, strip newpage,
        # and compile a list of marks here, on the fly, to be returned
        #return self._mrks
        marks_list = []
        for p in self._pgs:
            for t in p.note.tags:
                if t not in marks_list:
                    marks_list.append(t)
            if p.note.tags.silent:
                for st in p.note.tags.silent:
                    if st not in marks_list:
                        marks_list.append(st)
        return marks_list
    

    def togglewrap(self):
        '''Toggle word-wrap for current tab'''
        dprint(3, "\nBook::togglewrap")
        if len(self._pgs) == 1:
            self.togglewrapall()
        else:
            self._pgs[self.index("current")].toggle_wrap()

            
    def togglewrapall(self):
        '''Toggle word-wrap for all tabs'''
        dprint(3, "\nBook::togglewrapall")
        if self._ctrl:
            if self._ctrl["wrap"] == "word":
                self._ctrl["wrap"] = "none"
            else:
                self._ctrl["wrap"] = "word"
        for p in self._pgs:
            p.toggle_wrap(self._ctrl["wrap"])

            
    def show_search(self):
        '''Show search bar'''
        dprint(3, "\nBook::show_search")
        self.__show_search = "start"
        for p in self._pgs:
            p.toggle_search("start")
            

    def kill_search(self):
        '''Hide search bar'''
        dprint(3, "\nBook::kill_search")
        self.__show_search = "stop"
        for p in self._pgs:
            p.toggle_search("stop")
            

    def toggle_search(self, val=None):
        '''Toggle search bar visible/hidden or set to specific state'''
        dprint(3, "\nBook::toggle_search")
        if val:
            if val == "start":
                self.__show_search = "start"
                for p in self._pgs:
                    p.start_search()
                return "break"
            if val == "stop":
                self.__show_search = "stop"
                for p in self._pgs:
                    p.stop_search()
                return "break"
        if self.__show_search == "start":
            self.__show_search = "stop"
            for p in self._pgs:
                p.stop_search()
        else:
            self.__show_search = "start"
            for p in self._pgs:
                p.start_search()
        return "break"
    

    def set_page_font(self, fam, sz, wt):
        '''Set font in current tab. Does notthing for Image or PDF types.'''
        dprint(3, "\nBook::set_page_font")
        for p in self._pgs:
            p.set_font(fam, sz, wt)
            

    def on_close_release(self, event):
        '''Override for parent callback function for release of close button'''
        dprint(3, "\nBook::on_close_release")
        if not self.instate(['pressed']):
            return
        element =  self.identify(event.x, event.y)
        index = self.index("@%d,%d" % (event.x, event.y))
        if "close" in element and self._active == index:
            self._close_hook()
        self.state(["!pressed"])
        self._active = None
