###############################################################################################
#  memobook.py: parent class for the GUI object that runs the show
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



'''Memobook trunk-class: the parent class for frontend and control structures 
   for the application. Configuration values are in config.py or loaded via extconf.py.
   Database is handled in binding.py.'''


import os
import os.path
import memo.extconf as extconf
import memo.parse as parse
import memo.empty as empty
from memo.binding import FileBinding, DatabaseBinding
from memo.note import NoteMime
from memo.debug import dprint




    

class Memobook:

    '''Memobook trunk class'''

    ctrl = None
    data = None
    index = None
    

    def __init__(self, **kwargs):
        dprint(3, "\nMemobook::__init__::")
        if "ctrl" in kwargs.keys():
            try:
                self.ctrl = extconf.load_file(kwargs["ctrl"])
            except Exception as e:
                dprint(1, "Error loading or preparing memobook: " + str(e))
                empty.write_skeleton_conf(os.getcwd()+os.sep, "conf.xml")
                self.ctrl = extconf.load_file("conf.xml")
                working_loc = os.getcwd() + os.sep + 'conf.xml'
            else:
                dprint(3, "conf.xml found. ")
                #working_loc = str(os.path.dirname(kwargs["ctrl"]))
                #if working_loc == '':
                #    working_loc == './conf.xml'
                working_loc = kwargs["ctrl"]
        else:
            empty.write_skeleton_conf(os.getcwd()+os.sep, "conf.xml")
            self.ctrl = extconf.load_file("conf.xml")
            working_loc = os.getcwd() + os.sep + 'conf.xml'
        self.ctrl["loc"] = working_loc
        if not "scan" in self.ctrl["db"].keys() :
            self.ctrl["db"]["scan"] = "."
        if "data" in kwargs.keys():
            self.data = kwargs["data"]
        else:
            self.data = DatabaseBinding(self.ctrl)
            exc = self.data.get_last_error()
            if exc:
                dprint(2, "Failed to open DatabaseBinding. Opening FileBinding instead. ")
                messagebox.showinfo( "Data error","Unable to open data source: " + str(exc) )
                self.data = FileBinding(self.ctrl) # FileBinding is no longer a reasonable fallback. Should remove this.
        try:
            if "index" in kwargs.keys():
                self.index = extconf.load_file(kwargs["index"])
            else:
                self.index = extconf.load_file(self.ctrl["index"])
        except Exception as e:
            dprint(1, "Error loading index.xml: " + str(e))
            empty.write_skeleton_index(os.getcwd()+os.sep, "index.xml")
            self.index = extconf.load_file("index.xml")
            index_loc = os.getcwd() + os.sep + 'index.xml'
            self.ctrl["index"] = index_loc
        self.data.set_index(self.index)


    def populate_menus(self):
        dprint(3, "\nMemobook::populate_menus:: ")

    
    def set_bindings(self):  # binding functions to keystrokes
        dprint(3, "\nMemobook::set_bindings:: ")

    
    def _build_file_types(self):
        dprint(3, "\nMemobook::_build_file_types:: ")
        prep_list = []
        for filetype in self.ctrl["mime"]:
            tmp_list = None
            if isinstance(self.ctrl["mime"][filetype]["suff"], str):
                tmp_tuple = ( str(filetype + " files"), str("*" + self.ctrl["mime"][filetype]["suff"]) )
            else:
                tmp_type = [ str("*"+t) for t in self.ctrl["mime"][filetype]["suff"] ]
                tmp_tuple = ( str(filetype + " files"), tuple(tmp_type) )
            prep_list.append(tmp_tuple)
        prep_list.append(("All files", "*.*"))
        return tuple(prep_list)

    
    def open_file(self):  # open by file name
        dprint(3, "\nMemobook::open_file:: ")


    def save_note(self):
        dprint(3, "\nMemobook::__save_note:: ")
        

    def save_note_as(self):
        dprint(3, "\nMemobook::__save_note_as:: ")
        

    def _process_save_target(self,note,saveas=False,callback=None):  # select file name for saving
        dprint(3, "\nMemobook::__process_save_target:: Note title is " + note.title + ", saveas=" + str(saveas) + ". ")
        return 0
    

    def close_page(self):
        dprint(3, "\nMemobook::__close_page:: ")
        return 0
    
    
    def close_all(self):
        dprint(3, "\nMemobook::__close_all:: ")
                    
            
    def exit_all(self, e):
        dprint(3, "\nMemobook::exit_all:: ")
        self.ctrl.print_config(self.ctrl["loc"])
        if isinstance(self.index, extconf.Configuration):
            self.index.print_config(self.ctrl["index"])

    
    def font_dialogue(self):
        dprint(3, "\nMemobook::font_dialogue:: ")


    def mark_dialogue(self):  # select mark to be added to note from list of current marks
        dprint(3, "\nMemobook::__mark_dialogue:: ")


    def _mark_update_index(self, win, ls, nt):
        dprint(3, "\nMemobook::__mark_update_index:: ")
        self.data.update(nt,ls)


    def open_pop(self, hook_remove, hook_add, hook_apply):  # populate bookmark lists
        dprint(3, "\nMemobook::__open_pop:: ")


    def publication_info(self):
        dprint(3, "\nMemobook::__publication_info:: ")
