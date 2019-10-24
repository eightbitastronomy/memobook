import memo
from memo.binding import DatabaseBinding
import sys
import os
import argparse




def parseCommandLine(filetest):
    parser = argparse.ArgumentParser()
    group_action = parser.add_mutually_exclusive_group(required=True)
    group_logic = parser.add_mutually_exclusive_group(required=False)
    group_logic.add_argument("-O","--orlogic",action="store_true",help="Search for files with any given marks")
    group_logic.add_argument("-A","--andlogic",action="store_true",help="Search for files matching each given mark")
    #parser.add_argument("-m","--marks",help="Marks, comma-separated list",metavar="")
    #parser.add_argument("-f","--file",default=None,help="File name",metavar="")
    parser.add_argument("-i","--identifiers",default=None,help="Identifiers (marks, files, or dirs) in comma-separated list",metavar="")
    group_action.add_argument("-s","--save",action="store_true",help="Store: store marks and write file to disk")
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
        print("fn " + args.filename)
    print("s {}\nl {}\nL {}\nt {}\np {}\nd {}\nD {}\nO {}\nA {}\ni {}".format(args.save,args.lookupmark,args.lookupname,args.toc,args.populate,args.readdirs,args.setdirs,args.orlogic,args.andlogic,args.identifiers))
    return args



if os.isatty(0):
    sys.stderr.write("No pipe\n")
    sys.stderr.flush()
    guide = parseCommandLine(True)
    #if guide is not None :
    #    data = open(guide.filename,"r",-1)
    #else:
    sys.exit(0)
else:
    sys.stderr.write("Pipe\n")
    sys.stderr.flush()
    guide = parseCommandLine(False)
    #if guide is not None :
    #    data = sys.stdin
    #else:
    sys.exit(0)

