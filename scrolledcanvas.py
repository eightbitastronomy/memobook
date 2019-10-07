import PIL
import math
import tkinter
from PIL import Image
from PIL import ImageTk
from tkinter import font



###  PIL does not support SVG; only writes PDF. See https://pillow.readthedocs.io/en/stable/handbook/image-file-formats.html



class ScrolledCanvas(tkinter.Canvas):

    __src = None
    __src_tk = None
    __sz = None
    __canvas_ref = None
    __scale = 1.0
    __x = 0
    __y = 0
    __inc_x = 0.
    __inc_y = 0.
    
    def __init__(self,master,**kwargs):
        self.__frame = tkinter.Frame(master)
        self.__scroll_v = tkinter.Scrollbar(self.__frame,orient="vertical")
        self.__scroll_h = tkinter.Scrollbar(self.__frame,orient="horizontal")
        if "OpenSymbol" in tkinter.font.families(root=master):
            self.__zoom = tkinter.Label(self.__frame,text="",borderwidth=0,padx=0,pady=0,font=("Open Symbol",10,"normal"))
        else:
            self.__zoom = tkinter.Label(self.__frame,text="⃝",borderwidth=0,padx=0,pady=0,font=("Open Symbol",10,"normal"))
        self.__zoom.bind("<Button-1>",lambda e:self.__set_zoom())
        #mag_img = Image.open(io.BytesIO(base64.b64decode('''R0lGODlhZABkAIABAAAAAP///yH5BAEKAAEALAAAAABkAGQAAAL+jI+py+0Po5y02ouz3rz7D4biSJbmCQKqirbUCsexSx/yjbO1mff4LvIJf0DO8EgsXoYPpvLVW0afkJzRSm1gO9ssIpm6eb9iEpha5qXRs9ZaKau9d3F6HTh33+Xt4t71Z9cHOOhXeBKIl2h2aAhD0+i4Qvg4FrAYEgmnGTZpecnpgblZWTIqqWMaqljK6PkJ2jqyyvrqmvp5emVrqbtBK8gbJDvmqwHMR5ypnGWc4UwpvMz8BC1FTSo9jetljYGsh/3hrSouCq6G/qw+y/7tvs2NCH9uHg/ARv9ufysfzn8PHyqByQAO01fhTDBtBxHuMrjPIRdyExRWs/hQ4jGKIZ3yLPSRkWJHTyAtlGyWxkkTjt3AIHkpcqQymC97YTRA82RLjwlyxmwIzidBmzyrsISF8yZSmQyXjlPqdGLRqCGbUv0F9eq6qVojauxqIyvYhGLHVixrNkKXtBu5slWL9q2WuHIXrK1L1i1eBnf3Sujr16jewD0HEybzle1Pv4kPO34MObLkAwUAADs=''')))
        #mag_img_tk = ImageTk.PhotoImage(mag_img.resize((4,4)))
        #mag_img_tk = tkinter.PhotoImage("/home/travertine/Pictures/mag1.gif")
        #mag_img = Image.open("/home/travertine/Pictures/faxanadu_USA-2.png")
        #mag_img_tk = ImageTk.PhotoImage(mag_img.resize((100,100)))
        #self.__zoom.create_image(100,100,image=mag_img_tk,anchor="nw")
        if "image" in kwargs.keys():
            #self.__src = Image.open(kwargs["image"])
            self.__src = kwargs["image"]
            self.__sz = self.__src.size
            del kwargs["image"]
        kwargs.update({"master":self.__frame})
        tkinter.Canvas.__init__(self,**kwargs)
        tkinter.Canvas.config(self,
                              yscrollcommand=self.__scroll_v.set,
                              xscrollcommand=self.__scroll_h.set)
        self.__scroll_v.config(command=self.yview)
        self.__scroll_h.config(command=self.xview)
        self.grid_rowconfigure(0,weight=1)
        self.grid_columnconfigure(0,weight=1)
        self.grid(row=0,column=0,sticky="nswe")
        self.__scroll_v.grid_columnconfigure(1,weight=1)
        self.__scroll_v.grid(row=0,column=1,sticky="ns")
        self.__scroll_h.grid_rowconfigure(1,weight=1)
        self.__scroll_h.grid(row=1,column=0,sticky="we")
        self.__zoom.grid(row=1,column=1,sticky="nswe")
        self.__frame.grid_rowconfigure(0,weight=1)
        self.__frame.grid_columnconfigure(0,weight=1)
        self.__frame.grid(sticky="nswe")
        if self.__src:
            self.__src_tk = ImageTk.PhotoImage(self.__src)
            self.__canvas_ref = self.create_image(0,0,image=self.__src_tk,anchor="nw")
        self.__frame.bind("<Configure>", lambda e: self.__on_frame_configure())
        self.bind("<Button-1>",lambda e: self.__drag_start(e.x,e.y))
        self.bind("<B1-Motion>",lambda e: self.__drag(e.x,e.y))
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
        
    def __str__(self):
        return str(self.__frame)
    
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
        instructions = tkinter.Label(dialog_frame,text="Zoom (%):")
        dialog = tkinter.Entry(dialog_frame,width=8)
        dialog.insert(0,str(self.__scale*100.0))
        dialog_apply = tkinter.Button(dialog_frame,text="Apply",command=lambda:__apply_zoom(self,dialog_win,dialog))
        dialog_win.bind("<Return>",lambda e:dialog_apply.invoke())
        instructions.pack(side="left")
        dialog.pack(side="left")
        dialog_apply.pack(side="left")
        dialog_frame.pack()
        
    def __resize(self):
        self.__src_tk = ImageTk.PhotoImage(self.__src.resize((int(self.__scale*float(self.__sz[0])),
                                                              int(self.__scale*float(self.__sz[1])))
                                                             ))
        self.itemconfig(self.__canvas_ref,image=self.__src_tk)
        self.__on_frame_configure()
        
    def __on_frame_configure(self):
        '''Reset the scroll region to encompass the inner frame'''
        tkinter.Canvas.configure(self,scrollregion=self.bbox("all"))

    def __drag_start(self,x,y):
        '''Mouse button down; begin drag operation; collect position information'''
        self.__x = x
        self.__y = y
        bounding = self.bbox(self.__canvas_ref)
        self.__inc_x = 1./float(bounding[2]-bounding[0])
        self.__inc_y = 1./float(bounding[2]-bounding[1])

    def __drag(self,x,y):
        '''Mouse button down while motion detected; drag operation; scroll canvas image'''
        deltax = float(self.__x - x)
        deltay = float(self.__y - y)
        movex = deltax*self.__inc_x + self.xview()[0]
        self.xview_moveto(movex)
        movey = deltay*self.__inc_y + self.yview()[0]
        self.yview_moveto(movey)
        self.__x = x
        self.__y = y
