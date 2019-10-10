import tkinter
from tkinter import font
from PIL import ImageTk



class PDFCanvas(tkinter.Canvas):

    __src = None
    __src_tk = []
    __current = 0
    __sz = []
    __canvas_ref = None
    __auto_resize = None
    __scale = 1.0
    __x = []
    __y = []
    __inc_x = []
    __inc_y = []
    __pos = []
    
    def __init__(self, master, **kwargs):
        self.__frame = tkinter.Frame(master)
        self.__ctrl_frame = tkinter.Frame(self.__frame,
                                          width=1)
        self.__disp_frame = tkinter.Frame(self.__frame)
        if "document" in kwargs.keys():
            self.__src = kwargs["document"]
            for doc in self.__src:
                self.__sz.append(doc.size)
                self.__pos.append([0.,0.])
            del kwargs["document"]
        kwargs.update({"master":self.__disp_frame})
        tkinter.Canvas.__init__(self,**kwargs)
        self.__page_rev = tkinter.Button(self.__ctrl_frame,
                                         text="<",
                                         padx=0,
                                         pady=0,
                                         command=lambda: self.__set_page_rev())
        self.__page_rev_f = tkinter.Button(self.__ctrl_frame,
                                           text="<<",
                                           padx=0,
                                           pady=0,
                                           command=lambda: self.__goto(0))
        self.__page_fwd = tkinter.Button(self.__ctrl_frame,
                                         text=">",
                                         padx=0,
                                         pady=0,
                                         command=lambda: self.__set_page_fwd())
        self.__page_fwd_f = tkinter.Button(self.__ctrl_frame,
                                           text=">>",
                                           padx=0,
                                           pady=0,
                                           command=lambda: self.__goto(len(self.__src)-1))
        self.__page_nav = tkinter.Entry(self.__ctrl_frame,
                                        width="4")
        self.__page_nav.insert(0,"1")
        page_filler_1 = tkinter.Label(self.__ctrl_frame,
                                      text="   ")
        self.__page_nav_pgs = tkinter.Label(self.__ctrl_frame,
                                            text="/"+str(len(self.__src)))
        self.__page_nav_go = tkinter.Button(self.__ctrl_frame,
                                            text="Go",
                                            padx=0,
                                            pady=0,
                                            command=lambda: self.__jumpto(self.__page_nav.get()))
        page_filler_2 = tkinter.Label(self.__ctrl_frame,
                                      text="  ")
        self.__auto_resize = tkinter.IntVar()
        self.__auto_resize_cb = tkinter.Checkbutton(self.__ctrl_frame,
                                                    text="Auto-resize:",
                                                    variable=self.__auto_resize,
                                                    onvalue=1,
                                                    offvalue=0,
                                                    padx=0,
                                                    pady=0)
        self.__scroll_v = tkinter.Scrollbar(self.__disp_frame,
                                            orient="vertical")
        self.__scroll_h = tkinter.Scrollbar(self.__disp_frame,
                                            orient="horizontal")
        if "OpenSymbol" in tkinter.font.families(root=master):
            self.__zoom = tkinter.Label(self.__disp_frame,
                                        text="",
                                        borderwidth=0,
                                        padx=0,
                                        pady=0,
                                        font=("Open Symbol",10,"normal"))
        else:
            self.__zoom = tkinter.Label(self.__disp_frame,
                                        text="⃝",
                                        borderwidth=0,
                                        padx=0,
                                        pady=0,
                                        font=("Open Symbol",10,"normal"))
        tkinter.Canvas.config(self,
                              yscrollcommand=self.__scroll_v.set,
                              xscrollcommand=self.__scroll_h.set)
        self.__scroll_v.config(command=self.yview)
        self.__scroll_h.config(command=self.xview)
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
        self.__auto_resize_cb.grid(row=0,
                                   column=9,
                                   sticky="w")
        self.grid(row=0,
                  column=0,
                  sticky="nswe")
        self.__scroll_v.grid(row=0,
                             column=1,
                             sticky="ns")
        self.__scroll_h.grid(row=1,
                             column=0,
                             sticky="we")
        self.__zoom.grid(row=1,
                         column=1,
                         sticky="nswe")
        self.__ctrl_frame.grid_rowconfigure(0,
                                            weight=0)
        self.__ctrl_frame.grid(row=0,
                               column=0,
                               sticky="nwe")
        self.__disp_frame.grid_rowconfigure(0,
                                            weight=1)
        self.__disp_frame.grid_rowconfigure(1,
                                            weight=0)
        self.__disp_frame.grid_columnconfigure(0,
                                               weight=1)
        self.__disp_frame.grid(sticky="nswe")
        self.__frame.grid_rowconfigure(0,
                                       weight=0)
        self.__frame.grid_rowconfigure(1,
                                       weight=1)
        self.__frame.grid_columnconfigure(0,
                                          weight=1)
        self.__frame.grid(sticky="nswe")
        if self.__src:
            # resize pdf image based on current window space
            self.__scale = (self.__frame._nametowidget(self.__frame.winfo_parent()).winfo_width() - self.__scroll_v.winfo_reqwidth()) / self.__sz[0][0]
            self.__src_tk = ImageTk.PhotoImage(self.__src[self.__current].resize((int(self.__scale*float(self.__sz[self.__current][0])),
                                                                                  int(self.__scale*float(self.__sz[self.__current][1])))))
            self.__canvas_ref = self.create_image(0,
                                                  0,
                                                  image=self.__src_tk,
                                                  anchor="nw")
        self.__zoom.bind("<Button-1>", lambda e:self.__set_zoom())
        self.__page_nav.bind("<Return>", lambda e: self.__jumpto(self.__page_nav.get()))
        self.__frame.bind("<Configure>", lambda e: self.__on_frame_configure(True))
        self.bind("<Button-1>", lambda e: self.__drag_start(e.x, e.y))
        self.bind("<B1-Motion>", lambda e: self.__drag(e.x, e.y))
        canv_meths = vars(tkinter.Canvas).keys()
        methods = vars(tkinter.Pack).keys() | vars(tkinter.Grid).keys() | vars(tkinter.Place).keys()
        methods = methods.difference(canv_meths)
        for m in methods:
            if m[0] != '_' and m != 'config' and m != 'configure':
                setattr(self, m, getattr(self.__frame, m))

    def get_frame(self):
        return self.__frame

    def set_hook(self,func):
        pass

    def hide_h(self):
        self.__scroll_v.pack_forget()
        self.__scroll_h.pack_forget()

    def show_h(self):
        self.__scroll_v.pack(side="right",fill="y")
        self.__scroll_h.pack(side="bottom",fill="x")

    def __set_page_rev(self):
        if self.__current > 0:
            self.__goto(self.__current - 1)

    def __set_page_fwd(self):
        if self.__current < len(self.__src):
            self.__goto(self.__current + 1)

    def __set_zoom(self):
        def __apply_zoom(canv,widge,dia):
            try:
                zoom = float(dia.get())
                if (zoom > 0.) and (zoom <= 500.0):
                    self.__scale = zoom/100.0
                    self.__resize()
                widge.destroy()
            except Exception as e:
                print(e)
        dialog_win = tkinter.Toplevel(self.__frame)
        dialog_frame = tkinter.Frame(dialog_win)
        instructions = tkinter.Label(dialog_frame,
                                     text="Zoom (%):")
        dialog = tkinter.Entry(dialog_frame,
                               width=8)
        dialog.insert(0, str(self.__scale*100.0))
        dialog_apply = tkinter.Button(dialog_frame,
                                      text="Apply",
                                      command=lambda: __apply_zoom(self,
                                                                   dialog_win,
                                                                   dialog))
        dialog_win.bind("<Return>", lambda e:dialog_apply.invoke())
        instructions.pack(side="left")
        dialog.pack(side="left")
        dialog_apply.pack(side="left")
        dialog_frame.pack()
        
    def __resize(self):
        self.__src_tk = ImageTk.PhotoImage(self.__src[self.__current].resize((int(self.__scale*float(self.__sz[self.__current][0])),
                                                                              int(self.__scale*float(self.__sz[self.__current][1])))))
        self.itemconfig(self.__canvas_ref, image=self.__src_tk)
        self.__on_frame_configure(False)

    def __set_page(self):
        def __apply_page(canv,widge,dia):
            try:
                page = int(dia.get())-1
                if (page > -1) and (page < len(self.__src)):
                    self.__goto(page)
                widge.destroy()
            except Exception as e:
                print(e)
        dialog_win = tkinter.Toplevel(self.__frame)
        dialog_frame = tkinter.Frame(dialog_win)
        instructions = tkinter.Label(dialog_frame,
                                     text="Page #:")
        dialog = tkinter.Entry(dialog_frame,
                               width=8)
        dialog.insert(0, str(self.__scale+1))
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
        self.__current = page
        self.__src_tk = ImageTk.PhotoImage(self.__src[self.__current].resize((int(self.__scale*float(self.__sz[self.__current][0])),
                                                                              int(self.__scale*float(self.__sz[self.__current][1])))))
        self.__canvas_ref = self.create_image(0,
                                              0,
                                              image=self.__src_tk,
                                              anchor="nw")
        self.itemconfig(self.__canvas_ref, image=self.__src_tk)
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
            if (pg >= 0) and (pg < len(self.__src)):
                self.__goto(pg)

    def __str__(self):
        return str(self.__frame)

    def __on_frame_configure(self,eventflag):
        '''Reset the scroll region to encompass the inner frame'''
        if eventflag and (self.__auto_resize.get() == 1):
            self.__scale = (self.__frame._nametowidget(self.__frame.winfo_parent()).winfo_width() - self.__scroll_v.winfo_reqwidth()) / self.__sz[0][0]
            self.__resize()
        tkinter.Canvas.configure(self, scrollregion=self.bbox("all"))
        

    def __drag_start(self, x, y):
        '''Mouse button down; begin drag operation; collect position information'''
        self.__x = x
        self.__y = y
        bounding = self.bbox(self.__canvas_ref)
        self.__inc_x = 1./float(bounding[2]-bounding[0])
        self.__inc_y = 1./float(bounding[2]-bounding[1])

    ### to meet inheritance needs, override __drag, call parent.__drag, then set self.__pos, then return
    def __drag(self, x, y):
        '''Mouse button down while motion detected; drag operation; scroll canvas image'''
        deltax = float(self.__x - x)
        deltay = float(self.__y - y)
        movex = deltax*self.__inc_x + self.xview()[0]
        self.xview_moveto(movex)
        movey = deltay*self.__inc_y + self.yview()[0]
        self.yview_moveto(movey)
        self.__pos[self.__current][0]=self.xview()[0]
        self.__pos[self.__current][1]=self.yview()[0]
        self.__x = x
        self.__y = y
