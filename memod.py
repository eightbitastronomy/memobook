import memo
from memo.binding import DatabaseBinding
from memo.config import dprint
from memo.note import Note,NoteMime,Tag
import memo.extconf as extconf
import memo.empty as empty
import sys
import os
import argparse




def parse_command_line(filetest):
    parser = argparse.ArgumentParser()
    group_action = parser.add_mutually_exclusive_group(required=True)
    group_logic = parser.add_mutually_exclusive_group(required=False)
    parser.add_argument("-r","--source",default="archive.db",help="Path to data source",metavar="")
    parser.add_argument("-c","--ctrl",default="conf.xml",help="Path to control/configuration XML",metavar="")
    parser.add_argument("-f","--file",default=None,help="File name for save/store operation",metavar="")
    parser.add_argument("-i","--identifiers",default=None,help="Identifiers (marks, files, or dirs) in comma-separated list",metavar="")
    group_logic.add_argument("-O","--orlogic",action="store_true",help="Search for files with any given marks")
    group_logic.add_argument("-A","--andlogic",action="store_true",help="Search for files matching each given mark")
    group_action.add_argument("-s","--save",action="store_true",help="Save: store marks and write file to disk")
    group_action.add_argument("-S","--store",action="store_true",help="Store: store marks")
    group_action.add_argument("-l","--lookupmark",action="store_true",help="Lookup: retrieve file names based on marks")
    group_action.add_argument("-L","--lookupname",action="store_true",help="Lookup: retrieve marks based on file name")
    group_action.add_argument("-t","--toc",action="store_true",help="Table of Contents: retrieve all marks")
    group_action.add_argument("-p","--populate",action="store_true",help="Populate: scan directories for marks")
    group_action.add_argument("-d","--readdirs",action="store_true",help="Retrieve scan directories")
    #group_action.add_argument("-D","--setdirs",help="Set scan directories, comma-separated list (erases previous)")
    group_action.add_argument("-D","--setdirs",action="store_true",help="Set scan directories, comma-separated list (erases previous)")
    if filetest:
        parser.add_argument("filename")
    args = parser.parse_args()
    if (args.save or args.store) and (args.file == None or filetest == False) and (args.identifiers == None):
        print("Save/store (-s/-S) requires a pipe or file name target (-f) and marks (-i)")
        return None
    if args.lookupmark and (args.identifiers == None):
        print("Lookup by marks (-l) requires marks (-i)")
        return None
    if args.lookupname and (args.identifiers == None):
        print("Lookup by name (-L) requires file (-i)")
        return None
    if args.setdirs and (args.identifiers == None):
        print("Set scan directories (-D) requires directories (-i)")
        return None
    print("-----------------------------")
    if filetest:
        dprint(3,"fn " + args.filename)
    dprint(3,"s {}S {}\nl {}\nL {}\nt {}\np {}\nd {}\nD {}\nO {}\nA {}\ni {}\nf {}".format(args.save,args.store,args.lookupmark,args.lookupname,args.toc,args.populate,args.readdirs,args.setdirs,args.orlogic,args.andlogic,args.identifiers,args.file))
    return args


def create_note(**kwargs):
    newnote = Note()
    if "title" in kwargs.keys():
        newnote.title = kwargs["title"]
    if "id" in kwargs.keys():
        newnote.ID = kwargs["id"]
    if "tags" in kwargs.keys():
        newnote.tags = Tag(kwargs["tags"])
    if "mime" in kwargs.keys():
        newnote.mime = kwargs["mime"]
    return newnote
        

guide = None
data = None
text = ""
db = None
ctrl = None

if os.isatty(0):
    print("No pipe\n")
    guide = parse_command_line(True)
    if guide and (True in (guide.save,guide.store,)):
        data = open(guide.filename,"r",-1)
    else:
        sys.exit(0)
else:
    print("Pipe\n")
    guide = parse_command_line(False)
    if guide is not None :
        data = sys.stdin
    else:
        sys.exit(0)


for line in data:
    text += line
data.close()


try:
    ctrl = extconf.load_file(guide.ctrl)
except Exception as e:
    dprint(1,"Error loading or preparing memobook: " + str(e))
    empty.write_skeleton_conf("conf.xml")
    ctrl = extconf.load_file("conf.xml")
    ctrl["loc"]='.'


db = DatabaseBinding(ctrl)
exc = db.get_last_error()
if exc:
    dprint(2,"Failed to open DatabaseBinding (" + guide.source + ") with error: " + str(exc) )
    print("Failed to open DatabaseBinding.")
    sys.exit(-1)
if guide.source != ctrl["db"]["src"]:
    print(guide.source, "vs", ctrl["db"]["src"])
    db.set_source(guide.source)
    exc = db.get_last_error()
    if exc:
        dprint(2,"Failed to set DatabaseBinding  source(" + guide.source + ") with error: " + str(exc) )
        print("Failed to set DatabaseBinding source.")
        sys.exit(-1)


if guide.save:
    name = ""
    if guide.file:
        name = guide.file
    else:
        name = guide.filename
    marks = guide.identifiers.split(",")
    if len(marks) < 1:
        print("Improper marks list")
        sys.exit(0)
    nt = create_note(title=os.path.basename(name),
                     ID=name,
                     tags=marks,
                     body=text,
                     mime=NoteMime.TEXT)
    if db.save_note(nt):
        dprint(2,"Failed to save (" + nt.ID + ") with error: " + str(db.get_last_error()))
        print("Failed to save")
        sys.exit(-2)
    sys.exit(0)

    
if guide.store:
    name = ""
    if guide.file:
        name = guide.file
    else:
        name = guide.filename
    marks = guide.identifiers.split(",")
    if len(marks) < 1:
        print("Improper marks list")
        sys.exit(0)
    nt = create_note(title=os.path.basename(name),
                     ID=name,
                     tags=marks,
                     mime=NoteMime.TEXT)
    if db.save_note_nowrite(nt):
        dprint(2,"Failed to store (" + name + ") with error: " + str(db.get_last_error()))
        print("Failed to store")
        sys.exit(-2)
    sys.exit(0)
    
if guide.lookupmark:
    sys.exit(0)

if guide.lookupname:
    sys.exit(0)
if guide.toc:
    sys.exit(0)
    
if guide.populate:
    sys.exit(0)
    
if guide.readdirs:
    sys.exit(0)
    
if guide.setdirs:
    sys.exit(0)
