if exists('g:loaded_memo')
   finish
endif
let g:loaded_memo = 1


let s:cpo_save = &cpo
set cpo&vim

let b:smarks = ""


" Remapping the 'down a line' command also remaps <CR>.
" This is unavoidable, so I should find a different method.
" Unfortunately, just about everything is in use / thought of.
nmap <silent> <c-m> :call Interface()<CR>

" this uses ctrl-space, but i'm not sure I will use it
" nmap <silent> <c-@> :call Interface()<CR>


" Each case has been moved to its own function; this way command-mappings
" can be made for each functionality if so desired.
function! Interface()
    echo ""
    let c = nr2char(getchar())
    if c == "w"
        " intercept write and store marks
        call Write(expand('%:p'),"1")
    elseif c == "e"
	" Edit/Read files: marks will be ORed together
	    call Edit(0)
    elseif c == "E"
	" Edit/Read files: marks will be ANDed together
	    call Edit(1)
    elseif c == "m"
        " add silent marks
	" these must be buffer-local and Savetodb must send them to db
	" what about MANAGING the silent marks?
	let marks = ""
	let bid = bufname("%")
	if bid == ""
	    let bid = "buffer " . bufnr()
	endif
	let marks = input("Silent(" . bid . "): ")
	let b:smarks = Splitmarks(marks)
    elseif c == "M"
	echo b:smarks
    elseif c == "s"
        " scan directories
    else
        let cp = getcurpos()
	call cursor(cp[1]+1,cp[2])
    endif
    return
endfunction


function! ParseNumberList(numbers)
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


function! Parsebuffer()
    let curline = line (".") "line("'<")
    let curcol = virtcol(".") "virtcol("'<")
    call cursor(1,1)
    let results = []
    while search("@@","W")
        "execute "/@@\c[0-9\-a-z][0-9\-a-z]*"
	let markstart = getpos(".")[2] + 1 " getpos returns col counting from 1, but string splicing starts from 0
	let rstring = split(getline(".")[markstart:]," ")[0]
	call add(results,rstring)
    endwhile
    call cursor(curline,curcol)
    return results
endfunction


function! Write(filename,filetype)
    call Savetodb(a:filename,a:filetype)
    "call Savesilentmarks(a:filename, ...)
    write
endfunction


function! Savetodb(filename,filetype)
    let marksinbuffer = Parsebuffer()
    let markstoadd = []
    let markstoremove = []
    let marksretrieved = []
    let retrieved = Marksbyfile(a:filename)
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
	call system("sqlite3 -line /home/travertine/code/bin/memobook/archive.db 'insert into bookmarks(mark,file,type) values(\"" . savemark . "\",\"" . a:filename . "\",\"" . a:filetype . "\");'")
    endfor
    if !empty(markstoremove)
	for delmark in markstoremove
		call system("sqlite3 -line /home/travertine/code/bin/memobook/archive.db 'delete from bookmarks where rowid=" . str2nr(delmark) . ";'")
	endfor
    endif
endfunction


function! Edit(logic)
	" get files by marks (OR)
	if a:logic == 0
        	let marks = input("Marks(any): ")
	elseif a:logic == 1
		let marks = input("Marks(all): ")
	else
		return
	endif
	let marklist = Splitmarks(marks)
	echo ""
	if !empty(marklist)
		let flist = RetrieveFilesList(marklist,a:logic)
		if empty(flist)
			return
		endif
		let i = 1
		echo "\n"
		for fname in flist
			echon i ". " fname "\n"
			let i += 1
		endfor
		let resp = input("Please enter choice (ex: 1,2,3-6,10 or nothing): ")
		let answerlist = ParseNumberList(resp)
		if empty(answerlist)
			return
		endif
		let curbuf = bufnr()
		if len(answerlist) == 1 
			let path = get(flist,answerlist[0],"")
			if path != ""
				exec ":view " . flist[answerlist[0]]
			endif
		else
			for answer in answerlist
				let path = get(flist,answer,"")
				if path != ""
					exec ":view " . flist[answer]
				endif
			endfor
		endif
		exec ":b " . curbuf
	endif
endfunction


function! Managesilentmarks()
endfunction


function! Splitmarks(inputstring)
    if !empty(a:inputstring) 
	if !empty(matchstr(a:inputstring,","))
	    return split(a:inputstring,",")
	else
	    return split(a:inputstring)
	endif
    else
	return []
    endif
endfunction


function! RetrieveFilesList(mk,logic)
	let tuplelist = []
	let filelist = []
	if a:logic == 0
		" OR
		for item in a:mk
			let retlist = Filesbymark(item)
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
			let retlist = Filesbymark(item)
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


function! Savesilentmarks(fname,marks)
endfunction


function! Filesbymark(mk)
	  let cmd = "sqlite3 -line /home/travertine/code/bin/memobook/archive.db 'select * from bookmarks where mark=\"" . a:mk . "\";'"
	  let dbretval = system(cmd)
	  let retval = []
	  if dbretval != ""
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


function! Marksbyfile(fl)
	  let cmd = "sqlite3 -line /home/travertine/code/bin/memobook/archive.db 'select rowid,mark from bookmarks where file=\"" . a:fl . "\";'"
	  let dbretval = system(cmd)
	  let retval = []
	  if dbretval != ""
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


function! Removefromdb(mk)
	  let cmd = "sqlite3 -line /home/travertine/code/memobook/archive.db 'delete from bookmarks where mark=\"" . a:mk . "\";'"
	  let retval = system(cmd)
	  exe "normal! o" . retval . "\<Esc>"
endfunction


let &cpo = s:cpo_save
unlet s:cpo_save
