###############################################################################################
#  tkmemobook.py: the tk GUI object that runs the show
#
#  Author (pseudonomously): eightbitastronomy (eightbitastronomy@protonmail.com)
#  Copyrighted by eightbitastronomy, 2019.
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



'''TkMemobook class file: the frontend and control structure for the application.
   Configuration values are in config.py or loaded via extconf.py.
   Database is handled in binding.py.'''


import enum
import os
import os.path
from tkinter import Tk
from tkinter import Menu
from tkinter import messagebox
from tkinter import filedialog
from tkinter import Toplevel
from tkinter import END
from tkinter import Frame
from tkinter import Button
from tkinter import Radiobutton
from tkinter import StringVar
from tkinter import Listbox
from tkinter import Label
from tkinter import Entry
from tkinter import TclError
from tkinter import font
from tkinter.ttk import Combobox
from tkinter.ttk import Style
from memo.memobook import Memobook
from memo.book import Book
import memo.parse as parse
from memo.hscroll import ListboxHV
from memo.note import NoteMime
from memo.debug import dprint





class Heading(enum.Enum):

    '''Menu headings'''

    MF = 'File'
    ME = 'Edit'
    MS = 'Sources'
    MH = 'Help'


    

class TkMemobook(Memobook):

    '''Memobook Tk frontend'''

    root = None
    tabs = None
    menu = None
    offset = None
    

    def __init__(self, **kwargs):
        dprint(3, "\nTkMemobook::__init__::")
        Memobook.__init__(self, **kwargs)
        self.offset = []
        if "root" in kwargs.keys():
            self.root = kwargs["root"]
        else:
            self.root = Tk()
            ### setting theme is inexplicably only affecting Book and the file-open dialogue,
            ### nothing else. Setting theme of, e.g., self.menu also isn't working.
            #self.root.style = Style()
            #self.root.style.theme_use(self.ctrl["style"]["theme"])
            self.root.title("Memobook")
        # adjust Tk's font sizes according to conf.xml "style" section.
        # Positive value in conf.xml is an increase in size, negative a decrease
        for name in font.names():
            tk_font = font.nametofont(name)
            new_size = tk_font["size"] - int(self.ctrl["style"]["font"]["size"])
            tk_font.configure(size=new_size)
        # deal with hidden files for file dialogue by calling a dummy dialogue with nonsense options: (method taken from online forum)
        # (this is done here and not in binding class because it is a front-end matter, not a back-end one)
        try:
            self.root.tk.call('tk_getOpenFile', '-flurpee')
        except TclError:
            #catch and discard the TclError that the nonsense option caused
            pass
        finally:
            self.root.tk.call('set', '::tk::dialog::file::showHiddenBtn', '1')
            self.root.tk.call('set', '::tk::dialog::file::showHiddenVar', '0')
        if "tabs" in kwargs.keys():
            self.tabs = kwargs["tabs"]
        else:
            self.tabs = Book(self.root, ruling=self.ctrl, width=self.ctrl["x"], height=self.ctrl["y"])
            #self.tabs.ruling(self.ctrl)  #if ruling is not specified in constructor call, it must be done so here
            self.tabs.set_save_hook(lambda:self.save_note())
            self.tabs.set_close_hook(lambda:self.close_page())
            self.tabs.bind("<Double-Button-1>", lambda e: self.tabs.newpage(None))
        self.menu = Menu(self.root)
        self.set_bindings()
        dprint(3, "Tk initialization complete. Displaying...")
        self.tabs.grid_columnconfigure(0, weight=1)
        self.tabs.grid_rowconfigure(0, weight=1)
        self.tabs.grid(sticky="nswe")
        self.populate_menus()
        self.root.config(menu=self.menu)
        self.root.grid_columnconfigure(0, weight=1)
        self.root.grid_rowconfigure(0, weight=1)
        self.offset = [ self.tabs.winfo_reqwidth()-int(self.ctrl["x"]),
                        self.tabs.winfo_reqheight()-int(self.ctrl["y"]) ]


    def populate_menus(self):
        '''Populate menus using Tk library'''
        dprint(3, "\nTkMemobook::populate_menus:: ")
        mdict = { Heading.MF:Menu(self.menu, tearoff=0),
                  Heading.ME:Menu(self.menu, tearoff=0),
                  Heading.MS:Menu(self.menu, tearoff=0),
                  Heading.MH:Menu(self.menu, tearoff=0) }
        for k in mdict:
            self.menu.add_cascade(label=k.value, menu=mdict[k])
        mdict[Heading.MF].add_command(label="New",
                                      command=lambda: self.tabs.newpage(None))
        mdict[Heading.MF].add_command(label="Open by mark",
                                      command=lambda: self.__open_mark())
        mdict[Heading.MF].add_command(label="Open from file",
                                      command=lambda: self.open_file())
        mdict[Heading.MF].add_command(label="Save",
                                      command=lambda: self.save_note())
        mdict[Heading.MF].add_command(label="Save as",
                                      command=lambda: self.save_note_as())
        mdict[Heading.MF].add_separator()
        mdict[Heading.MF].add_command(label="New tab",
                                      command=lambda: self.tabs.newpage(None))
        mdict[Heading.MF].add_command(label="Close tab",
                                      command=lambda: self.close_page())
        mdict[Heading.MF].add_command(label="Close all tabs",
                                      command=lambda: self.close_all())
        mdict[Heading.MF].add_separator()
        mdict[Heading.MF].add_command(label="Quit",
                                      command=lambda: self.exit_all(None))
        mdict[Heading.ME].add_command(label="Find/Replace",
                                      command=lambda: self.tabs.toggle_search("start"))
        mdict[Heading.ME].add_command(label="Edit marks",
                                      command=lambda: self.mark_dialogue())
        mdict[Heading.ME].add_command(label="Font",
                                      command=lambda: self.font_dialogue())
        mdict[Heading.ME].add_separator()
        mdict[Heading.ME].add_command(label="Toggle tab wrap",
                                      command=lambda: self.tabs.togglewrap())
        mdict[Heading.ME].add_checkbutton(label="Toggle global wrap",
                                          onvalue="word",
                                          offvalue="none",
                                          variable=self.ctrl["wrap"],
                                          command=lambda: self.tabs.togglewrapall())
        mdict[Heading.MS].add_command(label="Scan",
                                      command=lambda: self.__get_busy_with(None,self.data.populate))
        mdict[Heading.MS].add_command(label="Clear",
                                      command=lambda: self.data.clear())
        mdict[Heading.MS].add_command(label="Manage locations",
                                      command=lambda: self.open_pop(self.__open_pop_remove,
                                                                    self.__open_pop_add,
                                                                    self.__open_pop_apply))
        mdict[Heading.MH].add_command(label="About",
                                      command=lambda: self.publication_info())


    def set_bindings(self):
        '''Bind methods to keystrokes'''
        dprint(3, "\nTkMemobook::set_bindings:: ")
        self.root.protocol("WM_DELETE_WINDOW", lambda: self.exit_all(None))
        self.root.bind("<Control-f>", lambda e: self.tabs.toggle_search())
        self.root.bind("<Control-q>", lambda e: self.exit_all(None))
        self.root.bind("<Control-w>", lambda e: self.close_page())
        self.root.bind("<Control-n>", lambda e: self.tabs.newpage(None))
        self.root.bind("<Control-s>", lambda e: self.save_note())
        self.root.bind("<Alt-m>", lambda e: self.mark_dialogue())


    def __open_mark(self):
        '''Open files by mark: Major dialogue for mark choices and logic'''
        ### despite using select, invoke, focus_set, event_generate,
        ### tk wouldn't set the OR radiobutton as default.
        ### So the following sub-function is a workaround to force the issue.
        def default_selection(var):
            var.set("or")
        dprint(3, "\nTkMemobook::open_mark:: ")
        #Memobook.open_mark(self,toc)
        toc = [ item for item in self.data.toc() ]
        toc.sort(key=lambda x: x.lower())
        getter = Toplevel(self.root)
        getter_list = ListboxHV(getter, selectmode="multiple")
        for item in toc:
            getter_list.insert(END, item)
        getter_list.pack(fill="both", expand="true")
        button_frame = Frame(getter)
        logic_variable = StringVar(None, "or")
        radiobutt_OR = Radiobutton(button_frame,
                                   text="OR",
                                   variable=logic_variable,
                                   command=lambda: default_selection(logic_variable),  # get tk to give default selection
                                   value="or")
        radiobutt_AND = Radiobutton(button_frame,
                                    text="AND",
                                    variable=logic_variable,
                                    value="and")
        retbutt = Button(button_frame,
                         text="Apply",
                         command=lambda: self.__open_mark_confirm(getter,
                                                                  [ toc[int(j)] for j in getter_list.curselection() ],
                                                                  logic_variable.get()))
        cancbutt = Button(button_frame,
                          text="Cancel",
                          command=lambda: getter.destroy())
        radiobutt_OR.pack(side="left")
        radiobutt_AND.pack(side="left")
        cancbutt.pack(side="left")
        retbutt.pack(side="left")
        button_frame.pack(side="bottom")
        radiobutt_OR.invoke()


    def __open_mark_confirm(self, win, ls, logic):
        '''Open files by mark: Minor dialogue for confirming file selection if 2+ files were found'''
        def launch(choices):
            if choices:
                for note in choices:
                    self.tabs.newpage(note)
            chooser.destroy()
            win.destroy()
        dprint(3, "\nTkMemobook::__open_mark_confirm:: ")
        if ls:
            if logic == "or":
                notes = self.__get_busy_with(win, self.data.open_from_toc, ls)
            elif logic == "and":
                notes = self.__get_busy_with(win, self.data.open_from_toc_intersection, ls)
            else:
                notes = []
            if not notes:
                last = self.data.get_last_error()
                if last:
                    messagebox.showinfo("Open error",
                                    "Unable to open file(s): " + str(last))
                else:
                    failure = ", ".join(ls)
                    if logic == "or":
                        messagebox.showinfo("Open failure",
                                            "Unable to find files for any of the following marks: " + failure)
                    else:
                        messagebox.showinfo("Open failure",
                                            "Unable to find files containing each of the following marks: " + failure)
            else:
                if len(notes) == 1:
                    self.tabs.newpage(notes[0])
                    win.destroy()
                    return
                notes.sort(key=lambda x: str(os.path.basename(x.ID)))
                chooser = Toplevel(self.root)
                chooser_frame = Frame(chooser)
                chooser_banner = Label(chooser_frame,
                                       text="The following files were found.\nPlease select which files to open:",
                                       padx=10,
                                       pady=5)
                chooser_list = ListboxHV(chooser_frame,selectmode="multiple")
                for i,item in enumerate(notes):
                    chooser_list.insert(END,
                                        "{:>5}{:<32}".format(str(i+1)+". ",
                                                             str(os.path.basename(item.ID)) + "  (" + str(os.path.dirname(item.ID)) + ")"))
                chooser_list.pack(fill="both",expand="true")
                button_frame = Frame(chooser)
                button_open = Button(button_frame,
                                     text="Open",
                                     command=lambda: launch([notes[j] for j in map(int,chooser_list.curselection())]))
                button_open_all = Button(button_frame,
                                         text="Open All",
                                         command=lambda: launch(notes))
                button_cancel = Button(button_frame,
                                       text="Cancel",
                                       command=lambda: chooser.destroy())
                chooser_list.pack(side="bottom")
                chooser_banner.pack(side="top")
                chooser_frame.pack(side="top",fill="both",expand="true")
                button_cancel.pack(side="left")
                button_open_all.pack(side="left")
                button_open.pack(side="right")
                button_frame.pack(side="bottom")


    def _build_file_types(self):
        '''Build available file types from config.xml (Parent class method)'''
        dprint(3, "\nTkMemobook::_build_file_types:: ")
        return Memobook._build_file_types(self)

    
    def open_file(self):
        '''Open file by name: calls Tk file dialogue'''
        dprint(3, "\nTkMemobook::open_file:: ")
        active_dir = self.data.get_active_open()
        if not active_dir:
            file_names = filedialog.askopenfilenames(initialdir=self.data.active_base(),
                                                     title="Choose file(s) to open",
                                                     filetypes=self._build_file_types())
        else:
            file_names = filedialog.askopenfilenames(initialdir=active_dir,
                                                     title="Choose file(s) to open",
                                                     filetypes=self._build_file_types())
        if file_names:
            dprint(3, "File names from dialogue are: " + str(file_names) + ". ")
            self.data.set_active_open(os.path.dirname(file_names[0]))
            list_of_notes = self.__get_busy_with(None, self.data.open_note,file_names)
            for nt in list_of_notes:
                self.tabs.newpage(nt)


    def save_note(self):
        '''Save note to disk, save marks to memobook. Calls _process_save_target.'''
        dprint(3, "\nTkMemobook::save_note:: ")
        index = self.tabs.index("current")
        dprint(3, "Index is " + str(index) + ". ")
        if self.tabs.changed(index) is False:
            return
        save_nt = self.tabs.getnoteref(index)
        save_nt.body = self.tabs.getpageref(index).plate.get("1.0", "end-1c")
        ret_val = self._process_save_target(save_nt,
                                            callback=lambda c:self.tabs.tab(index,text=c))
        if (ret_val > 0):
            dprint(2, "Unable to process save target. Aborting.\n")
            messagebox.showinfo("Save target error",
                                "Unable to process save target")
            return
        if (ret_val < 0) or save_nt.ID == "":
            return
        if self.data.save_note(save_nt) :
            dprint(2, "Save error in data.save_note. Aborting.\n")
            messagebox.showinfo("Save error",
                                "Unable to save note: " + str(self.data.get_last_error()) )
            return
        self.tabs.clearchanges(index)


    def save_note_as(self):
        '''Save-as functionality: save note to disk, save marks to memobook. Calls _process_save_target.'''
        dprint(3, "\n TkMemobook::save_note_as:: ") 
        index = self.tabs.index("current")
        dprint(3, "Index is " + str(index) + ". ")
        save_nt = self.tabs.getnoteref(index)
        save_nt.body = self.tabs.getpageref(index).dump()
        if not save_nt.body:
            dprint(3, "No note body, returning.")
            return
        ret_targ = self._process_save_target(save_nt,
                                             saveas=True,
                                             callback=lambda c:self.tabs.tab(index,text=c))
        if (ret_targ > 0):
            dprint(2, "Unable to process save target. Aborting.\n")
            messagebox.showinfo("Save target error",
                                "Unable to process save target")
            return
        if (ret_targ < 0):
            return
        if self.data.save_note(save_nt):
            dprint(2, "Save error in data.save_note. Aborting.\n")
            messagebox.showinfo("Save error",
                                "Unable to save note: " + str(self.data.get_last_error()) )
            return
        self.tabs.clearchanges(index)


    def _process_save_target(self,note,saveas=False,callback=None):
        '''Select file name for saving. Calls Tk save dialog.'''
        dprint(3, "\nTkMemobook::_process_save_target:: Note title is " + note.title + ", saveas=" + str(saveas) + ". " )
        if note is None:
            return 1
        if (note.ID == "") or saveas:
            try:
                if note.ID == "":
                    if not self.data.get_active_save():
                        name = filedialog.asksaveasfilename(initialdir=self.data.get_active_base(),
                                                            title="Save file as...")
                    else:
                        name = filedialog.asksaveasfilename(initialdir=self.data.get_active_save(),
                                                            title="Save file as...")
                else:
                    temp_dir = os.path.dirname(note.ID)
                    name = filedialog.asksaveasfilename(initialdir=temp_dir,
                                                        title="Save file as...")
                if name:
                    if isinstance(name, str) and name == "":
                        return -1
                    if isinstance(name, tuple) and name == ():
                        return -1
                    self.data.set_active_save(os.path.dirname(name))
                else:
                    return -1
                note.ID = name
                note.title = os.path.basename(name)
            except Exception as e:
                dprint(2, "Exception raised during processing of file name and saving: " + str(e))
                return 1
            else:
                if callback:
                    dprint(3, "Calling callback function. ")
                    callback(note.title)
                return 0
        else:
            return 0


    def close_page(self):
        '''Close current note/tab'''
        dprint(3, "\nTkMemobook::close_page:: ")
        current = self.tabs.index("current")
        if self.tabs.changed(current):
            finish_nt = self.tabs.getnoteref(current)
            title = str(finish_nt.title)
            if title == "":
                title = self.tabs.tab(current, option="text")
            ans = messagebox.askyesnocancel(title="Save changes?",
                                            message="Save changes before closing " + title  + "?",
                                            default=messagebox.YES)
            if ans is None:
                return -1
            if not ans:
                self.tabs.removepage(current)
                return 0
            if self._process_save_target(finish_nt) > 0:
                err_ans = messagebox.askyesno(title="Save error",
                                              message="Error encountered while preparing save file. Close anyway?",
                                              default=messagebox.NO )
                if err_ans:
                    self.tabs.removepage(current)
                    return 1
                return -1
            if finish_nt.ID == "":
                return -1
            to_be_written = self.tabs.removepage(current)
            if self.data.save_note(to_be_written):
                err_ans = messagebox.askyesno(title="Save error",
                                              message="Error encountered while saving file: " + str(self.data.get_last_error()) + "\nClose anyway?",
                                              default=messagebox.NO )
                if not err_ans:
                    self.tabs.newpage(to_be_written)
                    return 0
                return -1
            return 0
        else:
            self.tabs.removepage(current)
            return 1
    
    
    def close_all(self):
        '''Close all notes/tabs'''
        dprint(3, "\nTkMemobook::close_all:: ")
        for tb in self.tabs.tabs():
            i = self.tabs.index(tb)
            self.tabs.select(i)
            if self.tabs.changed(i):
                ret_int = self.close_page()
                if ret_int and ret_int < 0:
                    return
            else:
                self.__close_page()
            
            
    def exit_all(self, e):
        '''Exit: Close all notes/tabs and exit.'''
        dprint(3, "\nTkMemobook::exit_all:: ")
        for tb in self.tabs.tabs():
            i = self.tabs.index(tb)
            self.tabs.select(i)
            if self.tabs.changed(i):
                ret_int = self.close_page()
                if ret_int and ret_int < 0:
                    return
            else:
                self.close_page()
        self.ctrl["x"] = str(self.root.winfo_width() - self.offset[0])
        #I found a mysterious increase in window size, countered it by subtracting an additional amount in the following:
        self.ctrl["y"] = str(self.root.winfo_height() - self.offset[1] - 19) 
        Memobook.exit_all(self, e)
        self.root.destroy()
        

    def font_dialogue(self):
        '''Font selection: dialogue for font choices'''
        dprint(3, "\nTkMemobook::font_dialogue:: ")
        def set_string_variable(var, val):
            var.set(val)
        def set_font(getter, fam, sz, wt):
            self.ctrl["font"]["family"] = fam
            self.ctrl["font"]["size"] = sz
            self.ctrl["font"]["weight"] = wt
            self.tabs.set_page_font(fam, sz, wt)
            getter.destroy()
        getter = Toplevel(self.root)
        getter.title("Font selection")
        family_str = StringVar(getter)
        family_str.set(self.ctrl["font"]["family"])
        size_str = StringVar(getter)
        size_str.set(self.ctrl["font"]["size"])
        weight_str = StringVar(getter)
        weight_str.set(self.ctrl["font"]["weight"])
        possible_fams = list(font.families(root=self.root))
        possible_fams.sort(key=lambda x: x[0])
        display_frame = Frame(getter)
        instr_frame = Frame(display_frame)
        instr_instr = Label(instr_frame,
                            text="Please select a font:")
        instr_examp = Label(instr_frame,
                            text=family_str.get(),
                            font=(family_str.get(),12,"normal"))
        family_str.trace_add("write",
                             lambda x,y,z: instr_examp.config(text=family_str.get(),
                                                              font=(family_str.get(),
                                                                    12,
                                                                    weight_str.get())))
        weight_str.trace_add("write",
                             lambda x,y,z: instr_examp.config(text=family_str.get(),
                                                              font=(family_str.get(),
                                                                    12,
                                                                    weight_str.get())))
        label_frame = Frame(display_frame)
        label_family = Label(label_frame,text="Family:")
        label_size = Label(label_frame,text="Size:")
        label_weight = Label(label_frame,text="Weight:")
        choice_frame = Frame(display_frame)
        choice_family = Combobox(choice_frame,
                                 textvariable=family_str,
                                 values=possible_fams)
        choice_size = Combobox(choice_frame,
                               textvariable=size_str,
                               values=(6,8,10,12,14,16,18,20,24,28,32,48,64,72),
                               postcommand=lambda: set_string_variable(size_str,
                                                                       self.ctrl["font"]["size"]))
        choice_weight = Combobox(choice_frame,
                                 textvariable=weight_str,
                                 values=("normal","bold","italic"))
        finish_frame = Frame(getter)
        finish_cancel = Button(finish_frame,
                               text="Cancel",
                               command=lambda: getter.destroy())
        finish_apply = Button(finish_frame,
                              text="Apply",
                              command=lambda: set_font(getter,
                                                       family_str.get(),
                                                       size_str.get(),
                                                       weight_str.get()))
        instr_instr.pack(side="top", anchor="w")
        instr_examp.pack(side="bottom", anchor="w")
        instr_frame.pack()
        label_family.pack(anchor="w")
        label_size.pack(anchor="w")
        label_weight.pack(anchor="w")
        label_frame.pack(side="left")
        choice_family.pack(anchor="w", fill="x", expand="true")
        choice_size.pack(anchor="w", fill="x", expand="true")
        choice_weight.pack(anchor="w", fill="x", expand="true")
        choice_frame.pack(side="left", expand="true", fill="x")
        display_frame.pack(side="top", expand="true", fill="both")
        finish_cancel.pack(side="left")
        finish_apply.pack(side="right")
        finish_frame.pack(side="bottom")


    def mark_dialogue(self):
        '''Select mark to be added to note from list of current marks'''
        def add_to_dest(listbox1,listitems,var="", listbox2=None):
            # subfunction for adding items to the pending list of marks [silent or open]
            if listbox2 and (var in ("VIS", "INVIS")):
                if var == "VIS":
                    for item in listitems:
                        listbox1.insert(END, item)
                else:
                    for item in listitems:
                        listbox2.insert(END, item)
            else:
                for item in listitems:
                    listbox1.insert(END, item)
        def rem_from_dest(listbox):
            # subfunction for removing items from the pending list of marks
            orderlist = list(listbox.curselection())
            orderlist.sort(reverse=True)
            for index in orderlist:
                listbox.delete(index)
        def process_dest(win, listbox1, listbox2=None):
            # assert pending list of marks to memobook
            self.tabs.writetocurrent(listbox1.get(0, END))
            if listbox2:
                self.data.update(focus, listbox2.get(0, END))
            else:
                self.data.update(focus, listbox1.get(0, END))
            win.destroy()
        def default_selection(var):
            # subfunction to set default silent/open
            var.set("VIS")
        dprint(3, "\nTkMemobook::mark_dialogue:: ")
        getter = None
        try:
            focus = self.tabs.getnoteref(self.tabs.index("current"))
        except TclError:
            dprint(1, "Error in fetching current tab from .tabs.")
            messagebox.showinfo("Edit Marks Error:",
                                "A tab must be opened before marks can be managed.")
            return
        else:
            getter = Toplevel(self.root)
            title_string = "Manage marks for "
            if len(focus.title) > 32:
                title_string += focus.title[:32] + "..."
            else:
                title_string += focus.title
            getter.title(title_string)
            top_frame = Frame(getter)
        top_left_frame = Frame(top_frame)
        top_left_label = Label(top_left_frame,
                               text="Marks from open notes:")
        top_left_getter = ListboxHV(top_left_frame,
                                    height=12,
                                    width=27,
                                    selectmode="multiple")
        getter_items = self.tabs.marks()
        getter_items.sort()
        for item in getter_items:
            top_left_getter.insert(END, item)
        top_right_frame = Frame(top_frame)
        top_cent_frame = Frame(top_frame)
        bottom_frame = Frame(getter)
        bottom_middle_frame = Frame(bottom_frame)
        bottom_middle_label = Label(bottom_middle_frame,
                                    text="Additional marks:")
        bottom_middle_enter = Entry(bottom_middle_frame,
                                    width=24)
        bottom_bottom_frame = Frame(bottom_frame)
        bottom_bottom_cancel = Button(bottom_bottom_frame,
                                      text="Cancel",
                                      command=lambda: getter.destroy())
        top_left_label.pack(side="top", anchor="n")
        top_left_getter.pack(side="bottom", anchor="w", expand="true", fill="both")
        top_left_frame.pack(side="left", expand="true", fill="both")            
        if focus.mime == NoteMime.TEXT:
            top_right_vis_label = Label(top_right_frame,
                                        text="Store in text (append to end):")
            top_right_vis_dest = ListboxHV(top_right_frame,
                                           height=5,
                                           width=27,
                                           selectmode="multiple")
            top_right_invis_label = Label(top_right_frame,
                                          text="All hidden (not stored in text):")
            top_right_invis_dest = ListboxHV(top_right_frame,
                                             height=5,
                                             width=27,
                                             selectmode="multiple")
            if focus.tags:
                if focus.tags.silent:
                    for st in focus.tags.silent:
                        top_right_invis_dest.insert(END, st)
            top_cent_add_vis = Button(top_cent_frame,
                                      text="→",
                                      command=lambda:add_to_dest(top_right_vis_dest,
                                                                 [getter_items[j] for j in top_left_getter.curselection()]))
            top_cent_remove_vis = Button(top_cent_frame,
                                         text="X",
                                         command=lambda:rem_from_dest(top_right_vis_dest))
            top_cent_upperspacer = Label(top_cent_frame,
                                         text="\n\n")
            top_cent_add_invis = Button(top_cent_frame,
                                        text="→",
                                        command=lambda:add_to_dest(top_right_invis_dest,
                                                                   [getter_items[j] for j in top_left_getter.curselection()]))
            top_cent_remove_invis = Button(top_cent_frame,
                                           text="X",
                                           command=lambda:rem_from_dest(top_right_invis_dest))
            storage_variable = StringVar(bottom_middle_frame)
            storage_variable.set("VIS")
            bottom_middle_radio_VIS = Radiobutton(bottom_middle_frame,
                                                  text="Visible",
                                                  variable=storage_variable,
                                                  command=lambda: default_selection(storage_variable),  # get tk to give default selection
                                                  value="VIS")
            bottom_middle_radio_INVIS = Radiobutton(bottom_middle_frame,
                                                    text="Hidden",
                                                    variable=storage_variable,
                                                    value="INVIS")
            bottom_middle_add = Button(bottom_middle_frame,
                                       text="↑",
                                       command=lambda:add_to_dest(top_right_vis_dest,
                                                                  parse.split_by_unknown(bottom_middle_enter.get()),
                                                                  storage_variable.get(),
                                                                  top_right_invis_dest))
            bottom_bottom_apply = Button(bottom_bottom_frame,
                                         text="Apply",
                                         command=lambda:process_dest(getter,top_right_vis_dest,top_right_invis_dest))
            top_cent_remove_invis.pack(side="bottom")
            top_cent_add_invis.pack(side="bottom")
            top_cent_upperspacer.pack(side="bottom")
            top_cent_remove_vis.pack(side="bottom")
            top_cent_add_vis.pack(side="bottom")
            top_right_vis_label.pack(side="top", anchor="n")
            top_right_vis_dest.pack(side="top", anchor="w", fill="both", expand="true")
            top_right_invis_label.pack(side="top", anchor="n")
            top_right_invis_dest.pack(side="top", anchor="w", fill="both", expand="true")
            bottom_middle_label.pack(side="left", anchor="w")
            bottom_middle_enter.pack(side="left", anchor="w", fill="x", expand="true")
            bottom_middle_radio_VIS.pack(side="left", anchor="w")
            bottom_middle_radio_INVIS.pack(side="left", anchor="w")
            bottom_middle_add.pack(side="right", anchor="w")
        else:
            top_right_invis_label = Label(top_right_frame,
                                          text="Hidden and stored outside of text:")
            top_right_invis_dest = ListboxHV(top_right_frame,
                                             height=12,
                                             width=27,                                             
                                             selectmode="multiple")
            if focus.tags:
                for t in focus.tags:
                    top_right_invis_dest.insert(END, t)
            top_cent_add_invis = Button(top_cent_frame,
                                        text="→",
                                        command=lambda:add_to_dest(top_right_invis_dest,
                                                                   [getter_items[j] for j in top_left_getter.curselection()]))
            top_cent_remove_invis = Button(top_cent_frame,
                                           text="X",
                                           command=lambda:rem_from_dest(top_right_invis_dest))
            bottom_middle_add = Button(bottom_middle_frame,
                                       text="↑",
                                       command=lambda:add_to_dest(top_right_invis_dest,
                                                                  parse.split_by_unknown(bottom_middle_enter.get())))
            bottom_bottom_apply = Button(bottom_bottom_frame,
                                         text="Apply",
                                         command=lambda:process_dest(getter, top_right_invis_dest))
            top_cent_remove_invis.pack(side="bottom")
            top_cent_add_invis.pack(side="bottom")
            top_right_invis_label.pack(side="top", anchor="n")
            top_right_invis_dest.pack(side="top", anchor="w", fill="both", expand="true")
            bottom_middle_label.pack(side="left", anchor="w")
            bottom_middle_enter.pack(side="left", anchor="w", fill="x", expand="true")
            bottom_middle_add.pack(side="right", anchor="w")
        top_cent_frame.pack(side="left")
        top_right_frame.pack(side="left", fill="both", expand="true")
        top_frame.pack(side="top",fill="both",expand="true")
        bottom_bottom_apply.pack(side="left")
        bottom_bottom_cancel.pack(side="right")
        bottom_bottom_frame.pack(side="bottom")
        bottom_middle_frame.pack(side="bottom", anchor="w", fill="x", expand="true")
        bottom_frame.pack(side="bottom", fill="x", expand="true")


    def open_pop(self, hook_remove, hook_add, hook_apply):
        '''Manage bookmark sources: Major dialogue'''
        dprint(3, "\nTkMemobook::open_pop:: ")
        manager = Toplevel(self.root)
        manager_list = ListboxHV(manager, selectmode="multiple")
        manager_items = self.ctrl["db"]["scan"]
        if isinstance(manager_items, str):
            manager_items = [ manager_items ]
        else:
            manager_items = list(manager_items)
        manager_items.sort()
        for item in manager_items:
            manager_list.insert(END, item)
        manager_list.grid_columnconfigure(0, weight=1)
        manager_list.grid_rowconfigure(0, weight=1)
        manager_list.grid(sticky="nswe")
        buttons = Frame(manager)
        rembutt = Button(buttons,
                         text="Remove",
                         command=lambda: hook_remove(manager_list, manager_items) )
        addbutt = Button(buttons,
                         text="Add Other...",
                         command=lambda: hook_add(manager, manager_list, manager_items) )
        appbutt = Button(buttons,
                         text="Apply",
                         command=lambda: self.__get_busy_with(None, hook_apply, manager, manager_items) )
        rembutt.grid(row=1, column=0)
        addbutt.grid(row=1, column=1)
        appbutt.grid(row=1, column=2)
        buttons.grid_columnconfigure(1, weight=1)
        buttons.grid_rowconfigure(1, weight=1)
        buttons.grid(stick="nswe")
        manager.grid_columnconfigure(0, weight=1)
        manager.grid_rowconfigure(0, weight=1)

    
    def __open_pop_add(self, win, manlist, manitems):
        '''Manage bookmark sourse: add directory. Calls Tk file dialogue.'''
        dprint(3, "\nTkMemobook::__open_pop_add:: ")
        if manitems:
            new_dir = filedialog.askdirectory(initialdir=manitems[0],
                                              title="Choose a scan directory",
                                              parent=win )
        else:
            new_dir = filedialog.askdirectory(initialdir=self.ctrl["loc"],
                                              title="Choose a scan directory",
                                              parent=win )
        if new_dir:
            manitems.append(new_dir)
            manlist.insert(END, str(new_dir))

        
    def __open_pop_remove(self, manlist, manitems):
        '''Manage sources: remove directory.'''
        dprint(3, "\nTkMemobook::__open_pop_remove:: ")
        index_list = list(manlist.curselection())
        index_list.sort(reverse=True)
        for index in index_list:
            manitems.pop(index)
            manlist.delete(index)

        
    def __open_pop_apply(self, win, new_scan):
        '''Manage sources: apply changes to memobook and config object'''
        dprint(3, "\nTkMemobook::__open_pop_apply:: ")
        self.data.clear()
        if new_scan:
            self.ctrl["db"]["scan"] = list(new_scan)
        else:
            self.ctrl["db"]["scan"] = "."
        self.data.populate()
        win.destroy()


    def __get_busy_with(self, optionalwin, fctn, *args):
        '''Wrapper to invoke mouse busy icon'''
        ### Example of use: for a call, buff = f(arg1,arg2,arg3), use
        ### buff = self.__get_busy_with(f,arg1,arg2,arg3)
        ### The choice was made not to recursively propagate through self.root
        ### and its descendants: this seems overly broad and might involve
        ### propagation through too many (out-of-view) tabs or, worse, might not
        ### reach the visible tab at all. The biggest negative is that if the
        ### UI is drastically changed, this function must be tailored to those changes.
        dprint(3, "\nMemobook::__get_busy_with:: ")
        self.root.config(cursor="watch")
        self.root.update()
        self.menu.config(cursor="watch")
        self.menu.update()
        self.tabs.config(cursor="watch")
        self.tabs.update()
        if optionalwin:
            optionalwin.config(cursor="watch")
            optionalwin.update()
        # the following logic avoids the exception thrown when the current index
        # is requested but there are no tabs.
        if self.tabs.tabs():
            i = self.tabs.index("current")
        else:
            i = -1
        if i >= 0:
            self.tabs.getpageref(i).plate.config(cursor="watch")
            self.tabs.getpageref(i).plate.update()
        retval = fctn(*args)
        self.root.config(cursor="")
        self.menu.config(cursor="")
        self.tabs.config(cursor="")
        if optionalwin:
            optionalwin.config(cursor="")
        if i >= 0:
            self.tabs.getpageref(i).plate.config(cursor="")
        return retval
