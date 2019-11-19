if exists('g:loaded_memo_auto')
	finish
endif
let g:loaded_memo_auto = 1


let s:cpo_save = &cpo
set cpo&vim



" Memobook locations and files (rewritten by configuration script)
if !exists("s:memo_loc")
	let s:memo_loc = "/home/travertine/fiddlesticks"
endif
if !exists("s:memo_db")
	let s:memo_db = "/home/travertine/fiddlesticks/archive.db"
endif
if !exists("s:memo_conf")
	let s:memo_conf = "memo/config.py"
endif
if !exists("s:memo_econf")
	let s:memo_econf = "/home/travertine/fiddlesticks/conf.xml"
endif
if !exists("s:memo_dex")
	let s:memo_dex = "/home/travertine/fiddlesticks/index.xml"
endif
if !exists("s:xml_offset")
	let s:xml_offset = 1
endif
if !exists("s:memo_mark")
	let s:memo_mark = "@@"
endif
if !exists("s:memo_sqlite")
	let s:memo_sqlite = "sqlite3"
endif

" Functions in alphabetical order:


function! s:Choices(preamble,choicelist)
    let i = 1
    if a:preamble != ""
	echo a:preamble "\n"
    else
	echo "\n"
    endif
    for name in a:choicelist
        echon i ". " name "\n"
        let i += 1
    endfor
    let resp = input("Please enter choice (ex: 1,2,3-6,10 or nothing): ")
    return s:ParseNumberList(resp)
endfunction


function! memobook#ClearDB()
	call system(s:memo_sqlite . " -line " . s:memo_db . 
		\ " 'drop table bookmarks;'")
	call system(s:memo_sqlite . " -line " . s:memo_db . 
		\ " 'create table bookmarks (mark NCHAR(255) NOT NULL,file NCHAR(1023) NOT NULL,type SMALLINT);'")
endfunction

function! memobook#Edit(logic,...)
	" get files by marks (OR)
	if (a:logic < 0) || (a:logic > 1)
		return
	endif
	if a:0 == 0
		if a:logic == 0
        		let marks = input("Marks(any): ")
		else
			let marks = input("Marks(all): ")
		endif
		let marklist = s:Splitwords(marks,0)
		echo ""
	else
		let marklist = a:000
	end
	if !empty(marklist)
		let flist = s:RetrieveFilesList(marklist,a:logic)
		if empty(flist)
			return
		endif
		" I've chosen not to immediately load a file-hit in the case
		" of one file in flist because (1) it can be disconcerting to
		" expect a choice list but to have a buffer loaded instead,
		" and (2) the user may wish to see the hit and choose not to
		" load it by hitting return.
		let answerlist = s:Choices("",flist)
		if empty(answerlist)
			return
		endif
		let curbuf = bufnr()
		if len(answerlist) == 1 
			let path = get(flist,answerlist[0],"")
			if path != ""
				exec ":hide enew"
				exec ":e " . flist[answerlist[0]]
				let b:smarks = s:SilentLoad(flist[answerlist[0]])
			endif
		else
			for answer in answerlist
				let path = get(flist,flist[answer],"")
				if path != ""
					exec ":hide enew"
				        exec ":e " . flist[answer]
				endif
			endfor
			for answer in answerlist
				let path = get(flist,flist[answer],"")
				if path != ""
					exec ":hide enew"
					exec ":e " . flist[answer]
					let b:smarks = s:SilentLoad(flist[answer])
				endif
			endfor

		endif
		exec ":b " . curbuf
	endif
endfunction


function! s:Filesbymark(mk)
	  let cmd = s:memo_sqlite . " -line " . s:memo_db  . 
		\ " 'select * from bookmarks where mark=\"" . a:mk . "\" and type=0 ;'"
	  let dbretval = system(cmd)
	  let retval = []
	  if dbretval =~ "^Error"
		  echo "\n" . dbretval
		  return retval
	  else
	      let groups = split(dbretval,"\n\n")
	      if !empty(groups)
	      	 for str in groups
		     let subtuple = split(str)
		     let i = index(subtuple,"mark")
		     let j = index(subtuple,"file")
		     let k = index(subtuple,"type")
		     call add(retval,[subtuple[i+2],subtuple[j+2],subtuple[k+2]])
		 endfor
	      endif
	  endif
	  return retval
