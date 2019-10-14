'''Memobook class file: the frontend and control structure for the application.
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
from memo.book import Book
import memo.extconf as extconf
import memo.parse as parse
from memo.hscroll import ListboxHV
from memo.binding import FileBinding, DatabaseBinding
from memo.note import NoteMime





class Heading(enum.Enum):

    '''Menu headings'''

    MF = 'File'
    ME = 'Edit'
    MS = 'Sources'
    MH = 'Help'


    

class Memobook:

    '''Memobook frontend'''

    root = None
    tabs = None
    menu = None
    offset = []
    ctrl = None
    data = None
    index = None
    

    def __init__(self,**kwargs):
        if "ctrl" in kwargs.keys():
            try:
                self.ctrl = extconf.load_file(kwargs["ctrl"])
            except Exception as e:
                print("Error loading or preparing memobook: " + str(e))
                return
            else:
                working_loc = str(os.path.dirname(kwargs["ctrl"]))
                if working_loc == '':
                    self.ctrl["loc"] = '.'
                else:
                    self.ctrl["loc"] = working_loc
        if not "scan" in self.ctrl["db"].keys() :
            self.ctrl["db"]["scan"] = "."
        if "data" in kwargs.keys():
            self.data = kwargs["data"]
        else:
            self.data = DatabaseBinding(self.ctrl)
            exc = self.data.get_last_error()
            if exc:
                messagebox.showinfo( "Data error","Unable to open data source: " + str(exc) )
                self.data = FileBinding(self.ctrl)
        if "index" in kwargs.keys():
            try:
                self.index = extconf.load_file(kwargs["index"])
            except Exception as e:
                print("Error loading non-text index: " + str(e))
            else:
                index_loc = str(os.path.dirname(kwargs["index"]))
                if index_loc == '':
                    self.ctrl["index"] = '.'
                else:
                    self.ctrl["index"] = index_loc
                self.data.set_index(self.index)
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
            self.tabs = Book(self.root,ruling=self.ctrl,width=self.ctrl["x"],height=self.ctrl["y"])
            #self.tabs.ruling(self.ctrl)  #if ruling is not specified in constructor call, it must be done so here
            self.tabs.set_save_hook(lambda:self.__save_note())
            self.tabs.set_close_hook(lambda:self.__close_page())
            self.tabs.bind("<Double-Button-1>",lambda e: self.tabs.newpage(None))
        self.menu = Menu(self.root)
        self.__set_bindings()
        self.tabs.grid_columnconfigure(0,weight=1)
        self.tabs.grid_rowconfigure(0,weight=1)
        self.tabs.grid(sticky="nswe")
        self.__populate_menus()
        self.root.config(menu=self.menu)
        self.root.grid_columnconfigure(0,weight=1)
        self.root.grid_rowconfigure(0,weight=1)
        self.offset = [ self.tabs.winfo_reqwidth()-int(self.ctrl["x"]),
                        self.tabs.winfo_reqheight()-int(self.ctrl["y"]) ]
        #style = Style()
        #style.configure(".",
        #                font=(self.ctrl["style"]["font"]["family"],
        #                      self.ctrl["style"]["font"]["size"],
        #                      self.ctrl["style"]["font"]["weight"],))


    def __populate_menus( self ):
        mdict = { Heading.MF:Menu(self.menu,tearoff=0),
                  Heading.ME:Menu(self.menu,tearoff=0),
                  Heading.MS:Menu(self.menu,tearoff=0),
                  Heading.MH:Menu(self.menu,tearoff=0) }
        for k in mdict:
            self.menu.add_cascade(label=k.value,menu=mdict[k])
        mdict[Heading.MF].add_command(label="New",
                                      command=lambda: self.tabs.newpage(None))
        mdict[Heading.MF].add_command(label="Open by mark",
                                      command=lambda: self.open_mark(self.__open_mark_open))
        mdict[Heading.MF].add_command(label="Open from file",
                                      command=lambda: self.open_file())
        mdict[Heading.MF].add_command(label="Save",
                                      command=lambda: self.__save_note())
        mdict[Heading.MF].add_command(label="Save as",
                                      command=lambda: self.__save_note_as())
        mdict[Heading.MF].add_separator()
        mdict[Heading.MF].add_command(label="New tab",
                                      command=lambda: self.tabs.newpage(None))
        mdict[Heading.MF].add_command(label="Close tab",
                                      command=lambda: self.__close_page())
        mdict[Heading.MF].add_command(label="Close all tabs",
                                      command=lambda: self.__close_all())
        mdict[Heading.MF].add_separator()
        mdict[Heading.MF].add_command(label="Quit",
                                      command=lambda: self.exit_all(None))
        mdict[Heading.ME].add_command(label="Insert mark",
                                      command=lambda: self.__mark_dialogue(self.__mark_store))
        mdict[Heading.ME].add_separator()
        mdict[Heading.ME].add_command(label="Font",
                                      command=lambda: self.__font_dialogue())
        mdict[Heading.ME].add_separator()
        mdict[Heading.ME].add_command(label="Toggle tab wrap",
                                      command=lambda: self.tabs.togglewrap())
        mdict[Heading.ME].add_checkbutton(label="Toggle global wrap",
                                          onvalue="word",
                                          offvalue="none",
                                          variable=self.ctrl["wrap"],
                                          command=lambda: self.tabs.togglewrapall())
        mdict[Heading.MS].add_command(label="Scan",
                                      command=lambda: self.data.populate())
        mdict[Heading.MS].add_command(label="Manage locations",
                                      command=lambda: self.__open_pop(self.__open_pop_remove,
                                                                     self.__open_pop_add,
                                                                     self.__open_pop_apply))
        mdict[Heading.MH].add_command(label="About",
                                      command=lambda: self.__publication_info())


    def __set_bindings( self ):  # binding functions to keystrokes
        self.root.protocol("WM_DELETE_WINDOW",lambda: self.exit_all(None))
        self.root.bind("<Control-q>",lambda e: self.exit_all(None))
        self.root.bind("<Control-w>",lambda e: self.__close_page())
        self.root.bind("<Control-n>",lambda e: self.tabs.newpage(None))
        self.root.bind("<Control-s>",lambda e: self.__save_note())
        self.root.bind("<Alt-m>",lambda e: self.__mark_dialogue(self.__mark_store))


    def open_mark( self, callback ):  # open by mark
        ### despite using select, invoke, focus_set, event_generate,
        ### tk wouldn't set the OR radiobutton as default.
        ### So the following sub-function is a workaround to force the issue.
        def default_selection(var):
            var.set("or")
        toc = list(self.data.toc())
        #toc.sort(key=lambda x: x[0]) #toc doesn't return a tuple of tuples, but a tuple of strings
        toc.sort(key=lambda x: x.lower())
        getter = Toplevel(self.root)
        getter_list = ListboxHV(getter,selectmode="multiple")
        for item in toc:
            getter_list.insert(END,item)
        getter_list.pack(fill="both",expand="true")
        button_frame = Frame(getter)
        logic_variable = StringVar(None,"or")
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
                         command=lambda: callback(getter,
                                                  [ toc[int(j)] for j in getter_list.curselection() ],
                                                  logic_variable.get()))
        radiobutt_OR.pack(side="left")
        radiobutt_AND.pack(side="left")
        retbutt.pack(side="left")
        button_frame.pack(side="bottom")
        radiobutt_OR.invoke()

        
    def __open_mark_open( self,win,ls,logic ):  # callback function for open_mark
        if ls:
            if logic == "or":
                notes = self.data.open_from_toc(ls)
            elif logic == "and":
                notes = self.data.open_from_toc_intersection(ls)
            else:
                notes = []
            if not notes:
                last = self.data.get_last_error()
                if last:
                    messagebox.showinfo("Open error",
                                    "Unable to open file(s): " + str(self.data.get_last_error()))
                else:
                    failure = ", ".join(ls)
                    if logic == "or":
                        messagebox.showinfo("Open failure",
                                            "Unable to find files for any of the following marks: " + failure)
                    else:
                        messagebox.showinfo("Open failure",
                                            "Unable to find files containing each of the following marks: " + failure)
            else:
                for note in notes:
                    self.tabs.newpage(note)
        win.destroy()


    def __build_file_types(self):
        prep_list = []
        for filetype in self.ctrl["mime"]:
            tmp_list = None
            if isinstance(self.ctrl["mime"][filetype]["suff"],str):
                tmp_tuple = ( str(filetype + " files"), str("*" + self.ctrl["mime"][filetype]["suff"]) )
            else:
                tmp_type = [ str("*"+t) for t in self.ctrl["mime"][filetype]["suff"] ]
                tmp_tuple = ( str(filetype + " files") , tuple(tmp_type) )
            prep_list.append( tmp_tuple )
        prep_list.append(("All files", "*.*"))
        return tuple(prep_list)

    
    def open_file( self ):  # open by file name
        active_dir = self.data.get_active_open()
        if not active_dir:
            file_names = filedialog.askopenfilenames(initialdir=self.data.active_base(),
                                                     title="Choose file(s) to open",
                                                     filetypes=self.__build_file_types())
        else:
            file_names = filedialog.askopenfilenames(initialdir=active_dir,
                                                     title="Choose file(s) to open",
                                                     filetypes=self.__build_file_types())
        if file_names:
            self.data.set_active_open(os.path.dirname(file_names[0]))
            list_of_notes = self.data.open_note(file_names)
            for nt in list_of_notes:
                self.tabs.newpage(nt)


    def __save_note( self ):
        index = self.tabs.index("current")
        if self.tabs.changed(index) is False:
            return
        save_nt = self.tabs.getnoteref(index)
        save_nt.body = self.tabs.getpageref(index).plate.get("1.0","end-1c")
        ret_val = self.__process_save_target(save_nt,
                                             callback=lambda c:self.tabs.tab(index,text=c))
        if ( ret_val > 0 ):
            messagebox.showinfo("Save target error",
                                "Unable to process save target")
            return
        if ( ret_val < 0 ) or save_nt.ID == "":
            return
        if self.data.save_note(save_nt) :
            messagebox.showinfo("Save error",
                                "Unable to save note: " + str(self.data.get_last_error()) )
            return
        self.tabs.clearchanges(index)


    def __save_note_as( self ):
        index = self.tabs.index("current")
        save_nt = self.tabs.getnoteref(index)
        save_nt.body = self.tabs.getpageref(index).dump()
        if not save_nt.body:
            return
        ret_targ = self.__process_save_target(save_nt,
                                              saveas=True,
                                              callback=lambda c:self.tabs.tab(index,text=c))
        if ( ret_targ > 0 ):
            messagebox.showinfo("Save target error",
                                "Unable to process save target")
            return
        if ( ret_targ < 0 ):
            return
        if ( self.data.save_note(save_nt) ):
            messagebox.showinfo("Save error",
                                "Unable to save note: " + str(self.data.get_last_error()) )
            return
        self.tabs.clearchanges(index)


    def __process_save_target(self,note,saveas=False,callback=None):  # select file name for saving
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
                    if isinstance(name,str) and name == "":
                        return -1
                    if isinstance(name,tuple) and name == ():
                        return -1
                    self.data.set_active_save(os.path.dirname(name))
                else:
                    return -1
                note.ID = name
                note.title = os.path.basename(name)
            except Exception as e:
                return 1
            else:
                if callback:
                    callback(note.title)
                return 0
        else:
            return 0


    def __close_page( self ):
        current = self.tabs.index("current")
        if self.tabs.changed(current):
            finish_nt = self.tabs.getnoteref(current)
            title = str(finish_nt.title)
            if title == "":
                title = self.tabs.tab(current,option="text")
            ans = messagebox.askyesnocancel(title="Save changes?",
                                            message="Save changes before closing " + title  + "?",
                                            default=messagebox.YES)
            if ans is None:
                return -1
            if not ans:
                self.tabs.removepage(current)
                return 0
            if self.__process_save_target(finish_nt) > 0:
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
    
    
    def __close_all( self ):
        for tb in self.tabs.tabs():
            i = self.tabs.index(tb)
            self.tabs.select(i)
            if self.tabs.changed(i):
                ret_int = self.__close_page()
                if ret_int and ret_int < 0:
                    return
            else:
                self.__close_page()
            
            
    def exit_all( self,e ):
        for tb in self.tabs.tabs():
            i = self.tabs.index(tb)
            self.tabs.select(i)
            if self.tabs.changed(i):
                ret_int = self.__close_page()
                if ret_int and ret_int < 0:
                    return
            else:
                self.__close_page()
        self.ctrl["x"] = str(self.root.winfo_width()-self.offset[0])
        self.ctrl["y"] = str(self.root.winfo_height()-self.offset[1] - 19)
        self.ctrl.print_config(str(self.ctrl["loc"]+os.sep+"conf.xml"))
        if isinstance(self.index,extconf.Configuration):
            self.index.print_config(str(self.ctrl["index"]+os.sep+"index.xml"))
        self.root.destroy()


    def __font_dialogue( self ):
        def set_string_variable(var,val):
            var.set(val)
        def set_font(getter,fam,sz,wt):
            self.ctrl["font"]["family"]=fam
            self.ctrl["font"]["size"]=sz
            self.ctrl["font"]["weight"]=wt
            self.tabs.set_page_font(fam,sz,wt)
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
        instr_instr.pack(side="top",anchor="w")
        instr_examp.pack(side="bottom",anchor="w")
        instr_frame.pack()
        label_family.pack(anchor="w")
        label_size.pack(anchor="w")
        label_weight.pack(anchor="w")
        label_frame.pack(side="left")
        choice_family.pack(anchor="w")
        choice_size.pack(anchor="w")
        choice_weight.pack(anchor="w")
        choice_frame.pack(side="left")
        display_frame.pack(side="top")
        finish_cancel.pack(side="left")
        finish_apply.pack(side="right")
        finish_frame.pack(side="bottom")


    def __mark_dialogue( self,callback ):  # select mark to be added to note from list of current marks
        def add_to_dest(listbox,listitems):
            for item in listitems:
                listbox.insert(END,item)
        def rem_from_dest(listbox):
            orderlist = list(listbox.curselection())
            orderlist.sort(reverse=True)
            for index in orderlist:
                listbox.delete(index)
        def process_dest(win,listbox):
            destlist = listbox.get(0,END)
            self.__mark_update_index(win,
                                     #[destlist[j] for j in map(int,listbox.curselection())],
                                     destlist,
                                     self.tabs.getnoteref(self.tabs.index("current")))
        getter = Toplevel(self.root)
        focus = self.tabs.getnoteref(self.tabs.index("current")) 
        if focus.mime == NoteMime.TEXT:
            getter_list = ListboxHV(getter,selectmode="multiple")
            getter_items = self.tabs.marks()
            getter_items.sort()
            for item in getter_items:
                getter_list.insert(END,item)
            getter_list.pack()
            retbutt = Button(getter,
                             text="Apply",
                             command=lambda: callback(getter,
                                                      [getter_items[j] for j in getter_list.curselection()]) )
            retbutt.pack()
        else:
            top_frame = Frame(getter)
            top_left_frame = Frame(top_frame)
            top_left_label = Label(top_left_frame,
                                   text="Marks from open notes:")
            top_left_getter = ListboxHV(top_left_frame,
                                        selectmode="multiple")
            getter_items = self.tabs.marks()
            getter_items.sort()
            for item in getter_items:
                top_left_getter.insert(END,item)
            top_right_frame = Frame(top_frame)
            top_right_label = Label(top_right_frame,
                                    text="Marks to be stored:")
            top_right_dest = ListboxHV(top_right_frame,
                                       selectmode="multiple")
            if focus.tags:
                for t in focus.tags:
                    top_right_dest.insert(END,t)
            top_cent_frame = Frame(top_frame)
            top_cent_add = Button(top_cent_frame,
                                  text="→",
                                  command=lambda:add_to_dest(top_right_dest,
                                                             [getter_items[j] for j in top_left_getter.curselection()]))
            top_cent_remove = Button(top_cent_frame,
                                     text="X",
                                     command=lambda:rem_from_dest(top_right_dest))
            bottom_frame = Frame(getter)
            bottom_middle_frame = Frame(bottom_frame)
            bottom_middle_label = Label(bottom_middle_frame,
                                 text="Additional marks:")
            bottom_middle_enter = Entry(bottom_middle_frame,
                                        width=24)
            bottom_middle_add = Button(bottom_middle_frame,
                                text="↑",
                                command=lambda:add_to_dest(top_right_dest,
                                                           parse.split_by_unknown(bottom_middle_enter.get())))
            bottom_bottom_frame = Frame(bottom_frame)
            bottom_bottom_apply = Button(bottom_bottom_frame,
                                  text="Apply",
                                         command=lambda:process_dest(getter,top_right_dest))
            bottom_bottom_cancel = Button(bottom_bottom_frame,
                                          text="Cancel",
                                          command=lambda: getter.destroy())
            top_left_label.pack(side="top",anchor="n")
            top_left_getter.pack(side="bottom",anchor="w")
            top_left_frame.pack(side="left")
            top_cent_remove.pack(side="bottom")
            top_cent_add.pack(side="bottom")
            top_cent_frame.pack(side="left")
            top_right_label.pack(side="top",anchor="n")
            top_right_dest.pack(side="left",anchor="w")
            top_right_frame.pack(side="left")
            top_frame.pack(side="top")
            bottom_bottom_apply.pack(side="left")
            bottom_bottom_cancel.pack(side="right")
            bottom_bottom_frame.pack(side="bottom")
            bottom_middle_label.pack(side="left",anchor="w")
            bottom_middle_enter.pack(side="left",anchor="w",fill="x",expand="true")
            bottom_middle_add.pack(side="right",anchor="w")
            bottom_middle_frame.pack(side="bottom",anchor="w")
            bottom_frame.pack(side="bottom")


    def __mark_update_index( self, win, ls, nt ):
        self.data.update(nt,ls)
        self.__mark_store(win,ls)

    
    def __mark_store( self,win,ls ):  # callback function for mark_dialogue
        self.tabs.writetocurrent(ls)
        win.destroy()


    def __open_pop( self, hook_remove, hook_add, hook_apply ):  # populate bookmark lists
        manager = Toplevel(self.root)
        manager_list = ListboxHV(manager,selectmode="multiple")
        manager_items = self.ctrl["db"]["scan"]
        if isinstance(manager_items,str):
            manager_items = [ manager_items ]
        else:
            manager_items = list(manager_items)
        manager_items.sort()
        for item in manager_items:
            manager_list.insert(END,item)
        manager_list.grid_columnconfigure(0,weight=1)
        manager_list.grid_rowconfigure(0,weight=1)
        manager_list.grid(sticky="nswe")
        buttons = Frame(manager)
        rembutt = Button(buttons,
                         text="Remove",
                         command=lambda: hook_remove(manager_list,manager_items) )
        addbutt = Button(buttons,
                         text="Add Other...",
                         command=lambda: hook_add(manager,manager_list,manager_items) )
        appbutt = Button(buttons,
                         text="Apply",
                         command=lambda: hook_apply(manager,manager_items) )
        rembutt.grid(row=1,column=0)
        addbutt.grid(row=1,column=1)
        appbutt.grid(row=1,column=2)
        buttons.grid_columnconfigure(1,weight=1)
        buttons.grid_rowconfigure(1,weight=1)
        buttons.grid(stick="nswe")
        manager.grid_columnconfigure(0,weight=1)
        manager.grid_rowconfigure(0,weight=1)

    
    def __open_pop_add( self,win,manlist,manitems ):  # populate button: add directory
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
            manlist.insert(END,str(new_dir))

        
    def __open_pop_remove( self,manlist,manitems ):  # populate button: remove directory
        index_list = list(manlist.curselection())
        index_list.sort(reverse=True)
        #for index in manlist.curselection():
        for index in index_list:
            manitems.pop(index)
            manlist.delete(index)

        
    def __open_pop_apply( self,win,new_scan ):  # populate button: apply changes
        self.data.clear()
        if new_scan:
            self.ctrl["db"]["scan"] = list(new_scan)
        else:
            self.ctrl["db"]["scan"] = "."
        self.data.populate()
        win.destroy()


    def __publication_info(self):
        pass
