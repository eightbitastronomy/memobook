memobook, author: eightbitastronomy
license: see file, LICENSE

A notepad/texteditor derivative for people who don't want to remember everything ever.

 -   Can display image files too (read-only).
 -   Written in Python 3; requires tkinter and sqlite3 libraries. Requires pillow (PIL) version 6+ (I think) -- must have ImageTk.
 -   Class Memobook is the application, but pad.sh is a short script to launch it. Alternatively, launch it via pad.py.

Usage:

 -   Write notes as you go, but store them as .txt text files. At the end of your file, type up a few "marks" which basically serve to hashtag your file. Use the tag-marker designated in config.py. Example, for "@@": @@readme @@help @@memobook
 -   Set & scan the folder(s) where you intend to keep your notes. Done. Use as normal.

Further usage detail:
 -   Yes, certainly on a -nix system you could just grep particular keywords. But why do we continue to code and code and code if not to make tasks easier than they were before?
 -   Memobook is opened with pad.sh or pad.py, unless you're using a pyinstaller package (in which case, the file to look for is Memobook).
 -   You can set the directories containing your notes under "Sources." "Scan" will update the memobook's marks. Once memobook has found marked files, you can open them by mark alone. Or, open files the traditional way -- by an open-file dialogue.
 -   For convenience, under "Marks" you can gather all the marks found in open text files, select the ones you want, and add them to the end of the current tab. This way, you needn't type the marks if you don't want.
 -   If the application font size (menu bars, buttons, etc) isn't to your liking, open up conf.xml and change the <style><font><size> tag. Enter a positive number to increase size, negative to decrease.
 -   Other config options can be altered in conf.xml if you choose, but most are automatically updated through application use.

Configuration details:

 -   only one global variable is used, and that's because doing so simplified some code a great deal: TAG_MARKER located in config.py. If you would rather use a different marker, change it. But this doesn't magically change the markers in files you've already made...
 -   the *other* global variable isn't actually used...yet.
 -   all other configuration values are found in conf.xml.

Future tasks:

 -   better handling of what is a text file and what is not.
 -   add pdf read-only capabilities.
 -   resolve malfunction of global Tk theme changes.
 -   ctrl-x for text cutting results in a fatal exception/error when no text has been highlighted. Must capture this exception and discard.