endfunction


function! s:Marksbyfile(fl)
	  let cmd = s:memo_sqlite . " -line " . s:memo_db  . 
		\ " 'select rowid,mark from bookmarks where file=\"" . a:fl . "\";'"
	  let dbretval = system(cmd)
	  let retval = []
	  if dbretval =~ "^Error"
		  echo "\n" . dbretval
		  return retval
	  else
	      let groups = split(dbretval,"\n\n")
	      if !empty(groups)
	      	 for str in groups
		     let subtuple = split(str)
		     let i = index(subtuple,"rowid")
		     let j = index(subtuple,"mark")
		     call add(retval,[subtuple[i+2],subtuple[j+2]])
		 endfor
	      endif
	  endif
	  return retval
endfunction


function! s:Parsebuffer()
    let curline = line (".") "line("'<")
    let curcol = virtcol(".") "virtcol("'<")
    call cursor(1,1)
    let results = []
    while search(s:memo_mark,"W")
        "execute "/@@\c[0-9\-a-z][0-9\-a-z]*"
	let markstart = getpos(".")[2] + 1 " getpos returns col counting from 1, 
					   " but string splicing starts from 0
	let rstring = split(getline(".")[markstart:]," ")[0]
	call add(results,rstring)
    endwhile
    call cursor(curline,curcol)
    return results
endfunction


function! s:ParseFile(filename)
	if expand('%:p') == ''
		let curbuf = -1
	else
		let curbuf = bufnr()
	endif
	exec ":hide enew " 
	exec ":hide e " . a:filename
	let editbuf = bufnr()
	let retmarks = s:Parsebuffer()
	if curbuf < 0
		exec ":enew"
		let curbuf = bufnr()
	endif
	exec ":bwipeout" . editbuf
	exec ":b " . curbuf
	return retmarks
endfunction


function! s:ParseNumberList(numbers)
    if a:numbers == ""
	    return []
    endif
    let choices = []
    let segments = split(a:numbers,",")
    for segment in segments
	let sbuffer = split(segment," ")
	if len(sbuffer) > 1
		return []
	endif
	let sbuffer = split(sbuffer[0],"-")
	if len(sbuffer) == 1
		if sbuffer[0] =~ "[0-9]*"
			call add(choices,str2nr(sbuffer[0])-1)
		endif
	elseif len(sbuffer) > 2
		return []
	else
		let startint = str2nr(sbuffer[0])
		let stopint = str2nr(sbuffer[1])
		if (startint =~ "[0-9]*") && (stopint =~ "[0-9]*")
			while startint <= stopint
				call add(choices,startint-1)
				let startint += 1
			endwhile
		endif
	endif
    endfor
    return choices
endfunction


function! s:Removefromdb(mk)
	  let cmd = s:memo_sqlite . " -line " . s:memo_db  . 
		\ " 'delete from bookmarks where mark=\"" . a:mk . "\";'"
	  let retval = system(cmd)
	  exe "normal! o" . retval . "\<Esc>"
endfunction


function! s:RetrieveFilesList(mk,logic)
	let tuplelist = []
	let filelist = []
	if a:logic == 0
		" OR
		for item in a:mk
			let retlist = s:Filesbymark(item)
			if !empty(retlist)
				if len(retlist) > 1
					call extend(tuplelist,retlist)
				else
					call add(tuplelist,retlist[0])
				endif
			endif
		endfor
		if empty(tuplelist)
			return []
		endif
		for t in tuplelist
			call add(filelist,t[1])
		endfor
	else
		" AND
		let n = len(a:mk)
		for item in a:mk
			let retlist = s:Filesbymark(item)
			if !empty(retlist)
				if len(retlist) > 1
					call extend(tuplelist,retlist)
				else
					call add(tuplelist,retlist[0])
				endif
			else
				let n -= 1
			endif
		endfor
		if empty(tuplelist)
			return []
		endif
		" All lists have been combined and checked for emptiness.
		" If a file exists in an intersection of n lists, it will
		" appear n times in tuplelist.
		let pathlist = []
		for tuple in tuplelist
			call add(pathlist,tuple[1])
		endfor
		while 1
			if len(pathlist) < 1
				break
			endif
			let possible = pathlist[0]
			if count(pathlist,possible) == n
				call add(filelist,possible)
			endif
			while 1
				let j = index(pathlist,possible)
				if j < 0
					break
				endif
				call remove(pathlist,j)
			endwhile
		endwhile
	endif
	return filelist
