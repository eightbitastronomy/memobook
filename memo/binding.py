###############################################################################################
#  binding.py: file & database backend
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



'''Source binding classes for memobook'''


import os
import magic
import sqlite3
from PIL import Image
from pathlib import Path
from io import BufferedReader, TextIOWrapper
import memo.parse as parse
import memo.extconf as extconf
from pdf2image import convert_from_path
from memo.note import Note, NoteMime, Tag
from memo.debug import dprint



class Binding():
    _src = None   # could file base directory, database connection
    _error = None
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



def _mime_open(fname, index=None):
    '''Binding utility: detect mime and dispatch relevant opening function. First stage in file opening.'''
    dprint(3, '''\nDatabaseBinding::_mime_open:: "''' + str(fname) + '''"''' )
    if not fname:
        return None
    try:
        m = magic.open(magic.NONE)
        m.load()
        file_type = m.file(fname)
    except Exception as e:
        dprint(2, "Error detecting mime type: " + str(e) + " Aborting::\n")
        raise Exception(e)
    else:
        tmp_type = file_type.lower()
        if tmp_type.find("text") >= 0:
            return _targeted_text(fname, index)
        if tmp_type.find("image") >= 0:
            return _targeted_image(fname, index)
        if tmp_type.find("pdf") >= 0:
            return _targeted_pdf(fname, index)
        dprint(3, "Magic type: " + tmp_type)
        # if we've reached here, we don't know the mime. _targeted_unknown will be our default case
        return _targeted_unknown(fname, index)


def _targeted_unknown(name, index=None):
    '''Binding utility: open unknown file type'''
    # open in binary mode and attempt to handle as text
    try:
        with open(name, "rb") as file_handle:
            #if file_handle is not None: #I think this is unnecessary. open should throw an exception if it can't open the file.
            buffered = BufferedReader(file_handle)
            wrapped = TextIOWrapper(buffered)
            newnt = Note()
            newnt.title = os.path.basename(name)
            newnt.ID = name
            newnt.body = ""
            newnt.mime = NoteMime.TEXT
            for l in wrapped:
                newnt.body += l
            newnt.parse()
        if index: 
            newnt.tags.silent = index_search(index, name, newnt)
    except Exception as e:
        raise Exception(e)
    else:
        return newnt

    
def _targeted_text(name, index=None):
    '''Binding utility: open text file'''
    try:
        with open(name, "r") as file_handle:
            #if file_handle is not None:  #I think this is unnecessary. open should throw an exception if it can't open the file.
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
            newnt.parse()
        if index: 
            newnt.tags.silent = index_search(index, name, newnt)
    except Exception as e:
        raise Exception(e)
    else:
        return newnt

    
def _targeted_image(name, index=None):
    '''Binding utility: open image file'''
    try:
        newnt = Note()
        newnt.title = os.path.basename(name)
        newnt.ID = name
        newnt.body = Image.open(name)
        newnt.mime = NoteMime.IMAGE
        newnt.tags = Tag(index_search(index, name, newnt))
    except TypeError as ke:
        return newnt
    except KeyError as ke:
        return newnt
    except Exception as e:
        raise Exception(e)
    else:
        return newnt


def _targeted_pdf(name, index=None):
    '''Binding utility: open pdf file'''
    try:
        newnt = Note()
        newnt.title = os.path.basename(name)
        newnt.ID = name
        newnt.body = convert_from_path(name)
        newnt.mime = NoteMime.PDF
        newnt.tags = Tag(index_search(index, name, newnt))
    except TypeError as ke:
        return newnt
    except KeyError as ke:
        return newnt
    except Exception as e:
        raise Exception(e)
    else:
        return newnt


def index_search(index, fname, note):
    '''Binding utility: Search silent index for entry based on file name'''
    try:
        target = None
        if index and ("file" in index.keys()):
            tmp_files = index["file"]
            if isinstance(tmp_files, extconf.Configuration):
                if tmp_files["loc"] == fname:
                    target = tmp_files
            else:
                for f in tmp_files:
                    if f["loc"] == fname:
                        target = f
                        break
            if target:
                if "mark" in target.keys():
                    tmp_marks = target["mark"]
                    if isinstance(tmp_marks, str):
                        return [tmp_marks]
                    else:
                        return list(tmp_marks)
            return []
    except Exception as e:
        raise(e)



    
