if exists('g:loaded_memo')
   finish
endif
let g:loaded_memo = 1


let s:cpo_save = &cpo
set cpo&vim


" Remapping the 'down a line' command also remaps <CR>.
" This is unavoidable, so I should find a different method.
" Unfortunately, just about everything is in use / thought of.
nmap <silent> <c-m> :call Interface()<CR>

" this uses ctrl-space, but i'm not sure I will use it
" nmap <silent> <c-@> :call Interface()<CR>


function! Interface()
    echo ""
    let c = nr2char(getchar())
    if c == "w"
        " intercept write and store marks
        call Write(expand('%:p'),"1")
    elseif c == "e"
        " get files by marks (OR)
        let marks = input("Marks(any): ")
	let marklist = []
	if !empty(marks) 
		if !empty(matchstr(marks,","))
			let marklist = split(marks,",")
		else
			let marklist = split(marks)
		endif
	else
		return
	endif
	echo ""
	if !empty(marklist)
		let flist = Edit(marklist,0)
		exe bufnr("Memo: File hits",1)."buffer"
		call append(0,flist)
	endif
        " use new buffer to choose files to open (maybe a quickbuffer?)
    elseif c == "E"
        " get files by marks (AND)
        let marks = input("Marks(all): ")
        let flist = Edit(marks,0)
        " use new buffer to choose files to open (maybe a quickbuffer?)
    elseif c == "m"
        " add silent marks
	" these must be buffer-local and Savetodb must send them to db
	let marks = ""
	let bid = bufname("%")
	if bid == ""
	    let bid = "buffer " . bufnr()
	endif
	let marks = input("Silent(" . bid . "): ")	
    elseif c == "s"
        " scan directories
    else
        let cp = getcurpos()
	call cursor(cp[1]+1,cp[2])
    endif
    return
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


function! Edit(mk,logic)
	if a:logic == 0
		let tuplelist = []
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
		let filelist = []
		for t in tuplelist
			call add(filelist,t[1])
		endfor
		return filelist
	else
		return []
	endif
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
