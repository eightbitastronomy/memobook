from tkinter import *
from tkinter import scrolledtext as st


class ListboxH(Listbox):
    def __init__(self,master=None,**kwargs):
        self.__frame = Frame(master)
        self.__scroll = Scrollbar(self.__frame,orient="horizontal")
        self.__scroll.pack(side=BOTTOM,fill="x")
        Listbox.__init__(self, self.__frame, **kwargs)
        self.config(self,xscrollcommand=self.__scroll.set)
        self.__scroll.config(command=self.xview)
        self.pack(side=TOP,fill=BOTH,expand="true")
        list_meths = vars(Listbox).keys()
        methods = vars(Pack).keys() | vars(Grid).keys() | vars(Place).keys()
        methods = methods.difference(list_meths)
        for m in methods:
            if m[0] != '_' and m != 'config' and m != 'configure':
                setattr(self, m, getattr(self.__frame, m))
    def __str__(self):
        return str(self.__frame)

class ScrolledTextH(st.ScrolledText):
    def __init__(self,master,**kwargs):
        self.__frame = Frame(master)
        self.__scroll = Scrollbar(self.__frame,orient="horizontal")
        kwargs.update({"master":self.__frame})
        st.ScrolledText.__init__(self,**kwargs)
        st.ScrolledText.config(self,xscrollcommand=self.__scroll.set)
        self.__scroll.config(command=self.xview)
        self.pack(side=TOP,fill="both",expand="true")
        st_meths = vars(Listbox).keys()
        methods = vars(Pack).keys() | vars(Grid).keys() | vars(Place).keys()
        methods = methods.difference(st_meths)
        for m in methods:
            if m[0] != '_' and m != 'config' and m != 'configure':
                setattr(self, m, getattr(self.__frame, m))
    def hide_h(self):
        self.__scroll.pack_forget()
    def show_h(self):
        self.__scroll.pack(side=BOTTOM,fill="x")
    def __str__(self):
        return str(self.__frame)
