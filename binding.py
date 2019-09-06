# v. 05

import os
import pathlib
import sys
from note import Note
import parse
import magic

import sqlite3



class Binding():
    _src = None   # could file base directory, database connection
    _error = []
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
            #print(magic.from_file(name))
            try:
                file_handle = open(name,"r")
                if file_handle is not None:
                    newnt = Note()
                    newnt.title =os.path.basename(name)
                    newnt.ID = name
                    for l in file_handle.readlines():
                        newnt.text += l
                        #askopenfilenames does not leave the "10" char, and this next command removes its line feeds.#
                        #if curses.ascii.isctrl(newnt.text[len(newnt.text)-1]):
                        #    newnt.text = newnt.text[:len(newnt.text)-1]
                    file_handle.close()
            except Exception as e:
                self._error.append(e)
            else:
                newnt.parse()
                note_list.append(newnt)
        return note_list

    def save_note(self,nt):
        if nt is None:
            e = Exception("set_save_as argument requires note object")
            self._error.append(e)
            return True
        try:
            handle = open(nt.ID,"w")
            handle.write(nt.text)
            handle.close()
        except Exception as e:
            #print("File could not be written due to error: " + str(e) )
            #return None
            self._error.append(e)
            return True
        else:
            return False

    def __process_file(self,f):
        try:
            m = magic.open(magic.NONE)
            m.load()
            ### the following needs to be moved to conf.xml or something :  ###
            file_type = m.file(f)
            if not ( (file_type.find("ASCII text")==0) or (file_type.find("UTF-8 Unicode text")==0) or (file_type.find("UTF-8 Unicode (with BOM) text")==0) ):
                #print("rejecting " + str(f))
                return None
            handle = open(f,"r")
            handle_text = ""
            for l in handle.readlines():
                handle_text += l
            handle.close()
        except Exception as e:
            self._error.append(e)
            return None
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
        ret_list = []
        for key,vals in self.__toc.items():
            tmp_list = [ item for item in vals ]
            tmp_list.insert(0,key)
            ret_list.append(tmp_list)
        return ret_list

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
                self.__cursor.execute('''create table bookmarks (mark NCHAR(255) NOT NULL,file NCHAR(1023) NOT NULL);''')
                self._src.commit()
        except Exception as e:
            self._error.append(e)

    def get_last_error(self):
        if self._error:
            return self._error.pop(len(self._error)-1)
        else:
            return None

    def populate(self):
        self.__scan_list = list(self.__ctrl["db"]["scan"])
        if self.__scan_list:
            for dir_name in self.__scan_list:
                self.__delve(pathlib.Path(dir_name))
                self._src.commit()
        
    def __process_file(self,f):
        try:
            ##### the following doesn't solve the text-vs-other problem, and needs to be implemented via conf.xml otherwise:  ########
            #if str(f).rfind(self.__ctrl["suff"]) < len(str(f))-len(self.__ctrl["suff"])-1 :
            #    m = magic.open(magic.NONE)
            #    m.load()
            #    file_type = m.file(f)
            #    if not ( (file_type.find("ASCII text")==0) or (file_type.find("UTF-8 Unicode text")==0) or (file_type.find("UTF-8 Unicode (with BOM) text")==0) ):
            #        return
            ############################################################################################################################
            if str(f).rfind(self.__ctrl["suff"]) < len(str(f))-len(self.__ctrl["suff"])-1 :
                return
            handle = open(f,"r")
            handle_text = ""
            for l in handle.readlines():
                handle_text += l
            handle.close()
        except Exception as e:
            self._error.append(e)
            return
        marks = parse.parse(handle_text)
        for m in marks:
            self.__cursor.execute('''SELECT mark,file FROM bookmarks WHERE mark=? AND file=?''',(m,str(f)))
            hit_list = self.__cursor.fetchall()
            if hit_list:
                continue
            else:
                self.__cursor.execute('''INSERT INTO bookmarks(mark,file) VALUES(?,?)''',(m,str(f)))
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
        for mark in mark_tuple:
            self.__cursor.execute('''select file from bookmarks where mark=?''',mark)
            query_list = [ item[0] for item in self.__cursor.fetchall() ]
            query_list.insert(0,mark[0])
            toc_list.append( query_list )
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
                file_handle = open(name,"r")
                if file_handle is not None:
                    newnt = Note()
                    newnt.title =os.path.basename(name)
                    newnt.ID = name
                    for l in file_handle.readlines():
                        newnt.text += l
                        #askopenfilenames does not leave the "10" char, and this next command removes its line feeds.#
                        #if curses.ascii.isctrl(newnt.text[len(newnt.text)-1]):
                        #    newnt.text = newnt.text[:len(newnt.text)-1]
                    file_handle.close()
            except Exception as e:
                self._error.append(e)
            else:
                newnt.parse()
                note_list.append(newnt)
        return note_list
    
    def save_note(self,nt):
        ### write a note to the source ###
        if nt is None:
            e = Exception("set_save_as argument requires note object")
            self._error.append(e)
            return True
        ### compare/update marks ###
        nt.tags = parse.parse(nt.text)
        self.__cursor.execute('''select rowid,mark from bookmarks where file=?''',(nt.ID,))
        db_hits = self.__cursor.fetchall()
        for item in db_hits:
            if not (item[1] in nt.tags):
                self.__cursor.execute('''delete from bookmarks where rowid=?''',(item[0],))
        self._src.commit()
        for tag in nt.tags:
            if not (tag in [ item[1] for item in db_hits ]):
                self.__cursor.execute('''insert into bookmarks (mark,file) values (?,?)''',(tag,nt.ID,))
        self._src.commit()
        try:
            handle = open(nt.ID,"w")
            handle.write(nt.text)
            handle.close()
        except Exception as e:
            self._error.append(e)
            return True
        else:
            return False

    def close_note(self):
        ### if applicable, close a note; could mean clearing some pointers ###
        pass

    def __del__(self):
        if self._src:
            self._src.close()
        self._error = None






        
######### obsolete ####################
### i must find a better way to implement unique id numbers!! ###
#class UniqueHolder:
#    def __init__(self,b=-1):
#        self.__val = b
#        
#    def  __call__(self):
#        self.__val+=1
#        return self.__val
#
#    def __str__(self):
#        self.__val += 1
#        return str(self.__val)
