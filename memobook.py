import enum
import os
import os.path
from tkinter import *
from tkinter import messagebox
from tkinter import ttk
from tkinter import filedialog
from note import Note
from notebook import NotebookPlus
import extconf
from hscroll import ListboxH,ScrolledTextH
from binding import FileBinding,DatabaseBinding





class Heading(enum.Enum):
    MF='File'
    ME='Edit'
    MM='Mark'
    MS='Sources'

    


class Memobook:

    root=None
    tabs=None
    menu=None
    offset=[]
    ctrl = None
    data = None

    
    def __init__(self,**kwargs):
        if "ctrl" in kwargs.keys():
            try:
                self.ctrl = extconf.load_file(kwargs["ctrl"])
            except Exception as e:
                print("Error loading or preparing memobook: " + str(e))
                return
        if "data" in kwargs.keys():
            self.data = kwargs["data"]
        else:
            self.data = DatabaseBinding(self.ctrl)
            exc = self.data.get_last_error()
            if exc:
                messagebox.showinfo( "Data error","Unable to open data source: " + str(exc) )
                self.data = FileBinding(self.ctrl)
        if "root" in kwargs.keys():
            self.root = kwargs["root"]
        else:
            self.root = Tk()
            self.root.title("Memobook")
        if "tabs" in kwargs.keys():
            self.tabs = kwargs["tabs"]
        else:
            self.tabs = NotebookPlus(self.root,width=self.ctrl["x"],height=self.ctrl["y"])
            self.tabs.ruling(self.ctrl)
            self.tabs.set_save_hook(lambda :self.__save_note())
            self.tabs.set_close_hook(lambda :self.__close_page())
            self.tabs.bind("<Double-Button-1>",lambda e: self.tabs.blankpage(e))
        self.menu = Menu(self.root)
        self.__set_bindings()
        self.tabs.grid_columnconfigure(0,weight=1)
        self.tabs.grid_rowconfigure(0,weight=1)
        self.tabs.grid(sticky="nswe")
        self.tabs.blankpage(None)
        self.__populate_menus()
        self.root.config(menu=self.menu)
        self.root.grid_columnconfigure(0,weight=1)
        self.root.grid_rowconfigure(0,weight=1)
        self.offset = [ self.tabs.winfo_reqwidth()-int(self.ctrl["x"]), self.tabs.winfo_reqheight()-int(self.ctrl["y"]) ]


    def __populate_menus( self ):
        mdict = { Heading.MF:Menu(self.menu,tearoff=0), Heading.ME:Menu(self.menu,tearoff=0), Heading.MM:Menu(self.menu,tearoff=0), Heading.MS:Menu(self.menu,tearoff=0) }
        for k in mdict.keys():
            self.menu.add_cascade(label=k.value,menu=mdict[k])
        mdict[Heading.MF].add_command(label="New",command=lambda :self.tabs.blankpage(None))
        mdict[Heading.MF].add_command(label="Open by mark",command=lambda :self.open_mark(self.__open_mark_open))
        mdict[Heading.MF].add_command(label="Open from file",command=lambda :self.open_file())
        mdict[Heading.MF].add_command(label="Save",command=lambda :self.__save_note())
        mdict[Heading.MF].add_command(label="Save as",command=lambda :self.__save_note_as())
        mdict[Heading.MF].add_separator()
        mdict[Heading.MF].add_command(label="New tab",command=lambda :self.tabs.blankpage(None))
        mdict[Heading.MF].add_command(label="Close tab",command=lambda :self.__close_page())
        mdict[Heading.MF].add_command(label="Close all tabs",command=lambda :self.__close_all())
        mdict[Heading.MF].add_separator()
        mdict[Heading.MF].add_command(label="Quit",command=lambda :self.exit_all(None))
        mdict[Heading.MM].add_command(label="Add mark",command=lambda :self.__mark_dialogue(self.__mark_store))
        mdict[Heading.ME].add_command(label="Toggle tab wrap",command=lambda :self.tabs.togglewrap())
        mdict[Heading.ME].add_checkbutton(label="Toggle global wrap",onvalue="word",offvalue="none",variable=self.ctrl["wrap"],command=lambda :self.__toggle_global(mdict))
        mdict[Heading.MS].add_command(label="Scan",command=lambda :self.data.populate())
        mdict[Heading.MS].add_command(label="Manage locations",command=lambda :self.__open_pop(self.__open_pop_remove,self.__open_pop_add,self.__open_pop_apply))
        return


    def __set_bindings( self ):  # binding functions to keystrokes
        self.root.protocol("WM_DELETE_WINDOW",lambda :self.exit_all(None))
        self.root.bind("<Control-q>",lambda e:self.exit_all(None))
        self.root.bind("<Control-w>",lambda e:self.__close_page())
        self.root.bind("<Control-n>",lambda e:self.tabs.blankpage(None))
        self.root.bind("<Control-s>",lambda e:self.__save_note())
        self.root.bind("<Alt-m>",lambda e: self.__mark_dialogue(mark_store))


    def open_mark( self,callback ):  # open by mark
        toc = self.data.toc()
        toc.sort(key=lambda x:x[0])
        getter = Toplevel(self.root)
        getter_list = ListboxH(getter,selectmode="multiple")
        getter_items = [ item[0] for item in toc ]
        for item in getter_items:
            getter_list.insert(END,item)
        getter_list.pack()
        retbutt = Button(getter,text="Apply",command=lambda : callback(getter,[ item for sublist in [ toc[j][1:] for j in getter_list.curselection()] for item in sublist]))
        retbutt.pack()


    def __open_mark_open( self,win,ls ):  # callback function for open_mark
        if ls:
            notes = self.data.open_note(ls)
            if not notes:
                messagebox.showinfo("Open error","Unable to open file: " + str(self.data.get_last_error()))
            for note in notes:
                self.tabs.newpage(note)
        win.destroy()


    def open_file( self ):  # open by file name
        active_dir = self.data.get_active_open()
        if not active_dir:
            file_names = filedialog.askopenfilenames(initialdir=self.data.active_base(),title="Choose file(s) to open")
        else:
            file_names = filedialog.askopenfilenames(initialdir=active_dir,title="Choose file(s) to open")
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
        save_nt.text = self.tabs.getpageref(index).txt.get("1.0","end-1c")
        ret_val = self.__process_save_target(save_nt,callback=lambda c:self.tabs.tab(index,text=c))
        if ( ret_val > 0 ):
            messagebox.showinfo("Save target error","Unable to process save target")
            return
        if ( ret_val < 0 ) or save_nt.ID=="":
            return
        if ( self.data.save_note(save_nt) ):
            messagebox.showinfo("Save error","Unable to save note: " + str(self.data.get_last_error()) )
            return
        self.tabs.clearchanges(index)
    
    
    def __save_note_as( self ):    
        index = self.tabs.index("current")
        save_nt = self.tabs.getnoteref(index)
        save_nt.text = self.tabs.getpageref(index).txt.get("1.0","end-1c")
        ret_targ = self.__process_save_target(save_nt,saveas=True,callback=lambda c:self.tabs.tab(index,text=c))
        if ( ret_targ > 0 ):
            messagebox.showinfo("Save target error","Unable to process save target")
            return
        if ( ret_targ < 0 ):
            return
        if ( self.data.save_note(save_nt) ):
            messagebox.showinfo("Save error","Unable to save note: " + str(self.data.get_last_error()) )
            return
        self.tabs.clearchanges(index)


    def __process_save_target(self,note,saveas=False,callback=None):  # select file name for saving
        if note is None:
            print("note is None")
            return 1
        if (note.ID == "") or saveas:
            try:
                if note.ID == "":
                    if not self.data.get_active_save():
                        name = filedialog.asksaveasfilename(initialdir=self.data.get_active_base(),title="Save file as...")
                    else:
                        name = filedialog.asksaveasfilename(initialdir=self.data.get_active_save(),title="Save file as...")
                else:
                    temp_dir = os.path.dirname(note.ID)
                    name = filedialog.asksaveasfilename(initialdir=temp_dir,title="Save file as...")
                if name:
                    if type(name)==str and name=="":
                        return -1
                    elif type(name)==tuple and name==():
                        return -1
                    else:
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
            name = str(finish_nt.ID)
            title = str(finish_nt.title)
            if title == "":
                title = self.tabs.tab(current,option="text")
            ans = messagebox.askyesnocancel(title="Save changes?",message="Save changes before closing " + title  + "?", default=messagebox.YES)
            if ans is None:
                return -1
            if not ans:
                self.tabs.removepage(current)
                return 0
            if ( self.__process_save_target(finish_nt)>0 ):
                err_ans = messagebox.askyesno(title="Save error",message="Error encountered while preparing save file. Close anyway?", default=messagebox.NO )
                if err_ans:
                    self.tabs.removepage(current)
                    return 1
                return -1
            if finish_nt.ID == "":
                return -1
            to_be_written = self.tabs.removepage(current)
            if ( self.data.save_note(to_be_written) ):
                err_ans = messagebox.askyesno(title="Save error",message="Error encountered while saving file: " + str(self.data.get_last_error()) + "\nClose anyway?", default=messagebox.NO )
                if not err_ans:
                    self.tabs.newpage(to_be_written)
                    return 0
                return -1
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
        self.ctrl.print_config("conf.xml")
        self.root.destroy()    


    def __mark_dialogue( self,callback ):  # select mark to be added to note from list of current marks
        getter = Toplevel(self.root)
        getter_list = Listbox(getter,selectmode="multiple")
        getter_items = self.tabs.marks()
        getter_items.sort()
        for item in getter_items:
            getter_list.insert(END,item)
        getter_list.pack()
        retbutt = Button(getter,text="Apply",command=lambda : callback(getter,[getter_items[j] for j in getter_list.curselection()]) )
        retbutt.pack()
    
    
    def __mark_store( self,win,ls ):  # callback function for mark_dialogue
        for t in ls:
            self.tabs.writetocurrent(" @@" + str(t))
        win.destroy()


    def __toggle_global( self,mdict ):
        if self.ctrl["wrap"]=="word":
            self.ctrl["wrap"]=="none"
        elif self.ctrl["wrap"]=="none":
            self.ctrl["wrap"]=="word"
        self.tabs.togglewrapall()


    def __open_pop( self, hook_remove, hook_add, hook_apply ):  # populate bookmark lists
        manager = Toplevel(self.root)
        manager_list = ListboxH(manager,selectmode="multiple")
        manager_items = self.ctrl["db"]["scan"]
        if type(manager_items) == str:
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
        rembutt = Button(buttons,text="Remove",command=lambda : hook_remove(manager_list,manager_items) )
        addbutt = Button(buttons,text="Add Other...",command=lambda : hook_add(manager,manager_list,manager_items) )
        appbutt = Button(buttons,text="Apply",command=lambda : hook_apply(manager,manager_items) )
        rembutt.grid(row=1,column=0)
        addbutt.grid(row=1,column=1)
        appbutt.grid(row=1,column=2)
        buttons.grid_columnconfigure(1,weight=1)
        buttons.grid_rowconfigure(1,weight=1)
        buttons.grid(stick="nswe")
        manager.grid_columnconfigure(0,weight=1)
        manager.grid_rowconfigure(0,weight=1)

    
    def __open_pop_add( self,win,manlist,manitems ):  # populate button: add directory
        new_dir = filedialog.askdirectory(initialdir=manitems[0],title="Choose a scan directory",parent=win )
        if new_dir:
            manitems.append(new_dir)
            manlist.insert(END,str(new_dir))

        
    def __open_pop_remove( self,manlist,manitems ):  # populate button: remove directory
        for index in manlist.curselection():
            manitems.pop(index)
            manlist.delete(index)

        
    def __open_pop_apply( self,win,new_scan ):  # populate button: apply changes
        self.data.clear()
        self.ctrl["db"]["scan"] = list(new_scan)
        self.data.populate()
        win.destroy()


