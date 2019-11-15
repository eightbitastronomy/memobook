if exists('g:loaded_memo')
   finish
endif
let g:loaded_memo = 1


let s:cpo_save = &cpo
set cpo&vim


" mappings {{{

" Remapping the 'down a line' command also remaps <CR>.
" This is unavoidable, so I should find a different method.
" Unfortunately, just about everything is in use / thought of.
"nmap <silent> <c-m> :call Interface()<CR>

" this uses ctrl-space, but i'm not sure I will use it
" nmap <silent> <c-@> :call Interface()<CR>

" using leader keys
nmap <silent> <leader>m :call Interface()<CR>

" }}}

" Commands {{{

command! -nargs=1 	Mwrite		:call memobook#Write("0",<f-args>)
command! -nargs=+ -bang Medit		:call memobook#Edit(<bang>0,<f-args>)
command! -nargs=0	Msil		:call memobook#SilentDisplay()
command! -nargs=0	Msilm		:call memobook#SilentManage()
command! -nargs=0	Mscan		:call memobook#Scan()
command! -nargs=0	Mscanm		:call memobook#ScanManage()

" }}}


" Each case has been moved to its own function; this way command-mappings
" can be made for each functionality if the user so desires.
function! Interface()
    echo ""
    let c = nr2char(getchar())
    if c == "w"
        " intercept write and store marks
        call memobook#Write("0",expand('%:p'))
    elseif c == "e"
	" Edit/Read files: marks will be ORed together
	call memobook#Edit(0)
    elseif c == "E"
	" Edit/Read files: marks will be ANDed together
	call memobook#Edit(1)
    elseif c == "m"
        " manage silent marks
	call memobook#SilentManage()
    elseif c == "M"
	" print silent marks
	call memobook#SilentDisplay()
    elseif c == "s"
        " scan directories
	call memobook#Scan()
    elseif c == "S"
	" manage scan directories
	call memobook#ScanManage()
    endif
    return
endfunction



let &cpo = s:cpo_save
unlet s:cpo_save

" end of plugin
