# v. 05

import os
import pathlib
import sys
import parse
import magic
import sqlite3
import PIL
import extconf
from note import Note, NoteMime



class Binding():
    _src = None   # could file base directory, database connection
    _error = []
    _text_hook = None
    _img_hook = None
    _pdf_hook = None
    def __init__(self,src=None):
        ### allow for init with or without source ###
        pass
    def set_source(self,s):
        ### prepare the source for use ###
        pass
    def get_last_error(self):
        ### error pop ###
        pass
    def populate(self):
        ### scan the source for all available marks ###
        pass
    def open_note(self,n):
        ### retrieve a note from source ###
        pass
    def open_from_toc(self,n):
        ### retrieve a note via toc entry ###
        pass
    def open_from_toc_intersection(self,n):
        ### retrieve a note via toc entry satisfying all mark criteria ###
        pass
    def save_note(self):
        ### write a note to the source ###
        pass
    def close_note(self):
        ### if applicable, close a note; could mean clearing some pointers ###
        pass
    def search(self,*marks):
        ### search available notes by either name or marks; maybe split into two methods? ###
        pass
    def get_active_open(self):
        ### last used dir for opening ###
        pass
    def set_active_open(self,d):
        pass
    def get_active_save(self):
        ### last used dir for saving ###
        pass
    def set_active_save(self,d):
        pass
    def get_active_base(self):
        ### conf file's source dir ###
        pass
    def set_active_base(self,d):
        pass
    def set_index(self,dex):
        pass



def _mime_open(fname,index=None):
    if not fname:
        return None
    try:
        m = magic.open(magic.NONE)
        m.load()
        file_type = m.file(fname)
    except Exception as e:
        raise Exception(e)
    else:
        tmp_type = file_type.lower()
        if tmp_type.find("text") >= 0:
            return _targeted_text(fname)
        if tmp_type.find("image") >= 0:
            return _targeted_image(fname,index)
        if tmp_type.find("pdf") >= 0:
            return None
        return None

    
def _targeted_text(name):
    try:
        with open(name,"r") as file_handle:
            if file_handle is not None:
                newnt = Note()
                newnt.title = os.path.basename(name)
                newnt.ID = name
                newnt.body = ""
                newnt.mime = NoteMime.TEXT
            for l in file_handle.readlines():
                newnt.body += l
                #askopenfilenames does not leave the "10" char, and this next command removes its line feeds.#
                #if curses.ascii.isctrl(newnt.text[len(newnt.text)-1]):
                #    newnt.text = newnt.text[:len(newnt.text)-1]
            file_handle.close()
    except Exception as e:
        raise Exception(e)
        #print(e)
        #self._error.append(e)
    else:
        newnt.parse()
        return newnt

    
def _targeted_image(name,index=None):
    try:
        newnt = Note()
        newnt.title = os.path.basename(name)
        newnt.ID = name
        #with PIL.Image.open(name) as img_src:
        #    newnt.body = img_src
        newnt.body = PIL.Image.open(name)
        newnt.mime = NoteMime.IMAGE
        if index:
            target = None
            tmp_files = index["file"]
            if isinstance(tmp_files,extconf.Configuration):
                if tmp_files["loc"] == name:
                    target = tmp_files
            else:
                for f in tmp_files:
                    if f["loc"] == name:
                        target = f
                        break
            if target:
                tmp_marks = target["mark"]
                if isinstance(tmp_marks,str):
                    newnt.tags = [ tmp_marks ]
                else:
                    newnt.tags = list(tmp_marks)
    except Exception as e:
        raise Exception(e)
    else:
        return newnt
    





    
### File-tree implementation of Binding ###


