import tkinter
from tkinter import font
from PIL import ImageTk
from memo.scrolledcanvas import ScrolledCanvas


class PDFCanvas(ScrolledCanvas):

    __src_tk = []
    __current = 0
    __sz = []
    __pos = []
    __rot= []
    
    def __init__(self, master, **kwargs):
        ScrolledCanvas.__init__(self,master,**kwargs)
        for doc in self._src:
            self.__sz.append(doc.size)
            self.__pos.append([0.,0.])
            self.__rot.append(0.)
        self.__page_rev = tkinter.Button(self._ctrl_frame,
                                         text="<",
                                         padx=0,
                                         pady=0,
                                         command=lambda: self.__set_page_rev())
        self.__page_rev_f = tkinter.Button(self._ctrl_frame,
                                           text="<<",
                                           padx=0,
                                           pady=0,
                                           command=lambda: self.__goto(0))
        self.__page_fwd = tkinter.Button(self._ctrl_frame,
                                         text=">",
                                         padx=0,
                                         pady=0,
                                         command=lambda: self.__set_page_fwd())
        self.__page_fwd_f = tkinter.Button(self._ctrl_frame,
                                           text=">>",
                                           padx=0,
                                           pady=0,
                                           command=lambda: self.__goto(len(self._src)-1))
        self.__page_nav = tkinter.Entry(self._ctrl_frame,
                                        width="4")
        self.__page_nav.insert(0,"1")
        page_filler_1 = tkinter.Label(self._ctrl_frame,
                                      text="   ")
        self.__page_nav_pgs = tkinter.Label(self._ctrl_frame,
                                            text="/"+str(len(self._src)))
        self.__page_nav_go = tkinter.Button(self._ctrl_frame,
                                            text="Go",
                                            padx=0,
                                            pady=0,
                                            command=lambda: self.__jumpto(self.__page_nav.get()))
        page_filler_2 = tkinter.Label(self._ctrl_frame,
                                      text="  ")
        self.__page_rev_f.grid(row=0,
                               column=0,
                               sticky="w")
        self.__page_rev.grid(row=0,
                             column=1,
                             sticky="w")
        self.__page_fwd.grid(row=0,
                             column=2,
                             sticky="w")
        self.__page_fwd_f.grid(row=0,
                               column=3,
                               sticky="w")
        page_filler_1.grid(row=0,
                           column=4,
                           sticky="w")
        self.__page_nav.grid(row=0,
                             column=5,
                             sticky="w")
        self.__page_nav_pgs.grid(row=0,
                                 column=6,
                                 sticky="w")
        self.__page_nav_go.grid(row=0,
                                column=7,
                                sticky="w")
        page_filler_2.grid(row=0,
                           column=8,
                           sticky="w")
        # resize pdf image based on current window space
        self._scale = (self._frame._nametowidget(self._frame.winfo_parent()).winfo_width() - self._scroll_v.winfo_reqwidth()) / self.__sz[0][0]
        self.__src_tk = ImageTk.PhotoImage(self._src[self.__current].resize((int(self._scale*float(self.__sz[self.__current][0])),
                                                                             int(self._scale*float(self.__sz[self.__current][1])))))
        self._canvas_ref = self.create_image(0,
                                             0,
                                             image=self.__src_tk,
                                             anchor="nw")
        self.__page_nav.bind("<Return>", lambda e: self.__jumpto(self.__page_nav.get()))

    def __set_page_rev(self):
        if self.__current > 0:
            self.__goto(self.__current - 1)

    def __set_page_fwd(self):
        if self.__current < len(self._src):
            self.__goto(self.__current + 1)

    def _resize(self):
        self.__src_tk = ImageTk.PhotoImage(self._src[self.__current].resize((int(self._scale*float(self.__sz[self.__current][0])),
                                                                              int(self._scale*float(self.__sz[self.__current][1])))))
        self.itemconfig(self._canvas_ref, image=self.__src_tk)
        self._on_frame_configure(False)

    def __set_page(self):
        def __apply_page(canv,widge,dia):
            try:
                page = int(dia.get())-1
                if (page > -1) and (page < len(self._src)):
                    self.__goto(page)
                widge.destroy()
            except Exception as e:
                print(e)
        dialog_win = tkinter.Toplevel(self._frame)
        dialog_frame = tkinter.Frame(dialog_win)
        instructions = tkinter.Label(dialog_frame,
                                     text="Page #:")
        dialog = tkinter.Entry(dialog_frame,
                               width=8)
        dialog.insert(0, str(self._scale+1))
        dialog_apply = tkinter.Button(dialog_frame,
                                      text="Apply",
                                      command=lambda: __apply_page(self,
                                                                   dialog_win,
                                                                   dialog))
        dialog_win.bind("<Return>", lambda e:dialog_apply.invoke())
        instructions.pack(side="left")
        dialog.pack(side="left")
        dialog_apply.pack(side="left")
        dialog_frame.pack()

    def __goto(self, page):
        self.__pos[self.__current][0]=self.xview()[0]
        self.__pos[self.__current][1]=self.yview()[0]
        self.__current = page
        self.__src_tk = ImageTk.PhotoImage(self._src[self.__current].resize((int(self._scale*float(self.__sz[self.__current][0])),
                                                                              int(self._scale*float(self.__sz[self.__current][1])))))
        self._canvas_ref = self.create_image(0,
                                             0,
                                             image=self.__src_tk,
                                             anchor="nw")
        self.itemconfig(self._canvas_ref, image=self.__src_tk)
        self.xview_moveto(self.__pos[self.__current][0])
        self.yview_moveto(self.__pos[self.__current][1])
        self.__page_nav.delete(0,tkinter.END)
        self.__page_nav.insert(0,str(self.__current+1))

    def __jumpto(self,pagestr):
        try:
            pg = int(pagestr)
        except:
            return
        else:
            pg -= 1 # Account for first page ... 0 vs 1
            if (pg >= 0) and (pg < len(self._src)):
                self.__goto(pg)

    def _rotate_CCW(self):
        self._src[self.__current] = self._src[self.__current].rotate(90.0,expand=1)
        self.__sz[self.__current] = (self.__sz[self.__current][1],self.__sz[self.__current][0],)
        self._resize()

    def _rotate_CW(self):
        self._src[self.__current] = self._src[self.__current].rotate(-90.0,expand=1)
        self.__sz[self.__current] = (self.__sz[self.__current][1],self.__sz[self.__current][0],)
        self._resize()

    def _on_frame_configure(self,eventflag):
        '''Reset the scroll region to encompass the inner frame'''
        if eventflag and (self._auto_resize.get() == 1):
            self._scale = (self._frame._nametowidget(self._frame.winfo_parent()).winfo_width() - self._scroll_v.winfo_reqwidth()) / self.__sz[0][0]
            self._resize()
        ScrolledCanvas._on_frame_configure(self,eventflag)

    ### to meet inheritance needs, override __drag, call parent.__drag, then set self.__pos, then return
    def _drag(self, x, y):
        ScrolledCanvas._drag(self, x, y)
        self.__pos[self.__current][0]=self.xview()[0]
        self.__pos[self.__current][1]=self.yview()[0]