endfunction


function! s:SavetodbUnprocessed(filename,filetype)
    let marksinbuffer = s:Parsebuffer()
    if exists("b:smarks")
	    call extend(marksinbuffer,b:smarks)
    endif
    let markstoadd = []
    let markstoremove = []
    let marksretrieved = []
    let retrieved = s:Marksbyfile(a:filename)
    if !empty(retrieved)
        for tuplet in retrieved
            if index(marksinbuffer,tuplet[1]) == -1
	        call add(markstoremove,tuplet[0])
	    endif
	endfor
	for tuplet in retrieved
	    call add(marksretrieved,tuplet[1])
	endfor
	for item in marksinbuffer
	    if index(marksretrieved,item) == -1
	        call add(markstoadd,item)
	    endif
	endfor
    else
        let markstoadd = marksinbuffer
    endif
    for savemark in markstoadd
	let dbretval = system(s:memo_sqlite . " -line " . s:memo_db  . 
			\ " 'insert into bookmarks(mark,file,type) values(\"" 
			\ . savemark . "\",\"" . a:filename . "\",\"" 
			\ . a:filetype . "\");'")
	if dbretval =~ "^Error"
		  echo "\n" . dbretval
		  return
	endif
    endfor
    if !empty(markstoremove)
	for delmark in markstoremove
		let dbretval = system(s:memo_sqlite . " -line " . s:memo_db  . 
			\ " 'delete from bookmarks where rowid=" . 
			\ str2nr(delmark) . ";'")
		if dbretval =~ "^Error"
			echo "\n" . dbretval
			return
		endif
	endfor
    endif
endfunction


function! s:SavetodbProcessedText(filename,marks)
	for mark in a:marks
		let dbretval = system(s:memo_sqlite . " -line " . s:memo_db  . 
				\ " 'insert into bookmarks(mark,file,type) values(\"" 
				\ . mark . "\",\"" . a:filename . "\",\"0\");'")
		if dbretval =~ "^Error"
			  echo "\n" . dbretval
			  return
		endif
	endfor
endfunction


function! memobook#Scan()
	" Scan using Python (faster)
	echo system("python3 " . s:memo_loc . "/memod.py --ctrl=" . s:memo_econf .  " --populate ")
	echo "Populated."
endfunction


function! memobook#Scann()
	" Scan without using Python (slower)
	" First, read scan directories
	if expand('%:p') == ''
		let curbuf = -1
	else
		let curbuf = bufnr()
	endif
	exec ":hide enew " 
	exec ":hide e " . s:memo_econf
	let editbuf = bufnr()
	call cursor(1,1)
	let dirlist = []
	let pos_db_begin = search("<db>","W")
	if pos_db_begin > 0
		" use xml_offset to find the beginning of the record
		let pos_db_end = search("</db>","nW")
		if pos_db_end > pos_db_begin
			while search("<scan>","W",pos_db_end)
				let markstart = getpos(".")[2] + 5
				call search("</scan>","W",pos_db_end)
				let markend = getpos(".")[2] - 2
				let dirstring = getline(".")[markstart:markend]
				call add(dirlist,dirstring)
			endwhile
		endif
	endif
	if curbuf < 0
		exec ":enew"
		let curbuf = bufnr()
	endif
	exec ":bwipeout" . editbuf
	exec ":b " . curbuf
	if (pos_db_begin < 1) || empty(dirlist)
		echo "Database not found in " . s:memo_econf
		return
	endif
	" Iterate through each scan directory and parse text files
	call memobook#ClearDB()
	if expand('%:p') == ''
		let curbuf = -1
	else
		let curbuf = bufnr()
	endif
	exec ":hide enew " 
	let editbuf = bufnr()
	for dir in dirlist
		let fileslist = split(globpath(dir,'**'),'\n')
		for file in fileslist
			if fnamemodify(file,":e") == "txt"
				let marks = []
				exec ":hide r " . file
				while search(s:memo_mark,"W")
					let markstart = getpos(".")[2] + 1 " getpos returns col counting from 1, 
									   " but string splicing starts from 0
					let rstring = split(getline(".")[markstart:]," ")[0]
					call add(marks,rstring)
				endwhile
				exec "normal G"
				let lastline = getcurpos()[1]
				exec ":1," . lastline . "d"
				call cursor(1,1)
				if !empty(marks)
					call s:SavetodbProcessedText(file,marks)
				endif
				" echo file marks
			endif
		endfor
	endfor
	if curbuf < 0
		exec ":enew!"
		let curbuf = bufnr()
	endif
	exec ":bwipeout" . editbuf
	exec ":b " . curbuf