### File-tree implementation of Binding ###



### maintenance of FileBinding is ceased, or at least lagging.
### I last updated it to use _mime_open, but have not kept up
### with any indexing changes or other changes. Preferably,
### do not use it until it is brought up-to-date with DatabaseBinding.

class FileBinding(Binding):
    __ctrl = None
    __toc = None
    def __init__(self,ctrl):       # an ExternalConfiguration is still required because I may want to use encoding options, etc, as the project grows
        self._error = []
        self.__toc = {}
        self.__ctrl = ctrl
        src = ctrl["loc"]
        if src is None:
            p = Path(".")
        else:
            p = Path(src)
        if not ( p.exists() and p.is_dir() ):
            p = Path(".")
        if os.access(p,os.R_OK | os.W_OK):
            self._src = p
        else:
            self._error.append(Exception("Inadequate permissions for file source"))
                    
    def list(self):
        if self._src:
            print("CWD is: " + str(os.getcwd()) )
            print(os.listdir())

    def set_source(self,s):
        p = Path(s)
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
            f = Path(directory / Path(s))
            if ( f.is_symlink() ):
                link_result = Path( os.path.join( os.path.dirname(f), os.readlink(f) ) )
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
            self.__delve(Path(directory) )

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

    '''Interface to SQLite3 database'''

    __db_name = None
    __scan_list = None
    __base_dir = None
    __ctrl = None
    __cursor = None
    __dex = None

    
    def __init__(self, ctrl):
        dprint(3, "\nDatabaseBinding::init")
        self._error = []
        self.__ctrl = ctrl
        #the following assumes a relative path, but the config script will
        #use an absolute one so that the user may call memobook from any PWD
        #self.__db_name = str(ctrl["loc"]+os.sep+ctrl["db"]["src"])
        self.__db_name = ctrl["db"]["src"]
        try:
            self._src = sqlite3.connect(self.__db_name)
        except Exception as e:
            dprint(1, "\nDatabaseBinding::init: cannot connect to database")
            self._error.append(e)
        else:
            self.__load_table()

            
    def set_source(self, db):
        '''Set memobook database file and connect to it'''
        dprint(3, "\nDatabaseBinding::set_source")
        if self._src:
            self._src.close()
        try:
            self.__db_name = db
            self._src = sq3lite.connect(db)
        except Exception as e:
            dprint(1, "\nDatabaseBinding::set_source: cannot connect to database")
            self._error.append(e)
            return True
        else:
            self.__load_table()
            return False

        
    def __load_table(self):
        '''Check for bookmarks table, and create one if not found'''
        dprint(3, "\nDatabaseBinding::__load_table")
        try:
            self.__cursor = self._src.cursor()
            self.__cursor.execute('''select * from sqlite_master where type="table" and name="bookmarks"''',)
            if self.__cursor.fetchone() is None:
                self.__cursor.execute('''create table bookmarks (mark NCHAR(255) NOT NULL,file NCHAR(1023) NOT NULL,type SMALLINT);''')
                self._src.commit()
        except Exception as e:
            dprint(1, "\nDatabaseBinding::__load_table: error executing, fetching, committing.")
            self._error.append(e)

            
    def get_last_error(self):
        '''Pop most recent DatabaseBinding exception and return it'''
        if self._error:
            return self._error.pop(len(self._error)-1)
        else:
            return None

        
    def set_index(self, dex):
        '''Set silent index reference'''
        self.__dex = dex

        
    def __load_index(self):
        '''Load silent index information'''
        dprint(3, "\nDatabaseBinding::__load_index")
        try:
            files = self.__dex["file"]
        except:
            return
        # because of the nature of the extconf class,
        # typechecking must be performed on "file" item and its contents
        if isinstance(files, extconf.Configuration):
            # for an extconf, simply place it in a list, since this is what will be expected next
            files = ( files, )
        for f in files:
            loc = f["loc"]
            if not os.access(loc, os.R_OK):
                # remove any troublesome entries
                self.clear(("file", loc))
                extconf.remove_configuration(self.__dex, "file", f)
            else:
                tmp_marks = f["mark"]
                if isinstance(tmp_marks, str):
                    # a single str should be placed in a list
                    marks = [ tmp_marks ]
                elif isinstance(tmp_marks, tuple) or isinstance(tmp_marks, list):
                    # tuples or lists can be used as-is
                    marks = f["mark"]
                else:
                    # is a Configuration. Undecided course of action.
                    pass
                for mark in marks:
                    self.__cursor.execute('''SELECT mark,file FROM bookmarks WHERE mark=? AND file=? AND type=?''',
                                          (mark,loc, f.get_attr("type")))
                    hit_list = self.__cursor.fetchall()
                    if hit_list:
                        continue
                    else:
                        self.__cursor.execute('''INSERT INTO bookmarks(mark,file,type) VALUES(?,?,?)''',
                                              (str(mark), str(loc), f.get_attr("type")))
        self._src.commit()

        
    def populate(self):
        '''Scan sources for files with marks'''
        dprint(3, "\nDatabaseBinding::populate")
        if not self._src:
            return
        try:
            if isinstance(self.__ctrl["db"]["scan"], str):
                self.__scan_list = [ self.__ctrl["db"]["scan"] ]
            else:
                self.__scan_list = list(self.__ctrl["db"]["scan"])
        except:
            # create a node and attach it
            newc = extconf.Configuration(self.__dex.getdoc())
            extconf.fill_configuration(newc, "db", members={"scan":"."})
            extconf.attach_configuration(self.__dex, "db", newc)
        if self.__scan_list:
            for dir_name in self.__scan_list:
                self.__delve(Path(dir_name))
                self._src.commit()
            if self._error:
                dprint(1, "\nDatabaseBinding::populate: Errors were encountered while populating database")
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
        '''Helper function for populate: if file is text, load its marks'''
        dprint(3, "\nDatabaseBinding::__process_file")
        try:
            suffices = self.__ctrl["mime"]["Text"]["suff"]
            if isinstance(suffices, str):
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
            with open(f, "r") as handle:
                for l in handle.readlines():
                    handle_text += l
        except Exception as e:
            wrapper = Exception("<  " + str(f) + "  >  " + str(e))
            self._error.append(wrapper)
            return
        marks = parse.parse(handle_text)
        dprint(4, " MARKS: " + ", ".join(marks))
        for m in marks:
            self.__cursor.execute('''SELECT mark,file FROM bookmarks WHERE mark=? AND file=? AND type=?''',
                                  (m, str(f), NoteMime.TEXT.value))
            hit_list = self.__cursor.fetchall()
            if hit_list:
                continue
            else:
                self.__cursor.execute('''INSERT INTO bookmarks(mark,file,type) VALUES(?,?,?)''',
                                      (m, str(f), NoteMime.TEXT.value))
        return

    
    def __delve(self, directory):
        '''Helper function for populate: recursive directory search'''
        dprint(3, "\nDatabaseBinding::__delve")
        file_tree = os.listdir(directory)
        for s in file_tree:
            f = Path(directory / Path(s))
            dprint(4, "\nDatabaseBinding::__delve:FILE " + str(f))
            if ( f.is_symlink() ):
                link_result = Path(os.path.realpath(f))
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
            elif f.is_file():
                self.__process_file(f)
            elif f.is_dir():
                self.__delve(f)

                
    def toc(self):
        '''Return list of marks in memobook'''
        dprint(3, "\nDatabaseBinding::toc")
        self.__cursor.execute('''select distinct mark from bookmarks''')
        mark_tuple = self.__cursor.fetchall()
        toc_list = []
        for mt in mark_tuple:
            toc_list.append(mt[0])
        return toc_list

    
    def clear(self, targetpair=()):
        '''Clear the database: drop bookmarks table and create a new one'''
        dprint(3, "\nDatabaseBinding::clear")
        if self.__cursor:
            if targetpair is ():
                self.__cursor.execute('''drop table bookmarks''')
                self._src.commit()
                self.__load_table()
            else:
                parameters = ( targetpair[0], targetpair[1], )
                self.__cursor.execute('''delete from bookmarks where ?=?''', parameters)
                

    def get_active_open(self):
        '''Get last directory used for file opening, ctrl[open]'''
        dprint(3, "\nDatabaseBinding::get_active_open")
        if "open" in self.__ctrl.keys():
            return self.__ctrl["open"]
        else:
            return self.__ctrl["loc"]

        
    def set_active_open(self, d):
        '''Set ctrl[open] with last directory used for file opening'''
        dprint(3, "\nDatabaseBinding::set_active_open")
        self.__ctrl["open"] = d

        
    def get_active_save(self):
        '''Get last directory used for file saving, ctrl[save]'''
        dprint(3, "\nDatabaseBinding::get_active_save")
        if "save" in self.__ctrl.keys():
            return self.__ctrl["save"]
        else:
            return self.__ctrl["loc"]

        
    def set_active_save(self, d):
        '''Set ctrl[save] with last directory used for file saving'''
        dprint(3, "\nDatabaseBinding::set_active_save")
        self.__ctrl["save"] = d

        
    def get_active_base(self):
        '''Get base directory, ctrl[loc]'''
        dprint(3, "\nDatabaseBinding::get_active_base")
        return self.__ctrl["loc"]

    
    def set_active_base(self, d):
        '''Set ctrl[base] with new base directory'''
        dprint(3, "\nDatabaseBinding::set_active_base")
        self.__ctrl["loc"] = d

        
    def open_note(self, nl=[]):
        '''Retrieve a note / list of notes from source'''
        dprint(3, "\nDatabaseBinding::open_note:: ")
        if not nl:
            return None
        else:
            file_names = [ n for n in nl ]
        note_list = []
        for name in file_names:
            try:
                note_list.append(_mime_open(name, self.__dex))
            except Exception as e:
                dprint(1, "Error in mime_open: " + str(e) + " Aborting::\n")
                self._error.append(e)
            else:
                continue
        return note_list

    
    def open_from_toc(self, ls):
        '''Retrieve note by mark(s) using OR logic / union of sets'''
        dprint(3, "\nDatabaseBinding::open_from_toc")
        if not ls:
            return None
        research_list = []
        if len(ls) > 1:
            query_string = '''select file from bookmarks where mark=?'''
            for item in ls[1:]:
                query_string += ''' union select file from bookmarks where mark=?'''
            self.__cursor.execute(query_string, tuple(ls))
        else:
            self.__cursor.execute('''select file from bookmarks where mark=?''', (ls[0],))
        for result in self.__cursor.fetchall():
            research_list.append(result[0])
        return self.open_note(research_list)
    

    def open_from_toc_intersection(self, ls):
        '''Retrieve note by mark(s) using AND logic / intersection of sets'''
        dprint(3, "\nDatabaseBinding::open_from_toc_intersection")
        if not ls:
            return None
        research_list = []
        ### cannot query as where 'mark = ? and ? and ?' because DB is built with one mark per file.
        ### hence, every record will fail the truth test. instead, must build lists of files for each mark,
        ### then find the intersection of these file lists.
        for entry in ls:
            self.__cursor.execute('''select file from bookmarks where mark=?''', (entry,))
            buffer_list = []
            for result in self.__cursor.fetchall():
                buffer_list.append(result[0])
            research_list.append(buffer_list)
        intersect = list(set.intersection(*(set(item) for item in research_list)))
        if not intersect:
            return None
        return self.open_note(intersect)
    
    
    def save_note(self, nt):
        '''Write a note to the source. Only text files are written; others silently fail.'''
        dprint(3, "\nDatabaseBinding::save_note")
        # this could be problematic for default/unknown mime loading.
        # ...if an unk type is displayed as text, why wouldn't the user expect
        # ...the write operation to succeed?
        if nt is None:
            e = Exception("save_note argument requires note object")
            self._error.append(e)
            return True
        if nt.mime is not NoteMime.TEXT:
            # silent fail: writing is not supported for images or pdfs
            return False
        ### compare/update marks ###
        nt.tags = Tag(parse.parse(nt.body))
        self.__cursor.execute('''select rowid,mark from bookmarks where file=?''',
                              (nt.ID, ))
        db_hits = self.__cursor.fetchall()
        for item in db_hits:
            if not (item[1] in nt.tags):
                self.__cursor.execute('''delete from bookmarks where rowid=?''',
                                      (item[0], ))
        self._src.commit()
        for tag in nt.tags:
            if not (tag in [ item[1] for item in db_hits ]):
                self.__cursor.execute('''insert into bookmarks (mark,file,type) values (?,?,?)''',
                                      (tag, nt.ID, nt.mime.value))
        self._src.commit()
        try:
            handle = open(nt.ID, "w")
            handle.write(nt.body)
            handle.close()
        except Exception as e:
            self._error.append(e)
            return True
        else:
            return False

        
    def save_note_nowrite(self, nt):
        '''Write note information to the source without writing note.body to memory'''
        dprint(3, "\nDatabaseBinding::save_note_nowrite")
        if nt is None:
            e = Exception("save_note_nowrite argument requires note object")
            self._error.append(e)
            return True
        if nt.mime is not NoteMime.TEXT:
            # silent fail: writing is not supported for images or pdfs
            return False
        ### compare/update marks ###
        self.__cursor.execute('''select rowid,mark from bookmarks where file=?''',
                              (nt.ID, ))
        db_hits = self.__cursor.fetchall()
        for item in db_hits:
            if not (item[1] in nt.tags):
                self.__cursor.execute('''delete from bookmarks where rowid=?''',
                                      (item[0], ))
        self._src.commit()
        for tag in nt.tags:
            if not (tag in [ item[1] for item in db_hits ]):
                self.__cursor.execute('''insert into bookmarks (mark,file,type) values (?,?,?)''',
                                      (tag, nt.ID, nt.mime.value))
        self._src.commit()
        return False

    
    def close_note(self):
        '''if applicable, close a note; could mean clearing some pointers'''
        # this method is not, at present, used or useful
        dprint(3, "\nDatabaseBinding::close_note")
        pass

    
    def update(self, nt, marks):
        '''Update silent index: save/remove marks, create an entry if necessary.'''
        dprint(3, "\nDatabaseBinding::update")
        if (not nt.tags) and (not marks):
                return
        if nt.mime == NoteMime.TEXT:
            nt.tags.silent = marks # this assignment will not replace the Tag() with a list()
        else:
            nt.tags = Tag(marks) # but this assignment will replace Tag() with a list() unless Tag(marks) is used
        # find the file in the index ( update or create it )
        target = None
        try:
            tmp_files = self.__dex["file"]
        except Exception as e:
            # no existing file tags in index
            newc = extconf.Configuration(self.__dex.getdoc())
            extconf.fill_configuration(newc,
                                       "file",
                                       members={"loc":nt.ID,
                                                "mark":[item for item in marks]},
                                       attributes={"type":str(nt.mime.value)})
            extconf.attach_top_configuration(self.__dex.getdoc(),
                                             "file",
                                             newc,
                                             "contents",
                                             self.__dex)
            for tag in marks:
                self.__cursor.execute('''insert into bookmarks (mark,file,type) values (?,?,?)''',
                                      (tag, nt.ID, nt.mime.value))
        else:
            if isinstance(tmp_files, extconf.Configuration):
                if tmp_files["loc"] == nt.ID:
                    target = tmp_files
            else: # it's a tuple of Configurations
                for f in tmp_files:
                    if f["loc"] == nt.ID:
                        target = f
                        break
            if target:
                target["mark"] = marks
            else:
                newc = extconf.Configuration(self.__dex.getdoc())
                extconf.fill_configuration(newc,
                                           "file",
                                           members={"loc":nt.ID,
                                                    "mark":[item for item in marks]},
                                           attributes={"type":str(nt.mime.value)})
                extconf.attach_configuration(self.__dex,
                                             "file",
                                             newc)
            total_marks = list(nt.tags) + list(nt.tags.silent)
            self.__cursor.execute('''select rowid,mark from bookmarks where file=?''',
                                  (nt.ID, ))
            db_hits = self.__cursor.fetchall()
            for item in db_hits:
                if not (item[1] in total_marks):
                    self.__cursor.execute('''delete from bookmarks where rowid=?''',
                                          (item[0], ))
            self._src.commit()
            for tag in total_marks:
                if not (tag in [ item[1] for item in db_hits ]):
                    self.__cursor.execute('''insert into bookmarks (mark,file,type) values (?,?,?)''',
                                          (tag, nt.ID, nt.mime.value))
        self._src.commit()

                
    def __del__(self):
        '''Destructor method: close database/source connection'''
        dprint(3, "\nDatabaseBinding::__del__")
        if self._src:
            self._src.close()
        self._error = None

