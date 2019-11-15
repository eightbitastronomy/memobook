# memobook

A notepad/texteditor derivative for people who don't want to remember everything ever.
 -  If you commonly write down things you've learned in plain text files -- because there's just too much to remember --
 -  ...and months later you need that information but can't remember where you wrote it down...
 -  Then sure, you could grep your home directory to death. Or, this is the application for you.

The Memobook Note Suite:
 -  Includes a Vim extension, a windowed GUI, and an upcoming Emacs extension
 -  Can display image and pdf files too (read-only) with basic functionality (zooming, rotating, etc.) -- windowed GUI only.
 -  Stores information (your bookmarks) about the image & pdf files without altering them.
 -  Bookmarks in plaintext files can be tagged in the text itself, or can be "silently" added, i.e., recorded outside of the file

Why use anything in this suite?
 -  Because grepping for keywords isn't always ideal. You know you best, and you know how you think best. When you write a bit of information down in a file, who knows better than you what words/topics/ideas you'll use to try to find it a year or two from now? And those will be the bookmarks you place in that file so that in a year or two, when you vaguely remember writing a thing or two down, you can find it.
 -  And because you don't want to waste the time using a file format that only one specific application can understand. Memobook Note Suite works with what you already have, use, and maybe even, a little nerdishly, love.

The windowed GUI:
 -  Is written in Python 3; requires tkinter, pillow, and poppler libraries. Pillow (PIL) version 6+ (I think) -- must have ImageTk.
 -  As far as I know, the poppler dependency is the reason this portion of the suite won't run on Windows.

The Vim extension:
 -  Requires Vim 8+ (I think)
 -  Currently relies on Python 3 only for one function call. In the future this dependency will be removed so that it can run on a system having no Python.
 -  Configuration script for Vim currently supports for vim-plug and pathogen utilities. For other plugin methods, it's currently DIY.

All portions:
 -  Require sqlite3. The windowed portion requires Python module sqlite3; the Vim extension requires an sqlite3 binary in the user's $PATH

Installation and configuration:
 -  Download these files or clone the git repo
 -  Run the config.sh bash script with any desired options
 -  The tag sequence for bookmarks is initially configured in the config.sh script, but can also be manually changed in appropriate files. Grep them to find them.

Usage: 
 -  In all portions: reading, writing, etc, of files is the same as it always was. However, once a few files have been bookmarked, files may be searched by those bookmarks. 
 -  In all portions: Text files may be bookmarked simply by prefixing a word with the tag sequence. For example, by default the tag sequence is @@. So, in a text file about how to use ffmpeg to transcode a movie file from one codec to another, one might use @@ffmpeg and @@HVEC to make the file searchable by "ffmpeg" or "HVEC".
 -  In all portions: silent bookmarks are not stored in the file itself. Hence, they must be added in a different manner. However, when searching for files by bookmark, nothing special must be done; silent marks will be searched as well.
 -  Windowed GUI: operates much like any other windowed text editor. Use 'Sources' menu for specifying and scanning directories for your existing (if any) bookmarked text files. Scanning will also load (if any) silent marks that are associated with image, pdf, and text files. Under the 'Edit' menu marks may be managed/inserted. To run from the command line, type 'memobook'. Running as a desktop app is currently DIY, but...There's no icon included with these files. (The struggle is real.)
 -  Vim: User preference may vary quite widely, so feel free to edit the plugin/memobook.vim to get desired key mappings. Out of the box, however, mappings are for <Leader>m followed by a single key: 
    >  w ... write to disk after storing marks in memobook database
    >  e ... followed by a list of marks: search for any file containing any of the marks listed
    >  E ... followed by a list of marks: search for any file that contains every one of the marks listed
    >  s ... scan directories for marks
    >  S ... manage scan directories
    >  m ... manage silent marks
    >  M ... print silent marks associated with the current buffer 
 -  Emacs: under construction.

For the future:
 -  Finish the Emacs extension
 -  Fix UTF-associated problems for text files
 -  Remove Python-dependency in Vim extension
 -  Do whatever needs to be done for portions of this suite to run on just about any Windows, MacOS, BSD, or Linux system.
 -  Better handling of what is a text file and what is not.
 -  Resolve malfunction of global Tk theme changes.

Author: eightbitastronomy
License: see file, LICENSE, provided with source code.