endfunction


function! memobook#ScanManage()
	if expand('%:p') == ''
		let curbuf = -1
	else
		let curbuf = bufnr()
	endif
	exec ":hide enew " 
	exec ":hide e " . s:memo_econf
	let editbuf = bufnr()
	call cursor(1,1)
	let dirlist = []
	let pos_db_begin = search("<db>","W")
	if pos_db_begin > 0
		" use xml_offset to find the beginning of the record
		let pos_db_end = search("</db>","nW")
		if pos_db_end > pos_db_begin
			while search("<scan>","W",pos_db_end)
				let markstart = getpos(".")[2] + 5
				call search("</scan>","W",pos_db_end)
				let markend = getpos(".")[2] - 2
				let dirstring = getline(".")[markstart:markend]
				call add(dirlist,dirstring)
			endwhile
		endif
	else
		if curbuf < 0
			exec ":enew"
			let curbuf = bufnr()
		endif
		exec ":bwipeout" . editbuf
		exec ":b " . curbuf
		echo "Database not found in " . s:memo_econf
		return
	endif
	let oldlist= copy(dirlist)
	if !empty(dirlist)
		let chlist = reverse(s:Choices("Delete which scan directories?",dirlist))
		if !empty(chlist)
			for num in chlist
				call remove(dirlist,str2nr(num))
			endfor
		endif
	endif
	call extend(dirlist,s:Splitwords(input("Add directories: ", "", "dir"),1))
	if oldlist == dirlist
		if curbuf < 0
			exec ":enew"
			let curbuf = bufnr()
		endif
		exec ":bwipeout" . editbuf
		exec ":b " . curbuf
		return
	endif
	if empty(dirlist)
		let dirlist = [ "." ]
	endif
	call cursor(pos_db_begin,1)
	while search("<scan>","W",pos_db_end)
		let pos_scan_end = search("</scan>","nW",pos_db_end)
		let i = pos_scan_end - getcurpos()[1] + 1
		while i > 0
			exec ":" . getcurpos()[1] . "d"
			let i -= 1
		endwhile
		call cursor(pos_db_begin,1)
	endwhile
	call cursor(pos_db_begin,1)
	let pos_db_end = search("</db>","W")
	call cursor(pos_db_end - 1,1) 
	let i = 0
	for d in dirlist
		call append(getcurpos()[1] + i, "      <scan>" . d . "</scan>")
		let i += 1
	endfor
	write
	if curbuf < 0
		exec ":enew"
		let curbuf = bufnr()
	endif
	exec ":bwipeout" . editbuf
	exec ":b " . curbuf
	return
endfunction


function! memobook#SilentDisplay()
	if exists("b:smarks")
		echo "Silent marks:" join(b:smarks," ")
	endif
	return
endfunction


function! s:SilentLoad(fname)
	let retlist = []
	let curbuf = bufnr()
	exec ":hide view " . s:memo_dex
	call cursor(1,1)
	let pos_path = search(a:fname,"W")
	if pos_path > 0
		" use xml_offset to find the beginning of the record
		let b:pos_in_dex = pos_path - 1
		let pos_end = search("</file>","nW")
		while search("<mark>","W",pos_end)
			let markstart = getpos(".")[2] + 5
			call search("</mark>","W",pos_end)
			let markend = getpos(".")[2] - 2
			let rstring = getline(".")[markstart:markend]
			call add(retlist,rstring)	
		endwhile
	endif
	exec ":bdelete " . bufnr()
	exec ":b " . curbuf
	return retlist
