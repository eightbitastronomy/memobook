memobook, author: eightbitastronomy
license: see file, LICENSE

A notepad/texteditor derivative for people who don't want to remember everything ever.

 -   Can display image files too (read-only).
 -   Written in Python 3; requires tkinter and sqlite3 libraries. Requires pillow (PIL) version 6+ (I think) -- must have ImageTk.
 -   Class Memobook is the application, but pad.sh is a short script to launch it. Alternatively, launch it via pad.py.

Usage:

 -   Write notes as you go, but store them as .txt text files. At the end of your file, type up a few "marks" which basically serve to hashtag your file. Use the tag-marker designated in config.py. Example, for "@@": @@readme @@help @@memobook
 -   Set & scan the folder(s) where you intend to keep your notes. Done. Use as normal.
 -   For images, once you've opened them and inserted a few marks (which won't alter the image file), you can search for images in the same way as texts.

Further usage detail:
 -   Yes, certainly on a -nix system you could just grep particular keywords. But why do we continue to code and code and code if not to make tasks easier than they were before? Additionally, grep isn't the most helpful tool when it comes to images...
 -   Memobook is opened with pad.sh or pad.py, unless you're using a pyinstaller package (in which case, the file to look for is Memobook).
 -   You can set the directories containing your notes under "Sources." "Scan" will update the memobook's marks. Once memobook has found marked files, you can open them by mark alone. Or, open files the traditional way -- by an open-file dialogue.
 -   For convenience, under Edit->Insert Mark, you can gather all the marks found in open text files, select the ones you want, and add them to the end of the current tab. This way, you needn't type the marks if you don't want. With image files, the marks are stored, just not visibly.
 -   If the application/GUI font size (menu bars, buttons, etc) isn't to your liking, open up conf.xml and change the <style><font><size> tag. Enter a positive number to increase size, negative to decrease. Fonts for texts that you open up in a tab can be chosen under the Edit menu.
 -   Other config options can be altered in conf.xml if you choose, but most are automatically updated through application use.

Configuration details:

 -   Probably, the only global variable of concern is TAG_MARKER located in config.py. It was chosen to be "@@" because in normal, everyday literature, "@@" is not a commonly used punctuation. In html, e.g., "@@" might not be so uncommon. If you would rather use a different marker, change it.  But this doesn't magically change the markers in files you've already made...
 -   most other configuration values are found in conf.xml.
 -   Image marks & details are stored in index.xml.

Future tasks:

 -   remove mime storage in database if it isn't useful
 -   better handling of what is a text file and what is not.
 -   add pdf read-only capabilities.
 -   resolve malfunction of global Tk theme changes.

