###############################################################################################
#  gmemobook.py: the Gtk GUI object for plugin use
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



'''gMemobook class file: Gtk plugin interface to Memobook.
   Configuration values are in config.py or loaded via extconf.py.
   Database is handled in binding.py.'''


import enum
import os
import os.path
import gi
try:
    gi.require_version('Gtk','3.0')
    gi.require_version('Gedit','3.0')
    from gi.repository import Gtk, GObject, Gio, Gedit, GtkSource
except:
    pass
from memo.memobook import Memobook
from memo.book import Book
import memo.parse as parse
from memo.hscroll import ListboxHV
from memo.note import NoteMime, Note, Tag
from memo.debug import dprint
from memo.binding import index_search





class StrDynamic():

    '''String Holder class for RadioButton facilitation'''

    __val = None
    def __init__(self):
        self.__val = ""
    def set(self, value):
        self.__val = value
    def get(self):
        return self.__val




class gMemobook(Memobook):

    '''Memobook Gtk plugin interface'''

    __window_hook = None
    __window = None
    __open_notes = None
    
    def __init__(self, **kwargs):
        Memobook.__init__(self, **kwargs)
        self.__window_hook = []
        self.__open_notes = []

    def add_window_hook(self, ref):
        '''Add reference to current GEdit window'''
        self.__window_hook.append(ref)
        return self.__window_hook[len(self.__window_hook)-1]

    def remove_window_hook(self, ref):
        pass

    def select_window_hook(self, ref):
        '''Set reference to window. Currently unused.'''
        self.__window = ref
        
    def open_mark(self):
        '''Open files by mark. Major dialogue.'''
        def toggler(widg, var, logic):
            # subfunction for toggling AND/OR search logic:
            if widg.get_active():
                dprint(3, "\ntoggled: " + logic)
                var.set(logic)
        dprint(3, "\ngMemobook::open_mark::")
        logic_var = StrDynamic()
        logic_var.set("or")
        [width, height] = self.__window.get_size()
        if width < 200:
            width = 300
        if height < 200:
            height = 250
        dprint(3, "size: " + str(width) + ", " + str(height))
        toc = [ item for item in self.data.toc() ]
        toc.sort(key=lambda x: x.lower())
        dprint(3, "\nIniting dialog...")
        getter = Gtk.Dialog("Open by mark",
                            None,
                            0,
                            (Gtk.STOCK_CANCEL, Gtk.ResponseType.CANCEL,
                             Gtk.STOCK_APPLY, Gtk.ResponseType.APPLY))
        getter.set_default_size(width/2, height/2)
        getter_list = Gtk.ListStore(str)
        dprint(3, "adding labels...")
        for item in toc:
            getter_list.append([item])
        getter_tree = Gtk.TreeView(getter_list)
        getter_tree_select = getter_tree.get_selection()
        getter_tree_select.set_mode(Gtk.SelectionMode.MULTIPLE)
        getter_rend = Gtk.CellRendererText()
        getter_column = Gtk.TreeViewColumn("Select marks:", getter_rend, text=0)
        getter_tree.append_column(getter_column)
        getter_view = Gtk.ScrolledWindow()
        getter_view.add(getter_tree)
        getter_view.set_policy(Gtk.PolicyType.AUTOMATIC, Gtk.PolicyType.AUTOMATIC)
        radio_label = Gtk.Label("Search logic:")
        radio_or = Gtk.RadioButton.new_with_label(None, "OR")
        radio_or.connect("toggled",lambda x: toggler(x,logic_var,"or"))
        radio_and = Gtk.RadioButton.new_with_label(None,"AND")
        radio_and.join_group(radio_or)
        radio_and.connect("toggled",lambda x: toggler(x,logic_var,"and"))
        box = getter.get_content_area()
        box.set_orientation(Gtk.Orientation.VERTICAL)
        box.add(getter_view)
        box.set_child_packing(getter_view,expand=True,fill=True,padding=0,pack_type=Gtk.PackType(0))
        subbox = Gtk.Box(orientation=Gtk.Orientation.HORIZONTAL)
        subbox.add(radio_label)
        subbox.add(radio_or)
        subbox.add(radio_and)
        subbox.set_child_packing(radio_label,expand=True,fill=True,padding=0,pack_type=Gtk.PackType(0))
        subbox.set_child_packing(radio_or,expand=True,fill=True,padding=0,pack_type=Gtk.PackType(0))
        subbox.set_child_packing(radio_and,expand=True,fill=True,padding=0,pack_type=Gtk.PackType(1))
        box.add(subbox)
        box.set_child_packing(subbox,expand=False,fill=True,padding=0,pack_type=Gtk.PackType(1))
        dprint(3,"showing...")
        getter.show_all()
        while getter.run() != Gtk.ResponseType.CANCEL:
            retvalue = self.__open_mark_confirm(None,
                                                getter,
                                                [ toc[int(j.get_indices()[0])] for j in getter_tree_select.get_selected_rows()[1] ],
                                                logic_var.get())
            if retvalue != Gtk.ResponseType.CANCEL:
                break
        getter.destroy()

            
    def __open_mark_confirm(self, widget, win, ls, logic):
        '''Open files by mark: minor dialogue for choosing among search results'''
        dprint(3, "\n__open_mark_confirm")
        dprint(3, "\n"+str(ls))
        if ls:
            if logic == "or":
                notes = self.data.open_from_toc(ls)
            else:
                notes = self.data.open_from_toc_intersection(ls)
            if not notes:
                last = self.data.get_last_error()
                if last:
                    msg = Gtk.MessageDialog(win,
                                            Gtk.DialogFlags(2),
                                            0,
                                            (Gtk.STOCK_OK, Gtk.ResponseType.OK),
                                            "Error: " + str(last))
                    
                    msg.run()
                    msg.destroy()
                    dprint(2, "\nOpen error: " + str(last))
                else:
                    failure = ", ".join(ls)
                    if logic == "or":
                        msg = Gtk.MessageDialog(win,
                                                Gtk.DialogFlags(2),
                                                0,
                                                (Gtk.STOCK_OK, Gtk.ResponseType.OK),
                                                "Unable to find files for any of the following marks: " + failure)

                        msg.run()
                        msg.destroy()
                        dprint(2, "\nOpen failure")
                    else:
                        msg = Gtk.MessageDialog(win,
                                                Gtk.DialogFlags(2),
                                                0,
                                                (Gtk.STOCK_OK, Gtk.ResponseType.OK),
                                                "Unable to find files containing each of the following marks: " + failure)
                        msg.run()
                        msg.destroy()
                        dprint(2, "Unable to find files containing each of the following marks: " + failure)
                    dprint(2, "...returning")
                    return Gtk.ResponseType.CANCEL
            else:
                for nt in notes:
                    dprint(3, nt.ID)
                confdialog = Gtk.Dialog("Confirm files to open",
                                        None,
                                        0,
                                        (Gtk.STOCK_CANCEL, Gtk.ResponseType.CANCEL,
                                         Gtk.STOCK_OPEN, Gtk.ResponseType.APPLY))
                confdialog.add_button("Open All", Gtk.ResponseType.YES)
                confdialog.set_default_size(*(win.get_size()))
                chooser_list = Gtk.ListStore(str)
                for i,nt in enumerate(notes):
                    chooser_list.append(["{:>5}{:<32}".format(str(i+1)+". ",
                                                              str(os.path.basename(nt.ID)) + "  (" + str(os.path.dirname(nt.ID)) + ")")])
                chooser_tree = Gtk.TreeView(chooser_list)
                chooser_tree_select = chooser_tree.get_selection()
                chooser_tree_select.set_mode(Gtk.SelectionMode.MULTIPLE)
                chooser_rend = Gtk.CellRendererText()
                chooser_column = Gtk.TreeViewColumn("Please select from the following:", chooser_rend,text=0)
                chooser_tree.append_column(chooser_column)
                chooser_view = Gtk.ScrolledWindow()
                chooser_view.add(chooser_tree)
                chooser_view.set_policy(Gtk.PolicyType.AUTOMATIC, Gtk.PolicyType.AUTOMATIC)
                box = confdialog.get_content_area()
                box.add(chooser_view)
                box.set_child_packing(chooser_view,
                                      expand=True,
                                      fill=True,
                                      padding=0,
                                      pack_type=Gtk.PackType(1))
                confdialog.show_all()
                value = confdialog.run()
                if (value != Gtk.ResponseType.CANCEL) and (value != Gtk.ResponseType.NONE):
                    # get each note and open a tab
                    gfilelist = None
                    if value == Gtk.ResponseType.YES:
                        gfilelist = [ Gio.file_new_for_path(nt.ID) for nt in notes ]
                        self.__open_notes += notes
                    elif value == Gtk.ResponseType.APPLY:
                        gfilelist = []
                        for j in chooser_tree_select.get_selected_rows()[1]:
                            tmp_nt = notes[j.get_indices()[0]]
                            self.__open_notes.append(tmp_nt)
                            gfilelist.append(Gio.file_new_for_path(tmp_nt.ID))
                    if gfilelist:
                        for gf in gfilelist:
                            Gedit.commands_load_location(self.__window,
                                                         gf,
                                                         None,
                                                         -1,
                                                         -1)
                confdialog.destroy()
                return value
        return Gtk.ResponseType.APPLY


    def save_note(self):
        '''Save note to disk with GEdit async save, and write marks to memobook'''
        dprint(3, "\ngMemobook::save_note::")
        doc = self.__window.get_active_document()
        Gedit.commands_save_document_async(doc,
                                           self.__window,
                                           None,
                                           lambda x,y,z: self.__save_note_hook(x,y,z),
                                           None)
        return


    def save_note_as(self):
        '''Save-as to disk with GEdit async save, and write marks to memobook'''
        dprint(3, "\ngMemobook::save_note::")
        doc = self.__window.get_active_document()
        f = doc.get_file()
        path = GtkSource.File.get_location(f).get_path()
        old_note = self.__get_note_ref(path)
        f.set_location(None)
        Gedit.commands_save_document_async(doc,
                                           self.__window,
                                           None,
                                           lambda x,y,z: self.__save_note_hook(x,y,z),
                                           old_note)
        return


    def __save_note_hook(self,obj,res,dat):
        '''Callback function for GEdit async save, as used in save_note and save_note_as'''
        dprint(3, "\nin save_note_hook...")
        result = Gedit.commands_save_document_finish(obj, res)
        dprint(3, "got result: " + str(result))
        if result == True:
            path = GtkSource.File.get_location(obj.get_file()).get_path()
            note = None
            if not dat:
                note = self.__get_note_ref(path)
                if not note:
                    note = self.__make_note_ref(obj,path)
            else:
                note = Note(dat)
                note.ID = path
            dprint(3, "...Note to be saved: " + str(note.ID))
            if self.data.save_note_nowrite(note):
                dprint(1, "\nbinding save error")
        else:
            dprint(1, "\nSave did not occur")



    def open_pop(self, hook_remove, hook_add, hook_apply):
        '''Manage bookmark sources: Major dialogue'''
        dprint(3, "\ngMemobook::open_pop::")
        [width, height] = self.__window.get_size()
        if width < 200:
            width = 300
        if height < 200:
            height = 250
        manager = Gtk.Window()
        manager.set_title("Manage Sources")
        manager.set_transient_for(self.__window)
        manager.set_focus()
        manager.set_default_geometry(width/2, height/2)
        manager.connect("destroy", lambda x: manager.destroy())
        source_list = Gtk.ListStore(str)
        dprint(3, "adding labels...")
        source_items = self.ctrl["db"]["scan"]
        if isinstance(source_items, str):
            source_items = [ source_items ]
        else:
            source_items = list(source_items)
        source_items.sort()
        for item in source_items:
            source_list.append([item])
        source_tree = Gtk.TreeView(source_list)
        source_tree_select = source_tree.get_selection()
        source_tree_select.set_mode(Gtk.SelectionMode.MULTIPLE)
        source_rend = Gtk.CellRendererText()
        source_column = Gtk.TreeViewColumn("Current silent marks:", source_rend, text=0)
        source_tree.append_column(source_column)
        source_view = Gtk.ScrolledWindow()
        source_view.add(source_tree)
        source_view.set_policy(Gtk.PolicyType.NEVER, Gtk.PolicyType.AUTOMATIC)
        btn_remove = Gtk.Button.new_with_label("Remove")
        btn_remove.connect("clicked",
                           lambda x: hook_remove(source_tree_select, source_items))
        btn_add = Gtk.Button.new_with_label("Add Other")
        btn_add.connect("clicked",
                        lambda x: hook_add(manager, source_tree, source_items))
        btn_apply = Gtk.Button.new_with_label("Apply")
        btn_apply.connect("clicked",
                          lambda x: hook_apply(manager, source_items))
        subbox = Gtk.Box(orientation=Gtk.Orientation.HORIZONTAL)
        subbox.add(btn_remove)
        subbox.add(btn_add)
        subbox.add(btn_apply)
        subbox.set_homogeneous(True)
        subbox.set_child_packing(btn_remove,
                                 expand=False,
                                 fill=True,
                                 padding=5,
                                 pack_type=Gtk.PackType(0))
        subbox.set_child_packing(btn_add,
                                 expand=False,
                                 fill=True,
                                 padding=0,
                                 pack_type=Gtk.PackType(0))
        subbox.set_child_packing(btn_apply,
                                 expand=False,
                                 fill=True,
                                 padding=5,
                                 pack_type=Gtk.PackType(0))
        box = Gtk.Box(orientation=Gtk.Orientation.VERTICAL)
        box.add(source_view)
        box.add(subbox)
        box.set_child_packing(source_view,
                              expand=True,
                              fill=True,
                              padding=0,
                              pack_type=Gtk.PackType(0))
        box.set_child_packing(subbox,
                              expand=False,
                              fill=True,
                              padding=0,
                              pack_type=Gtk.PackType(1))
        manager.add(box)
        manager.show_all()


    def open_pop_remove(self, slist, sitems):
        '''Manage sources: remove directory.'''
        model, pathlist = slist.get_selected_rows()
        iterlist = [ model.get_iter(p) for p in pathlist ]
        index_list = list(j.get_indices()[0] for j in slist.get_selected_rows()[1])
        index_list.sort(reverse=True)
        for index in index_list:
            sitems.pop(index)
        for i in iterlist:
            model.remove(i)


    def open_pop_add(self, win, slist, sitems):
        '''Manage bookmark sourse: add directory. Calls GTK file dialogue.'''
        dialog = Gtk.FileChooserNative.new(title="Select Directory to Add",
                                       parent=win,
                                       action=Gtk.FileChooserAction.SELECT_FOLDER,
                                       accept_label=None, #label is default
                                       cancel_label=None) #label is default
        response = dialog.run()
        if response == Gtk.ResponseType.ACCEPT:
            add_dir = dialog.get_filename()
            sitems.append(add_dir)
            model = slist.get_model()
            model.append([add_dir])


    def open_pop_apply(self, win, sitems):
        '''Manage sources: apply changes to memobook and config object'''
        self.data.clear()
        if sitems:
            self.ctrl["db"]["scan"] = list(sitems)
        else:
            self.ctrl["db"]["scan"] = "."
        self.data.populate()
        win.destroy()


    def mark_dialogue(self):
        '''Select mark to be added to note from list of current marks'''
        def silent_remove(strees, cmarks):
            # subfunction for removing items from the pending list of silent marks
            model, pathlist = strees.get_selected_rows()
            iterlist = [ model.get_iter(p) for p in pathlist ]
            index_list = list(j.get_indices()[0] for j in strees.get_selected_rows()[1])
            index_list.sort(reverse=True)
            for index in index_list:
                cmarks.pop(index)
            for i in iterlist:
                model.remove(i)
        def silent_add(stree, sentry, cmarks):
            # subfunction for adding items to the pending list of silent marks
            model = stree.get_model()
            tmp_marks = parse.split_by_unknown(sentry.get_text())
            dprint(3, "\nMarks to be added: " + str(tmp_marks))
            for tm in tmp_marks:
                cmarks.append(tm)
                model.append([tm])
            sentry.set_text("")
        def silent_apply(widget, nt, cmarks):
            # assert pending list of marks to memobook
            dprint(3, "\nMarks to be stored: " + str(cmarks))
            self.data.update(nt, cmarks)
            widget.destroy()
            return
        dprint(3, "\ngMemobook::mark_dialogue::")
        doc = self.__window.get_active_document()
        path = GtkSource.File.get_location(doc.get_file()).get_path()
        dprint(3, "Got path: " + str(path))
        note = self.__get_note_ref(path)
        if not note:
            note = self.__make_note_ref(doc, path, True)
        dprint(3, "...Note is prepared.")
        if not note:
            msg = Gtk.MessageDialog(self.__window,
                                    Gtk.DialogFlags(2),
                                    0,
                                    (Gtk.STOCK_OK,Gtk.ResponseType.OK),
                                    "Error: could not find note reference for current document.")
            
            msg.run()
            msg.destroy()
            return
        if note.mime == NoteMime.TEXT:
            width, height = self.__window.get_size()
            if width < 200:
                width = 300
            if height < 200:
                height = 250
            manager = Gtk.Window()
            manager.set_title("Manage Silent Marks")
            manager.set_transient_for(self.__window)
            manager.set_focus()
            manager.set_default_geometry(width/2, height/2)
            manager.connect("destroy", lambda x: manager.destroy())
            silent_list = Gtk.ListStore(str)
            current_marks = []
            if note.tags:
                if note.tags.silent:
                    dprint(3, "\nSilent tags: " + str(note.tags.silent))
                    current_marks = list(note.tags.silent)
                    current_marks.sort()
                    for st in current_marks:
                        silent_list.append([st])
            silent_tree = Gtk.TreeView(silent_list)
            silent_tree_select = silent_tree.get_selection()
            silent_tree_select.set_mode(Gtk.SelectionMode.MULTIPLE)
            silent_rend = Gtk.CellRendererText()
            silent_column = Gtk.TreeViewColumn("Current directories to be scanned for marks:", silent_rend,text=0)
            silent_tree.append_column(silent_column)
            silent_view = Gtk.ScrolledWindow()
            silent_view.add(silent_tree)
            silent_view.set_policy(Gtk.PolicyType.AUTOMATIC, Gtk.PolicyType.AUTOMATIC)
            label_remove = Gtk.Label("Remove selected files?")
            btn_remove = Gtk.Button.new_with_label("Remove")
            btn_remove.connect("clicked",
                               lambda x: silent_remove(silent_tree_select,
                                                       current_marks))
            label_add = Gtk.Label("Mark(s) to be added to list?")
            buffer_add = Gtk.EntryBuffer.new(None,-1)
            buffer_add.set_max_length(256)
            entry_add = Gtk.Entry.new_with_buffer(buffer_add)
            entry_add.set_placeholder_text("Type here...")
            btn_add = Gtk.Button.new_with_label("Add")
            btn_add.connect("clicked",
                            lambda x: silent_add(silent_tree,
                                                 entry_add,
                                                 current_marks))
            btn_cancel = Gtk.Button.new_with_label("Cancel")
            btn_cancel.connect("clicked",
                               lambda x: manager.destroy())
            btn_apply = Gtk.Button.new_with_label("Apply")
            btn_apply.connect("clicked",
                              lambda x: silent_apply(manager,
                                                     note,
                                                     current_marks))
            grid_alts = Gtk.Grid.new()
            grid_alts.attach(label_remove, 0, 0, 1, 1)
            grid_alts.attach(btn_remove, 2, 0, 1, 1)
            grid_alts.attach(label_add, 0, 1, 1, 1)
            grid_alts.attach(entry_add, 1, 1, 1, 1)
            grid_alts.attach(btn_add, 2, 1, 1, 1)
            grid_alts.set_row_spacing(5)
            grid_alts.set_column_spacing(5)
            grid_alts.set_column_homogeneous(True)
            grid_alts.set_row_homogeneous(True)
            box_control = Gtk.Box(orientation=Gtk.Orientation.HORIZONTAL)
            box_control.add(btn_cancel)
            box_control.add(btn_apply)
            box_control.set_homogeneous(True)
            box_control.set_child_packing(btn_cancel,
                                          expand=False,
                                          fill=True,
                                          padding=5,
                                          pack_type=Gtk.PackType(0))
            box_control.set_child_packing(btn_apply,
                                          expand=False,
                                          fill=True,
                                          padding=5,
                                          pack_type=Gtk.PackType(0))
            padding_box_horiz = Gtk.Box(orientation=Gtk.Orientation.HORIZONTAL)
            padding_box_vert = Gtk.Box(orientation=Gtk.Orientation.VERTICAL)
            padding_box_vert.add(grid_alts)
            padding_box_vert.add(box_control)
            padding_box_vert.set_child_packing(grid_alts,
                                               expand=True,
                                               fill=True,
                                               padding=5,
                                               pack_type=Gtk.PackType(0))
            padding_box_vert.set_child_packing(box_control,
                                               expand=True,
                                               fill=True,
                                               padding=0,
                                               pack_type=Gtk.PackType(1))
            padding_box_horiz.add(padding_box_vert)
            padding_box_horiz.set_child_packing(padding_box_vert,
                                                expand=True,
                                                fill=True,
                                                padding=5,
                                                pack_type=Gtk.PackType(0))
            box = Gtk.Box(orientation=Gtk.Orientation.VERTICAL)
            box.add(silent_view)
            box.add(padding_box_horiz)
            box.set_child_packing(silent_view,
                                  expand=True,
                                  fill=True,
                                  padding=0,
                                  pack_type=Gtk.PackType(0))
            box.set_child_packing(padding_box_horiz,
                                  expand=False,
                                  fill=False,
                                  padding=0,
                                  pack_type=Gtk.PackType(1))
            manager.add(box)
            manager.show_all()
            

    def __get_note_ref(self, fpath):
        '''Get note path: returns note ID/path if note was opened via memobook, returns None if not'''
        # this function is used in save-note methods:
        #   we must have an associated note if we wish to save marks to memobook.
        #   This function tests whether we do.
        if not self.__open_notes:
            return None
        for nt in self.__open_notes:
            if nt.ID == fpath:
                return nt
        return None

    
    def __make_note_ref(self, doc, docpath, bodycopy=False):
        '''Make note path: create and associate a note with current file and return it'''
        # this function is used in save-note methods:
        #   we must have an associated note if we wish to save marks to memobook.
        #   This function sets up the note so that we can perform the save.
        try:
            note = Note()
            note.title = os.path.basename(docpath)
            note.ID = docpath
            note.mime = NoteMime.TEXT
            docbody = doc.get_text(doc.get_start_iter(),
                                   doc.get_end_iter(),
                                   True)
            if bodycopy:
                note.body = docbody
            note.tags = Tag(parse.parse(docbody))
            note.tags.silent = index_search(self.index,
                                            docpath,
                                            None)
        except Exception as e:
            dprint(1, "\nError: " + str(e))
            return None
        else:
            self.__open_notes.append(note)
            return note