class FileBinding(Binding):
    __ctrl = None
    __toc = {}
    def __init__(self,ctrl):       # an ExternalConfiguration is still required because I may want to use encoding options, etc, as the project grows
        self.__ctrl = ctrl
        src = ctrl["loc"]
        if src is None:
            p = pathlib.Path(".")
        else:
            p = pathlib.Path(src)
        if not ( p.exists() and p.is_dir() ):
            p = pathlib.Path(".")
        if os.access(p,os.R_OK | os.W_OK):
            self._src = p
        else:
            self._error.append(Exception("Inadequate permissions for file source"))
                    
    def list(self):
        if self._src:
            print("CWD is: " + str(os.getcwd()) )
            print(os.listdir())

    def set_source(self,s):
        p = pathlib.Path(s)
        if (p.exists() and p.is_dir()):
            if os.access(p,os.R_OK | os.W_OK):
                self._src = p
                return False
            else:
                self._error.append(Exception("Inadequate permissions for file source"))
                return True
        else:
            self._error.append(Exception("Invalid path for file source"))
            return True
            
    def get_last_error(self):
        if self._error:
            return self._error.pop(len(self._error)-1)
        else:
            return None

    def open_note(self,nl=[]):
        if not nl:
            return None
        else:
            file_names = [ n for n in nl ]
        note_list = []
        for name in file_names:
            try:
                note_list.append( _mime_open(name) )
            except Exception as e:
                self._error.append(e)
            else:
                continue
        return note_list

    def open_from_toc(self,ls):
        if not ls:
            return None
        research_list = [ item for sublist in [ self.__toc[entry] for entry in ls ] for item in sublist ]
        return self.open_note(research_list)

    def open_from_toc_intersection(self,ls):
        if not ls:
            return None
        research_list = []
        for entry in ls:
            research_list.append(self.__toc[entry])
        intersect_set = set.intersection( *(set(item) for item in research_list) )
        return self.open_note(list(intersect_set))
    
    def save_note(self,nt):
        if nt is None:
            e = Exception("set_save_as argument requires note object")
            self._error.append(e)
            return True
        if nt.mime is not NoteMime.TEXT:
            # silent fail: writing is not supported for images or pdfs
            return False
        try:
            handle = open(nt.ID,"w")
            handle.write(nt.body)
            handle.close()
        except Exception as e:
            self._error.append(e)
            return True
        else:
            return False

    def __process_file(self,f):
        try:
            suffices = self.__ctrl["mime"]["Text"]["suff"]
            if isinstance(suffices,str):
                if str(f).rfind(suffices) < len(str(f))-len(suffices)-1 :
                    return
            else:
                success = False
                for suff in suffices:
                    if str(f).rfind(suff) < len(str(f))-len(suffices)-1 :
                        continue
                    else:
                        success = True
                        break
                if not success:
                    return
            handle_text = ""
            with open(f,"r") as handle:
                for l in handle.readlines():
                    handle_text += l
        except Exception as e:
            wrapper = Exception("<  " + str(f) + "  >  " + str(e))
            self._error.append(wrapper)
            return
        return parse.parse(handle_text)
        
    def __delve(self,directory):
        file_tree = os.listdir(directory)
        for s in file_tree:
            f = pathlib.Path(directory / pathlib.Path(s))
            if ( f.is_symlink() ):
                link_result = pathlib.Path( os.path.join( os.path.dirname(f), os.readlink(f) ) )
                if link_result.is_file():
                    if str(link_result).find(os.getcwd())<0 :
                        marks = self.__process_file(f)
                        if marks is None:
                            continue
                        for m in marks:
                            if m in self.__toc.keys():
                                self.__toc[m].append(f)
                            else:
                                self.__toc[m] = [ f ]
                    else:
                        continue
                if link_result.is_dir() :
                    if str(link_result).find(os.getcwd())<0 :
                        self.__delve(link_result)
                    else:
                        continue
            elif ( f.is_file() ):
                marks = self.__process_file(f)
                if marks is None:
                    continue
                for m in marks:
                    if m in self.__toc.keys():
                        self.__toc[m].append(f)
                    else:
                        self.__toc[m] = [ f ]
            elif ( f.is_dir() ):
                self.__delve(str(f))
        
    def populate(self):
        self.__toc = {}
        for directory in self.__ctrl["db"]["scan"]:
            self.__delve(pathlib.Path(directory) )

    def clear(self):
        pass

    def toc(self):
        return self.__toc.keys()

    def get_active_open(self):
        if "open" in self.__ctrl.keys():
            return self.__ctrl["open"]
        else:
            return self.__ctrl["loc"]

    def set_active_open(self,d):
        self.__ctrl["open"] = d

    def get_active_save(self):
        if "save" in self.__ctrl.keys():
            return self.__ctrl["save"]
        else:
            return self.__ctrl["loc"]

    def set_active_save(self,d):
        self.__ctrl["save"] = d

    def get_active_base(self):
        return self._src

    def set_active_base(self,d):
        self.set_source(d)
        self.__ctrl["loc"] = d



    

        
        



######  SQLite implementation of Binding ######

    