endfunction


function! memobook#SilentManage()
	if !exists('b:smarks')
		let b:smarks = []
	endif
	let old_marks = copy(b:smarks)
	if !empty(b:smarks)
		" delete, first
		let chlist = reverse(s:Choices("Delete which silent marks?",b:smarks))
		if !empty(chlist)
			for num in chlist
				call remove(b:smarks,str2nr(num))
			endfor
		endif	
	endif
	" add, second
	call extend(b:smarks,s:Splitwords(input("Add silent marks: "),0))
	return
endfunction


function! s:SilentWrite(fname)
	if !exists('b:smarks')
		return
	else
		let marks = copy(b:smarks)
	endif
	let storedlist = []
	if expand('%:p') == ''
		let curbuf = -1
	else
		let curbuf = bufnr()
	endif
	exec ":hide enew "
	exec ":hide e ". s:memo_dex
	let editbuf = bufnr()
	" check dex for file name
	" if present, rewrite marks
	" else, append new entry
	call cursor(1,1)
	let pos_path = search(a:fname,"W")
	if pos_path > 0
		" file name was in dex
		" use xml_offset to find the beginning of the record
		let b:pos_in_dex = pos_path - 1
		let pos_end = search("</file>","nW")
		" find the old/stored silent marks
		while search("<mark>","W",pos_end)
			let markstart = getpos(".")[2] + 5
			call search("</mark>","W",pos_end)
			let markend = getpos(".")[2] - 2
			let rstring = getline(".")[markstart:markend]
			call add(storedlist,rstring)	
		endwhile
		if marks == storedlist
			" nothing to write
			return
		endif
		" remove all marks 
		call cursor(pos_path,1)
		let pos_mark = search("<mark>","W")
		if pos_mark < 1
			" if xml <mark> is not present, place new marks immediately
			" after the <loc></loc> pair
			let pos_mark = pos_path + 1
		endif
		let i = pos_mark
		while i < pos_end
			exec ":". pos_mark ."d"
			let i += 1
		endwhile
		for sm in marks
			call append(pos_mark-1,"      <mark>".sm."</mark>")
		endfor
	else
		" file name was not in dex; make a new entry
		call cursor(1,1)
		let contents_end = search("</contents>","W") - 1
		call append(contents_end,"    <file type=\"1\">")
		call append(contents_end+1,"      <loc>".a:fname."</loc>")
		let contents_end += 2 
		for sm in marks
			call append(contents_end,"      <mark>".sm."</mark>")
			let contents_end += 1
		endfor	
		call append(contents_end,"    </file>")
	endif
	" finish up and return
	write
	if curbuf < 0
		exec ":enew"
		let curbuf = bufnr()
	endif
	exec ":bwipeout" . editbuf
	exec ":b " . curbuf 
endfunction


function! s:Splitwords(inputstring,isadir)
    if !empty(a:inputstring)
	let working_str = a:inputstring
	if a:isadir == 1
		while working_str =~ '\~'
			let index = match(working_str,'\~')
			if index == 0
				let rhalf = working_str[1:]
				let working_str = $HOME . rhalf
				continue
			endif
			if index == len(working_str)-1
				let lhalf = working_str[0:len(working_str)-2]
				let working_str = lhalf . $HOME
				continue
			endif
			let lhalf = working_str[0:index-1]
			let rhalf = working_str[index+1:len(working_str)-1]
			let working_str = lhalf . $HOME . rhalf
		endwhile
	endif
	if !empty(matchstr(working_str,","))
	    return split(working_str,",")
	else
	    return split(working_str)
	endif
    else
	return []
    endif
endfunction


function! memobook#Write(filetype,filename)
	if a:filename == ""
		echo "Please set buffer file name before calling Mwrite"
		return
	endif
	call s:SavetodbUnprocessed(a:filename,a:filetype)
	call s:SilentWrite(a:filename)
	exec ":write " . a:filename
endfunction

let &cpo = s:cpo_save
unlet s:cpo_save

" end of autoload
