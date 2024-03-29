###############################################################################################
#  hscroll.py: Tk widgets with scrollbars and additional functionality
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



'''Classes implementing scrollbars; classes implementing proxy-layers to facilitate edit-detection of text'''



import tkinter
from tkinter import scrolledtext
from memo.debug import dprint




class ListboxH(tkinter.Listbox):
    
    '''A ListBox with a horizontal scrollbar'''

    
    def __init__(self, master=None, **kwargs):
        dprint(3, "\nListboxH::__init__")
        self.__frame = tkinter.Frame(master)
        self.__scroll = tkinter.Scrollbar(self.__frame, orient="horizontal")
        self.__scroll.pack(side=tkinter.BOTTOM, fill="x")
        tkinter.Listbox.__init__(self, self.__frame, **kwargs)
        self.config(self, xscrollcommand=self.__scroll.set)
        self.__scroll.config(command=self.xview)
        self.pack(side=tkinter.TOP, fill=tkinter.BOTH, expand="true")
        list_meths = vars(tkinter.Listbox).keys()
        methods = vars(tkinter.Pack).keys() | vars(tkinter.Grid).keys() | vars(tkinter.Place).keys()
        methods = methods.difference(list_meths)
        for m in methods:
            if m[0] != '_' and m != 'config' and m != 'configure':
                setattr(self, m, getattr(self.__frame, m))

                
    def __str__(self):
        dprint(3, "\nListboxH::__str__")
        return str(self.__frame)



class ListboxHV(tkinter.Listbox):
    
    '''A ListBox with horizontal and vertical scrollbars'''

    
    def __init__(self, master=None, **kwargs):
        dprint(3, "\nListboxHV::__init__")
        self.__frame = tkinter.Frame(master)
        self.__subframe = tkinter.Frame(self.__frame)
        tkinter.Listbox.__init__(self, self.__subframe, **kwargs)
        self.__scroll_h = tkinter.Scrollbar(self.__frame, orient="horizontal")
        self.__scroll_v = tkinter.Scrollbar(self.__subframe, orient="vertical")
        self.config(self,
                    xscrollcommand=self.__scroll_h.set,
                    yscrollcommand=self.__scroll_v.set)
        self.__scroll_h.config(command=self.xview)
        self.__scroll_v.config(command=self.yview)
        self.__scroll_v.pack(side="right", fill="y")
        self.__scroll_h.pack(side="bottom", fill="x")
        self.pack(side="left", fill="both", expand="true")
        self.__subframe.pack(side="top", fill="both", expand="true")
        list_meths = vars(tkinter.Listbox).keys()
        methods = vars(tkinter.Pack).keys() | vars(tkinter.Grid).keys() | vars(tkinter.Place).keys()
        methods = methods.difference(list_meths)
        for m in methods:
            if m[0] != '_' and m != 'config' and m != 'configure':
                setattr(self, m, getattr(self.__frame, m))

                
    def __str__(self):
        dprint(3, "\nListboxHV::__str__")
        return str(self.__frame)


    
class ScrolledTextH(scrolledtext.ScrolledText):
    
    '''A ScrolledText with a horizontal scrollbar'''

    
    def __init__(self, master, **kwargs):
        dprint(3, "\nScrolledTextH::__init__")
        self.__frame = tkinter.Frame(master)
        self.__scroll = tkinter.Scrollbar(self.__frame, orient="horizontal")
        kwargs.update({"master":self.__frame})
        scrolledtext.ScrolledText.__init__(self, **kwargs)
        scrolledtext.ScrolledText.config(self, xscrollcommand=self.__scroll.set)
        self.__scroll.config(command=self.xview)
        self.pack(side=tkinter.TOP,
                  fill="both",
                  expand="true")
        st_meths = vars(tkinter.Listbox).keys()
        methods = vars(tkinter.Pack).keys() | vars(tkinter.Grid).keys() | vars(tkinter.Place).keys()
        methods = methods.difference(st_meths)
        for m in methods:
            if m[0] != '_' and m != 'config' and m != 'configure':
                setattr(self, m, getattr(self.__frame, m))

                
    def hide_h(self):
        '''Hide the scroll bar'''
        dprint(3, "\nScrolledTextH::hide_h")
        self.__scroll.pack_forget()

        
    def show_h(self):
        '''Show the scroll bar'''
        dprint(3, "\nScrolledTextH::show_h")
        self.__scroll.pack(side=tkinter.BOTTOM, fill="x")

        
    def __str__(self):
        dprint(3, "\nScrolledTextH::__str__")
        return str(self.__frame)

    

class TextCompound(ScrolledTextH):
    
    '''A ScrolledTextH that filters for text edits'''
    
    __hook = None

    
    def __init__(self, master, **kwargs):
        dprint(3, "\nTextCompound::__init__")
        if "hook" in kwargs.keys():
            self.__hook = kwargs["hook"]
            del kwargs["hook"]
        ScrolledTextH.__init__(self, master, **kwargs)
        self._original = self._w + "_original"
        self.tk.call("rename", self._w, self._original)
        self.tk.createcommand(self._w, self._compound)
        

    def set_hook(self,hook):
        '''Set callback function for insertion, deletion, replacement'''
        dprint(3, "\nTextCompound::set_hook")
        self.__hook = hook

        
    def _compound(self, cmd, *args):
        '''Middleman function: intercept method calls and filter for edits'''
        # suppresses errors due to too many undo's
        # dispatches __hook function for insert, delete, replace
        dprint(3, "\nTextCompound::_compound")
        compound_cmd = (self._original, cmd) + args
        try:
            cmd_result = self.tk.call(compound_cmd)
        except tkinter.TclError as tcle:
            tcle_descr = str(tcle)
            if tcle_descr == "nothing to undo":
                pass
            elif tcle_descr == '''text doesn't contain any characters tagged with "sel"''':
                pass
            else:
                raise tcle
        else:
            if (cmd == "edit") and ("modified" in args):
                return cmd_result
            elif cmd in ("insert", "delete", "replace"):
                if self.__hook is not None:
                    self.__hook()
            return cmd_result