class DatabaseBinding(Binding):

    __db_name = None
    __scan_list = None
    __base_dir = None
    __ctrl = None
    __cursor = None
    __dex = None
    
    def __init__(self,ctrl):
        self.__ctrl = ctrl
        self.__db_name = str(ctrl["loc"]+os.sep+ctrl["db"]["src"])
        try:
            self._src = sqlite3.connect(self.__db_name)
        except Exception as e:
            self._error.append(e)
        else:
            self.__load_table()

    def set_source(self,db):
        if self._src:
            self._src.close()
        try:
            self.__db_name = db
            self._src = sq3lite.connect(db)
        except Exception as e:
            self._error.append(e)
            return True
        else:
            self.__load_table()
            return False

    def __load_table(self):
        try:
            self.__cursor = self._src.cursor()
            self.__cursor.execute('''select * from sqlite_master where type="table" and name="bookmarks"''',)
            if self.__cursor.fetchone() is None:
                self.__cursor.execute('''create table bookmarks (mark NCHAR(255) NOT NULL,file NCHAR(1023) NOT NULL,type SMALLINT);''')
                self._src.commit()
        except Exception as e:
            self._error.append(e)

    def get_last_error(self):
        if self._error:
            return self._error.pop(len(self._error)-1)
        else:
            return None

    def set_index(self,dex):
        self.__dex = dex
        
    def __load_index(self):
        files = self.__dex["file"]
        for f in files:
            loc = f["loc"]
            if not os.access(loc,os.R_OK):
                self.clear(("file",loc))
                extconf.remove_configuration(self.__dex,"file",f)
            else:
                tmp_marks = f["mark"]
                if isinstance(tmp_marks,str):
                    marks = [ tmp_marks ]
                elif isinstance(tmp_marks,tuple) or isinstance(tmp_marks,list):
                    marks = f["mark"]
                else:
                    # is a Configuration. Undecided course of action.
                    pass
                for mark in marks:
                    self.__cursor.execute('''SELECT mark,file FROM bookmarks WHERE mark=? AND file=? AND type=?''',(mark,loc,f.get_attr("type")))
                    hit_list = self.__cursor.fetchall()
                    if hit_list:
                        continue
                    else:
                        self.__cursor.execute('''INSERT INTO bookmarks(mark,file,type) VALUES(?,?,?)''',(str(mark),str(loc),f.get_attr("type")))
        self._src.commit()
        
    def populate(self):
        if not self._src:
            return
        if isinstance(self.__ctrl["db"]["scan"],str):
            self.__scan_list = [ self.__ctrl["db"]["scan"] ]
        else:
            self.__scan_list = list(self.__ctrl["db"]["scan"])
        if self.__scan_list:
            for dir_name in self.__scan_list:
                self.__delve(pathlib.Path(dir_name))
                self._src.commit()
            if self._error:
                print("Errors were encountered while populating database:")
                for error in self._error:
                    print(error)
                self._error = []
        if self.__dex:
            self.__load_index()
            if self._error:
                for error in self._error:
                    print(error)
                self._error = []

        
    def __process_file(self,f):
        try:
            suffices = self.__ctrl["mime"]["Text"]["suff"]
            if isinstance(suffices,str):
                if str(f).rfind(suffices) < len(str(f))-len(suffices)-1 :
                    return
            else:
                success = False
                for suff in suffices:
                    if str(f).rfind(suff) < len(str(f))-len(suffices)-1 :
                        continue
                    else:
                        success = True
                        break
                if not success:
                    return
            handle_text = ""
            with open(f,"r") as handle:
                for l in handle.readlines():
                    handle_text += l
        except Exception as e:
            wrapper = Exception("<  " + str(f) + "  >  " + str(e))
            self._error.append(wrapper)
            return
        marks = parse.parse(handle_text)
        for m in marks:
            self.__cursor.execute('''SELECT mark,file FROM bookmarks WHERE mark=? AND file=? AND type=?''',(m,str(f),NoteMime.TEXT.value))
            hit_list = self.__cursor.fetchall()
            if hit_list:
                continue
            else:
                self.__cursor.execute('''INSERT INTO bookmarks(mark,file,type) VALUES(?,?,?)''',(m,str(f),NoteMime.TEXT.value))
        return
        
    def __delve(self,directory):
        file_tree = os.listdir(directory)
        for s in file_tree:
            f = pathlib.Path(directory / pathlib.Path(s))
            if ( f.is_symlink() ):
                link_result = pathlib.Path(os.path.realpath(f))
                if link_result.is_file():
                    if str(link_result).find(str(directory))<0 :
                        self.__process_file(f)
                    else:
                        continue
                if link_result.is_dir() :
                    if str(link_result).find(str(directory))<0 :
                        self.__delve(link_result)
                    else:
                        continue
            elif ( f.is_file() ):
                self.__process_file(f)
            elif ( f.is_dir() ):
                self.__delve(f)
                
    def toc(self):
        self.__cursor.execute('''select distinct mark from bookmarks''')
        mark_tuple = self.__cursor.fetchall()
        toc_list = []
        for mt in mark_tuple:
            toc_list.append(mt[0])
        return toc_list
    
    def clear(self,targetpair=()):
        if self.__cursor:
            if targetpair is ():
                self.__cursor.execute('''drop table bookmarks''')
                self._src.commit()
                self.__load_table()
            else:
                parameters = ( targetpair[0],targetpair[1], )
                self.__cursor.execute('''delete from bookmarks where ?=?''',parameters)

    def get_active_open(self):
        if "open" in self.__ctrl.keys():
            return self.__ctrl["open"]
        else:
            return self.__ctrl["loc"]

    def set_active_open(self,d):
        self.__ctrl["open"] = d

    def get_active_save(self):
        if "save" in self.__ctrl.keys():
            return self.__ctrl["save"]
        else:
            return self.__ctrl["loc"]

    def set_active_save(self,d):
        self.__ctrl["save"] = d

    def get_active_base(self):
        return self.__ctrl["loc"]

    def set_active_base(self,d):
        self.__ctrl["loc"] = d
            
    def open_note(self,nl=[]):
        ### retrieve a note from source ###
        if not nl:
            return None
        else:
            file_names = [ n for n in nl ]
        note_list = []
        for name in file_names:
            try:
                note_list.append( _mime_open(name,self.__dex) )
            except Exception as e:
                self._error.append(e)
            else:
                continue
        return note_list

    def open_from_toc(self,ls):
        if not ls:
            return None
        research_list = []
        for item in ls:
            self.__cursor.execute('''select file from bookmarks where mark=?''',(item,))
            for result in self.__cursor.fetchall():
                research_list.append(result[0])
        return self.open_note(research_list)

    def open_from_toc_intersection(self,ls):
        if not ls:
            return None
        research_list = []
        ### cannot query as where 'mark = ? and ? and ?' because DB is built with one mark per file.
        ### hence, every record will fail the truth test. instead, must build lists of files for each mark,
        ### then find the intersection of these file lists.
        for entry in ls:
            self.__cursor.execute('''select file from bookmarks where mark=?''',(entry,))
            buffer_list = []
            for result in self.__cursor.fetchall():
                buffer_list.append(result[0])
            research_list.append(buffer_list)
        intersect = list(set.intersection(*(set(item) for item in research_list)))
        if not intersect:
            return None
        return self.open_note(intersect)
    
    def save_note(self,nt):
        ### write a note to the source ###
        if nt is None:
            e = Exception("set_save_as argument requires note object")
            self._error.append(e)
            return True
        if nt.mime is not NoteMime.TEXT:
            # silent fail: writing is not supported for images or pdfs
            ### here i must implement xml tag rewrite for any changes in marks to the image/pdf/whatever ###
            return False
        ### compare/update marks ###
        nt.tags = parse.parse(nt.body)
        self.__cursor.execute('''select rowid,mark from bookmarks where file=?''',(nt.ID,))
        db_hits = self.__cursor.fetchall()
        for item in db_hits:
            if not (item[1] in nt.tags):
                self.__cursor.execute('''delete from bookmarks where rowid=?''',(item[0],))
        self._src.commit()
        for tag in nt.tags:
            if not (tag in [ item[1] for item in db_hits ]):
                self.__cursor.execute('''insert into bookmarks (mark,file,type) values (?,?,?)''',(tag,nt.ID,nt.mime.value))
        self._src.commit()
        try:
            handle = open(nt.ID,"w")
            handle.write(nt.body)
            handle.close()
        except Exception as e:
            self._error.append(e)
            return True
        else:
            return False

    def close_note(self):
        ### if applicable, close a note; could mean clearing some pointers ###
        pass

    def update(self,nt,marks):
        if (not nt.tags) and (not marks):
                return
        nt.tags = marks
        # find the file in the index ( update or create it )
        target = None
        tmp_files = self.__dex["file"]
        if isinstance(tmp_files,extconf.Configuration):
            if tmp_files["loc"] == nt.ID:
                target = tmp_files
        else:
            for f in tmp_files:
                if f["loc"] == nt.ID:
                    target = f
                    break
        if target:
            target["mark"] = marks
        else:
            newc = extconf.Configuration(self.__dex.getdoc())
            extconf.fill_configuration(newc,"file",members={"loc":nt.ID,"mark":[item for item in nt.tags]},attributes={"type":nt.mime.value})
            extconf.attach_configuration(self.__dex,"file",newc)

    def __del__(self):
        if self._src:
            self._src.close()
        self._error = None

