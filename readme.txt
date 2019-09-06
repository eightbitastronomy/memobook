memobook, author: eightbitastronomy

A notepad/texteditor derivative for people who don't want to remember everything ever.

 -   Written in Python 3; requires tkinter and sqlite3 libraries.
 -   Class Memobook is the application, but pad.sh is a short script to launch it. Alternatively, launch it via pad.py.
 -   Class CustomNotebook in notebook.py is not original code, but was copied from a public forum help thread. I imagine that this portion of the code is therefore not covered under any license of mine.

Usage:

 -   write notes as you go, but store them as .txt text files. At the end of your file, type up a few "marks" which basically serve to hashtag your file. Use the tag-marker designated in config.py. Example, for "@@": @@readme @@help @@memobook
 -   Yes, certainly on a -nix system you could just grep particular keywords. But why do we continue to code and code and code if not to make tasks easier than they were before?
 -   Open memobook (pad.sh or pad.py). You can set the directories containing your notes under "Sources." "Scan" will update the memobook's marks. Once memobook has found marked files, you can open them by mark alone. Or, open files the traditional way -- by an open-file dialogue.
 -   For convenience, under "Marks" you can gather all the marks found in open text files, select the ones you want, and add them to the end of the current tab. This way, you needn't type the marks if you don't want.

Configuration:

 -   only one global variable is used, and that's because doing so simplified some code a great deal: TAG_MARKER located in config.py. If you would rather use a different marker, change it. But this doesn't magically change the markers in files you've already made...
 -   all other configuration values are found in conf.xml.

Future tasks:

 -   add font control and text encoding.
 -   better handling of what is a text file and what is not.
 -   add canvas-pages so that pictures can be loaded into tabs; this will either require ancillary files to store mark information for the pictures or will require the database to keep track of said mark information.
