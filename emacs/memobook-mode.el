;;###############################################################################################
;;  memobook-mode.el: minor-mode code for emacs to implement memobook functionality
;;
;;  Author (pseudonomously): eightbitastronomy (eightbitastronomy@protonmail.com)
;;  Copyrighted by eightbitastronomy, 2020.
;;
;;  License information:
;;
;;  This file is a part of Memobook Note Suite. This file is not part of GNU Emacs.
;;
;;  Memobook Note Suite is free software; you can redistribute it and/or
;;  modify it under the terms of the GNU General Public License
;;  as published by the Free Software Foundation; either version 3
;;  of the License, or (at your option) any later version.
;;
;;  Memobook Note Suite is distributed in the hope that it will be useful,
;;  but WITHOUT ANY WARRANTY; without even the implied warranty of
;;  MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
;;  GNU General Public License for more details.
;;
;;  You should have received a copy of the GNU General Public License
;;  along with this program; if not, write to the Free Software
;;  Foundation, Inc., 51 Franklin Street, Fifth Floor, Boston, MA  02110-1301, USA.
;;###############################################################################################








;; TO-DO LIST:
;;       
;;        reading from db brings up non-text files...anything that matches query. 
;;           Can either filter at db or filter here or allow non-texts to be selected but not loaded
;;
;;        implement scan directories without python =(
;;
;;        12 may 2020







;;-------------------------------------------global--------------------------------------------------------------------------------




(defvar *MB-dex-tree* nil)




;;-------------------------------------------buffer local--------------------------------------------------------------------------------




(make-variable-buffer-local (defvar memobook-mode nil))

(make-variable-buffer-local (defvar MB-loc "/home/travertine/code/memobook"))

(make-variable-buffer-local (defvar MB-db "/home/travertine/code/memobook/archive.db"))

(make-variable-buffer-local (defvar MB-index "/home/travertine/code/memobook/index.xml"))

(make-variable-buffer-local (defvar MB-conf "/home/travertine/code/memobook/conf.xml"))

(make-variable-buffer-local (defvar MB-tag "@@"))

(make-variable-buffer-local (defvar MB-read-by-mark 'arch-sqlite3-read-by-mark))

(make-variable-buffer-local (defvar MB-add-mark 'arch-sqlite3-add-mark))

(make-variable-buffer-local (defvar MB-del-mark 'arch-sqlite3-delete-mark))

(make-variable-buffer-local (defvar MB-read-by-file 'arch-sqlite3-read-by-file))

(make-variable-buffer-local (defvar MB-clear 'arch-sqlite3-clear))

(make-variable-buffer-local (defvar silent-marks nil))

(make-variable-buffer-local (defvar silent-marks-loaded nil))







;-------------------------------------------mode setup--------------------------------------------------------------------------------







(defun memobook-mode (&optional arg)
  "Turn minor mode memobook book on or off"
  (interactive (list (or current-prefix-arg 'toggle)))

  (let ((enable
	(if (eq arg 'toggle)
	    (not memobook-mode) ; this is the mode's mode variable
	  (> (prefix-numeric-value arg) 0))))

    (if enable

	(progn "enabled"

	  (setq memobook-mode 1)
	  (make-save-hook)
	  ;(princ (key-binding "M-m C-b")) ;;M-m appears to be unbound, but C-m like Vim is tied to Return key
	  (local-set-key (kbd "M-m w") 'mb-write-marks)            ; WRITE MARKS WITHOUT SAVE
	  (local-set-key (kbd "M-m s") 'mb-source-scan)            ; SCAN SOURCE DIRECTORIES
	  (local-set-key (kbd "M-m C-s") 'mb-source-manage)        ; MANAGE SOURCE DIRECTORIES
	  (local-set-key (kbd "M-m c") 'mb-source-clear)           ; CLEAR DATABASE
	  (local-set-key (kbd "M-m C-n") 'mb-silentmark-manage)   ; MANAGE SILENT MARKS
	  (local-set-key (kbd "M-m n") '(lambda ()		; ADD MARK TO SILENT LIST
					    (interactive)
					    (if (use-region-p)
						(mb-silentmark-add nil (region-beginning) (region-end) (thing-at-point 'word))
					      (mb-silentmark-add nil nil nil (thing-at-point 'word)))))
	  (local-set-key (kbd "M-m m") '(lambda ()		; READ MARK "OR"
					    (interactive)
					    (if (use-region-p)
						(mb-readmarks-or nil (region-beginning) (region-end) (thing-at-point 'word))
					      (mb-readmarks-or nil nil nil (thing-at-point 'word)))))					 
	  (local-set-key (kbd "M-m C-m") '(lambda ()		; READ MARK "AND"
					    (interactive)
					    (if (use-region-p)
						(mb-readmarks-and nil (region-beginning) (region-end) (thing-at-point 'word))
					      (mb-readmarks-and nil nil nil (thing-at-point 'word)))))
	  ) ; progn enabled
      
      (progn "disabled"

	     (setq memobook-mode nil)
	     (local-unset-key (kbd "M-m w"))
	     (local-unset-key (kbd "M-m s"))
	     (local-unset-key (kbd "M-m C-s"))
	     (local-unset-key (kbd "M-m c"))
	     (local-unset-key (kbd "M-m n"))
	     (local-unset-key (kbd "M-m C-n"))
	     (local-unset-key (kbd "M-m m"))
	     (local-unset-key (kbd "M-m C-m"))
	     (unmake-save-hook)

	     ) ; progn disabled

      ) ; if enable
    
    ) ; let enable
  
  )








;-------------------------------------------functions--------------------------------------------------------------------------------



  





(defun arch-sqlite3-clear ()
  "Clear the database of bookmarks (i.e., delete the bookmarks table and recreate it)"
  
  (shell-command-to-string (concat "sqlite3 -line " MB-db " 'drop table bookmarks;'"))
  (shell-command-to-string (concat "sqlite3 -line " MB-db " 'create table bookmarks (mark NCHAR(255) NOT NULL,file NCHAR(1023) NOT NULL,type SMALLINT);'"))
  
   )









(defun arch-sqlite3-read-by-mark (fields params)
  "Fetch records from database based on mark"
  
  (shell-command-to-string (concat "sqlite3 -line " MB-db " 'select " (join-fields fields ",") " from bookmarks where mark=\"" params "\";'"))

  )








(defun arch-sqlite3-read-by-file (fields params)
  "Fetch records from database based on file name"

  (shell-command-to-string (concat "sqlite3 -line " MB-db " 'select " (join-fields fields ",") " from bookmarks where file=\"" params "\";'"))

  )








(defun arch-sqlite3-add-mark (title type mark-list)
  "Save marks to database"

  (if (not title)
      nil)

  (if (not mark-list)
      nil)

  (let ((type-holder nil))

    (if (numberp type)
	(setq type-holder (number-to-string type))
      (setq type-holder type))
    
    (while mark-list

      (shell-command-to-string (concat "sqlite3 -line " MB-db " 'insert into bookmarks (mark,file,type) values (\"" (car mark-list) "\",\"" title "\",\"" type-holder "\");'"))
      (setq mark-list (cdr mark-list))
      
      ) ; while mark-list

    ) ; let type-holder
  
  )







(defun arch-sqlite3-delete-mark (title mark-list)
  "Remove marks from database"

  (if (not title)
      nil)

  (if (not mark-list)
      nil)

  (while mark-list

    (shell-command-to-string (concat "sqlite3 -line " MB-db " 'delete from bookmarks where file=\"" title "\" and mark=\"" (car mark-list) "\";'"))
    (setq mark-list (cdr mark-list))

    ) ; while mark-list
  
  )







    

(defun fetch-by-mark (logic tlist)
  "Core functionality for mb-readmarks-XX. Logic 0=or, 1=and."

  (let ((target-list tlist)
	(retcall-list nil)
	(sets nil)
	(refined nil))

    (if (stringp target-list)
	(setq retcall-list (list (funcall MB-read-by-mark '("rowid" "file") target-list)))
      (setq retcall-list (mapcar '(lambda (x) (funcall MB-read-by-mark '("rowid" "file") x)) target-list))) ; if stringp

    (setq sets (mapcar '(lambda (x) (make-records (parse x '("rowid =" "file =" nil)) 2 0 0 0)) retcall-list))
    
    (if (eql logic 0)
	(setq refined (set-oper-or sets 1))
      (setq refined (set-oper-and-combined sets 1)))

    (if refined
	(post-files-to-buffers (make-option-buffer refined "Please select files to open"))
      (princ "No matching files found"))

    ) ; let target-list

  )









(defun join-fields (fields sep)
  "De-parsing function for database calls."

  (if (> (safe-length fields) 1)

      (let ((whole (car fields)))
	
	(setq fields (cdr fields))
	
	(while fields

	  (setq whole (concat whole sep (car fields)))
	  (setq fields (cdr fields))) ; while fields

	whole) ; let whole

    (car fields)

    ) ; if

  )










(defun make-option-buffer (opt banner)
  "Creates a temp buffer for choice lists, processes user's choices and returns choices as a list"
  
  ;(princ "Make-option-buffer")
  ;(terpri)
  
  (let ((tmp-opt opt)
	(numbering 0)
	(choices nil)
	(w-list (window-list)))
    

    (save-selected-window
    (with-output-to-temp-buffer "*Option List*"

      (while tmp-opt
	
	(setq numbering (1+ numbering))
	(princ (concat (number-to-string numbering) ". " (car tmp-opt)))
	(terpri)
	(setq tmp-opt (cdr tmp-opt))
	) ; while tmp-opt
      
      ) ; with-output

    ) ; save-selected
    
    (mapcar '(lambda (x) (if choices
			  (setq choices (append choices (list (nth x opt))))
			(setq choices (list (nth x opt))))) ; lambda
	 (parse-numbers-list (read-string (concat banner " (ex: 1,2,3-6,10 or nothing): ")) )) ; map

    (kill-buffer "*Option List*")

    (if (not (equal (safe-length w-list) (safe-length (window-list))))
	(delete-window (car (last (window-list)))))

    choices
    
    ) ; let tmp-opt
  
  )








(defun make-records (reclist fields id-f path-f marks-f)
  "Parse a list and form a list of lists. To-do: either use all the fctn args or trim them down."
  
  (let ((bldlist nil)
	(bld nil)
	(counter fields))

    (while reclist

      (while (> counter 0)
	
	(if (not bld)
	    (setq bld (list (car reclist)))
	  (setq bld (append bld (list (car reclist)))))

	(setq reclist (cdr reclist))
	(setq counter (1- counter))

	) ; while >

      (if (not bldlist)
	  (setq bldlist (list bld))
	(setq bldlist (append bldlist (list bld))))

      (setq bld nil)
      (setq counter fields)

      ) ; while reclist

    bldlist

    ) ; let bldlist

  )








(defun make-save-hook ()
  (add-hook 'after-save-hook 'write-marks)
  )









(defun manage-items (original itemsname)
  "Core functionality for mb-silentmark-manage, etc, which provide addition and removal interfaces"

  (if (not original)
      nil)

  (let ((choices nil)
	(final original))

    (setq choices (make-option-buffer original (concat "Please select " itemsname " to remove")))

    (while choices

      (setq final (remove (car choices) final))
      (setq choices (cdr choices))
	
      ) ; while choices

    (setq choices (parse (read-string (concat "Add " itemsname ": ")) '(nil "," ";" ":")))

    (if choices

	(if final
	    (setq final (append final choices))
	  (setq final choices))

      ) ; if choices

    (if final
	(delete-dups final))
    
    ) ; let choices
  
  )









(defun mb-readmarks-and (&optional entry start stop mark)
  "Read marks from db: AND logic"
  (interactive)

  (let ((targets (if entry
		     (parse entry '(nil "," ";" ":"))
		   (if (or (or (not start) (not stop)) (and (eql start 0) (eql stop 0)))
		       (if (not mark) (parse (read-string "Search by mark(s): ") '(nil "," ";" ":")) mark)
		     (parse (buffer-substring (region-beginning) (region-end)) '(nil "," "\\." ";" ":" "\n"))))))

    (fetch-by-mark 1 targets)

    ) ; let targets
  
  )







(defun mb-readmarks-or (&optional entry start stop mark)
  "Read marks from db: OR logic"
  (interactive)

  (let ((targets (if entry
		     (parse entry '(nil "," ";" ":"))
		   (if (or (or (not start) (not stop)) (and (eql start 0) (eql stop 0)))
		       (if (not mark) (parse (read-string "Search by mark(s): ") '(nil "," ";" ":")) mark)
		     (parse (buffer-substring (region-beginning) (region-end)) '(nil "," "\\." ";" ":" "\n"))))))

    (fetch-by-mark 0 targets)
    
    ) ; let targets
  
  )








(defun mb-silentmark-add (&optional entry start stop mark)
  "Add silent mark to buffer runtime list, silent-marks"
  (interactive)

  (let ((targets (if entry
		     (parse entry '(nil "," ";" ":"))
		   (if (or (or (not start) (not stop)) (and (eql start 0) (eql stop 0)))
		       (if (not mark) (parse (read-string "Add silent marks: ") '(nil "," ";" ":")) (list mark))
		     (parse (buffer-substring (region-beginning) (region-end)) '(nil "," "\\." ";" ":" "\n")))))
	(subtarget nil))

    (if targets
	
	(progn

	  (if (not silent-marks)
	      (setq silent-marks (xml-read-silent-marks (buffer-file-name))))
	  
	  (if silent-marks
	      (setq silent-marks (delete-dups (append silent-marks targets)))
	    (setq silent-marks targets))
	  
	  (princ "Marks added")

	  ) ; progn
      
      ) ; if targets
    
    ) ; let targets
  )








(defun mb-silentmark-manage ()
  "Add/remove silent marks for current buffer"
  (interactive)

  (if (not silent-marks)
      	(setq silent-marks (xml-read-silent-marks (buffer-file-name))))

  (setq silent-marks (manage-items silent-marks "silent marks"))

  )










(defun mb-source-clear ()
  "Clear the mb database"
  (interactive)
  
  (if (string= (read-string "Clear the memobook database? (y/n):") "y")
      (funcall MB-clear))
  
  )








(defun mb-source-manage ()
  "Add/remove source directories"
  (interactive)
  
  (let ((stored-sources (xml-get-child-value (xml-get-node-by-match (xml-process-tree (xml-read-conf-tree)) "table" "bookmarks") "scan"))
	(pending-sources nil)
	(record-pair nil))

    (if (not stored-sources)
	nil)

    (setq pending-sources (tilde-expand (manage-items stored-sources "scan directories")))

    (save-current-buffer

      (set-buffer (find-file-noselect MB-conf nil nil nil))

      (goto-char (point-min))
      (setq record-pair (xml-simple-target-entry "<db>" "</db>"))
	  
      (if (not record-pair)
	  nil)

      (setq record-start (car record-pair))
      (setq record-stop (cadr record-pair))
      (delete-region record-start record-stop)
      (insert (concat "<db>\n"))
      (insert (concat "      <src>" MB-db "</src>\n"))
      (insert (concat "      <table>bookmarks</table>\n"))

      (while pending-sources
	(insert (concat "      <scan>" (car pending-sources) "</scan>\n"))
	(setq pending-sources (cdr pending-sources)))

      (insert "    </db>")

      (save-buffer)
      
      ) ; save-current-buffer
    
    ) ; let stored-sources

  )








(defun mb-source-scan ()
  "Scan source directories for marks"
  (interactive)
  
  ;scan directories recursively
  ;load silent index

  ; Python3 version:

  (shell-command-to-string (concat "python3 " MB-loc "/memod.py --ctrl=" MB-conf " --populate"))
  (princ "Memobook database populated.")
  
  )







(defun mb-write-marks ()
  "Call write-marks function directly, i.e., write marks without saving buffer to disk"
  (interactive)

  (if (not (buffer-file-name))
      nil
    (progn
      (write-marks)
      (princ (concat "Bookmarks written for " (buffer-file-name)))
      ))
  
  )






  


(defun parse (whole &optional seps)
  "Parse strings to remove various separators, return list of resultant strings"
  
  (setq working-list nil)
  
  (let ((working-seps seps))

    (while working-seps

      (let ((targ-sep (car working-seps)))
	
	(if (not working-list)
	    (setq working-list (stripper whole targ-sep))
	  (setq working-list (stripper working-list targ-sep))) ; if not
	
	(setq working-seps (cdr working-seps)))) ; while working-seps

    ) ; let working-seps

  (remove "" (remove nil working-list))

  )








(defun parse-numbers-list (numbers)
  "Parse choice-lists entered by users. If form is 1,2,4-7,9, return (1 2 4 5 6 7 9)"

  (if (not numbers)
      nil

    (let ((nums-list nil)
	  (segments (parse numbers '(nil ",")))
	  (subrange nil)
	  (len 0)
	  (stop 0)
	  (counter 0))

      (while segments
	
	(setq subrange (split-string (car segments) "-"))
	(setq len (safe-length subrange))

	(if (equal 2 len)

	    (if (and (natnump (string-to-number (car subrange))) (natnump (string-to-number (car (cdr subrange)))))

		(progn
		  
		  (setq counter (string-to-number (car subrange)))
		  (setq stop (string-to-number (car (cdr subrange))))

		  (while (<= counter stop)
		    (if nums-list
			(setq nums-list (append nums-list (list (1- counter))))
		      (setq nums-list (list (1- counter))))
		    (setq counter (1+ counter))
		    ) ; while start
		  
		  ) ; progn
	      
	      ) ; if and natnump
	
	  (if (and (equal 1 len) (natnump (string-to-number (car subrange))))

	      (if nums-list
		  (setq nums-list (append nums-list (list (1- (string-to-number (car subrange))))))
		(setq nums-list (list (1- (string-to-number (car subrange))))))
	    
	    ) ; if and equals 1
	  
	  ) ; if equals 2
	
	(setq segments (cdr segments))
	
	) ; while segments
      
      nums-list

      ) ; let choices
    
    ) ; if not numbers
  
  )









(defun post-files-to-buffers (flist)
  "utility function: takes a list of file names and 'visits' them, i.e., reads them into buffers"
  
  (while flist
    (find-file-noselect (car flist))
    (setq flist (cdr flist))
    ) ; while flist
  
  )








(defun remove-last-slash (str)
  "File path processing"

  (let ((len (length str)))

    (if (string= "/" (substring str (- len 1) len))
	(substring str 0 (- len 1))
      str)

    ) ; let len
  
  )








(defun scan-for-marks ()
  "Scans buffer for open marks"
  (interactive)

  (let ((wordlist nil)
	(bufstr nil))
  
    (save-excursion

      (goto-char (point-min))

      (while (re-search-forward (concat MB-tag "[a-z\-0-9]+") nil t)

	(setq bufstr (match-string 0))
	
	(if wordlist
	    (setq wordlist (append wordlist (list (substring bufstr 2 (length bufstr)))))
	  (setq wordlist (list (substring bufstr 2 (length bufstr)))))
	
	) ; while re-search-forward
      
      ) ; save-excursion

    wordlist
    
    ) ; let placeholder
  
  )







(defun set-oper-and-atomic (&rest sets)
  "Returns intersection of sets using test-function."

  (if (not sets)
      nil)

  (if (< (safe-length sets) 2)
      sets)

  (let ((item-hash (make-hash-table :test 'equal))
	(listlen (safe-length sets))
	(working-set nil)
	(working-item nil)
	(final nil)
	(hashbuffer -1))

    (while sets

      (setq working-set (car sets))

      (while working-set

	(setq working-item (car working-set))
	(setq hashbuffer (gethash working-item item-hash 0))

	(if (equal hashbuffer 0)
	    (puthash working-item 1 item-hash)
	  (puthash working-item (1+ hashbuffer) item-hash))

	(setq working-set (cdr working-set))
	
	) ; while working-set
      
      (setq sets (cdr sets))
      
      ) ; while sets

    (maphash '(lambda (key val) (if (equal val listlen)
				    (if final
					(setq final (append final (list key)))
				      (setq final (list key))))) ; lambda
	     item-hash) ; maphash

    final

    ) ; let item-hash
  
  )







(defun set-oper-and-combined (set-list key-position)
  "Set operation: intersection. For lists that have been combined into sublists."

  (let ((item-hash (make-hash-table :test 'equal))
	(length (safe-length set-list))
	(final nil))

    (while set-list

      (let ((subset (car set-list))
	    (hashbuffer -1))

	(while subset

	  (setq hashbuffer (gethash (nth key-position (car subset)) item-hash 0))

	  (if (equal hashbuffer 0)
	      (puthash (nth key-position (car subset)) 1 item-hash)
	    (puthash (nth key-position (car subset)) (1+ hashbuffer) item-hash))

	  (setq subset (cdr subset))) ; while subset
	
	) ; let subset

      (setq set-list (cdr set-list))) ; while set-list

    (maphash '(lambda (key val) (if (equal val length)
				    (if final
					(setq final (append final (list key)))
				      (setq final (list key))))) ; lambda
	     item-hash) ; maphash
				    
    final

    ) ;let item-hash
  
  )






(defun set-oper-diff (first second)
  "Finds the difference in two sets, where the first is the target/final set. Returns ((to be added)(to be removed)) so that the second set can be brought into agreement with the first"

  (let ((intersection (set-oper-and-atomic first second))
	(adding nil)
	(removing nil)
	(temp nil))

    (if intersection

	(while intersection
	  (setq temp (car intersection))
	  (setq first (remove temp first))
	  (setq second (remove temp second))
	  (setq intersection (cdr intersection))
	  ) ; while intersection

      ) ; if intersection

    (setq adding first)
    (setq removing second)

    (list adding removing)
    
    ); let intersection
  
  )







(defun set-oper-or (set-list key-position)
  "Set operation: union"

  (let ((item-hash (make-hash-table :test 'equal))
	(length (safe-length set-list))
	(final nil))

    (while set-list

      (let ((subset (car set-list)))

	(while subset

	  (puthash (nth key-position (car subset)) 1 item-hash)
	  (setq subset (cdr subset))
	  
	  ); while subset
	 
	(setq set-list (cdr set-list))
	
	) ; let subset

      ) ; while set-list

    (maphash '(lambda (key val) (if final
				    (setq final (append final (list key)))
				  (setq final (list key)))) ; lambda
	     item-hash) ; maphash
				    
    final

    ) ;let item-hash
  
  )










(defun stripper (x y)
  "Strips y from string x by means of string splitting"
  
  (if (stringp x)
      (split-string x y)
    (apply 'append (mapcar (lambda (a) (split-string a y)) x)))

  )








(defun tilde-expand (dirs)
  "Replace tilde with home path"

  (if (not dirs)
      nil)

  (let ((home (getenv "HOME"))
	(index nil)
	(working nil)
	(splitbuf nil)
	(final nil))

    ; do replacement for any tilde in the string

    (while dirs

      (setq working (car dirs))
      (setq index (string-match "~" working))

      (if (not index)
	  
	  (setq final (append final (list (remove-last-slash working))))
	
	(if (= index 0)
	    
	    (setq final (append final (list (remove-last-slash (concat home (substring working 1))))))

	  (progn "split"
		 (setq splitbuf (split-string working "~"))
		 (setq final (append final (list (remove-last-slash (concat (car splitbuf) home (cadr splitbuf))))))
		 ) ; progn split
	  
	  ) ; if = index

	) ; if < index
      

      (setq dirs (cdr dirs))
      
      ) ; while dirs

    final
    
    ) ; let home
  
  )









(defun unmake-save-hook ()
  (remove-hook 'before-save-hook 'write-marks)
  )








(defun write-marks ()
  "Memobook: write marks to database"

  (let ((working-open-marks (scan-for-marks))
	(working-sil-marks silent-marks)
	(stored-sil-marks nil)
	(stored-open-marks (parse (funcall MB-read-by-file '("mark") (buffer-file-name)) '("mark =" nil)))
	(pending-db-marks nil)
	(pending-sil-marks nil)
	(sil-write-flag nil)
	(sil-file-type nil))

    ;(princ (concat "Writing marks for " (buffer-file-name)))
    ;(terpri)
    ;(princ (format "Working open: %s" working-open-marks))
    ;(terpri)
    ;(princ (format "Working sil: %s" working-sil-marks))
    ;(terpri)
    ;(princ (format "Stored open: %s" stored-open-marks))
    ;(terpri)

    (if silent-marks-loaded

	(progn "touched"

	       (setq stored-sil-marks (xml-read-silent-marks (buffer-file-name)))
	       (setq pending-sil-marks (set-oper-diff working-sil-marks stored-sil-marks))

	       ;(princ (format "pending sil diff is: %s" pending-sil-marks))
	       ;(terpri)

	       (if (or (car pending-sil-marks) (car (cdr pending-sil-marks)))
		   
		   (progn "silwrite"
			  (setq sil-write-flag t)
			  (setq sil-file-type (xml-get-file-type))
			  ) ; progn silwrite
		 
		 ) ; if or car
	       
	       ) ; progn touched
      
      (progn "untouched"

	     (setq stored-sil-marks (xml-read-silent-marks (buffer-file-name)))
	     (setq working-sil-marks stored-sil-marks)

	     ) ; progn untouched
      
     ) ; if silent-dex-tree
    
    (setq working-open-marks (append working-open-marks working-sil-marks))
    (setq pending-db-marks (set-oper-diff working-open-marks stored-open-marks))

    ;(princ (format "To be added to db: %s" (car pending-db-marks)))
    ;(terpri)
    ;(princ (format "To be removed from db: %s" (car (cdr pending-db-marks))))
    ;(terpri)
    ;(princ (format "To be added to dex: %s" (car pending-sil-marks)))
    ;(terpri)
    ;(princ (format "To be removed from dex: %s" (car (cdr pending-sil-marks))))
    ;(terpri)

    ; although a set-diff was done on working-vs-stored sil marks, only the working ones will be written (entire record is rewritten)
    (if sil-write-flag
	(xml-dex-entry-write (buffer-file-name) sil-file-type working-sil-marks))

    (funcall MB-add-mark (buffer-file-name) sil-file-type (car pending-db-marks))
    (funcall MB-del-mark (buffer-file-name) (cadr pending-db-marks))
    
    ) ; let working-open-marks

  )









(defun xml-dex-entry-write (loc type &optional marks)
  "Inserts xml/dex entry at a given file position"

  (if (not loc)
      nil)

  (if (not type)
      nil)
  
  (let ((record-start nil)
	(record-stop nil)
	(record-pair nil)
	(type-holder nil)
	(curr-pt 0)
	(new-line-flag nil))

    (if (numberp type)
	(setq type-holder (number-to-string type))
      (setq type-holder type))

    (with-temp-file MB-index
      
      (insert-file-contents MB-index nil nil nil)
      (goto-char (point-min))
      (setq record-pair (xml-dex-target-entry loc))
	  
      (if (not record-pair)
	  nil)

      (setq record-start (car record-pair))
      (setq record-stop (cadr record-pair))

      (if (not (= record-start record-stop))
	  
	  (delete-region record-start record-stop)
	
	(progn "new"
	       (goto-char record-start)
	       (setq type-holder "0")
	       (setq new-line-flag t)
	       ) ; progn new
	
	) ; if not =
      
      (insert (concat "<file type=\"" type-holder "\">\n"))
      (insert (concat "      <loc>" loc "</loc>\n"))

      (while marks
	(insert (concat "      <mark>" (car marks) "</mark>\n"))
	(setq marks (cdr marks)))

      (if new-line-flag
	  (insert "    </file>\n    ")
	(insert "    </file>"))

      ) ; with-temp-file
    
    ) ; let record-start
  
  )








(defun xml-get-child-value (node tag)
  "Return the associated value(s) for matching tag"
  
  (if (not node)
      nil)
  
  (let ((hits nil)
	(item (cdr (cdr node))))

    (while item

      (if (listp (car item))
	  (if (string= (car (car item)) tag)
		(if hits
		    (setq hits (append hits (last (car item))))
		  (setq hits (last (car item))))))

      (setq item (cdr item))
      
      ) ; while item

    hits
    
    ) ; let hits
  
  )







(defun xml-get-file-type ()
  "Returns mime type-number from silent-dex-tree. Will not load silent-dex-tree, returns nil instead."

  (if (not *MB-dex-tree*)
      (xml-read-dex-tree))

  ;If the read was unsuccessful, return nothing
  (if (not *MB-dex-tree*)
      nil)

  (let ((node (xml-get-node-by-match (xml-process-tree *MB-dex-tree*) "loc" (buffer-file-name)))
	(retval nil))

    (setq retval (cdar (cadr node)))

    retval
    
    ) ; let node
  
  )






(defun xml-get-node-by-match (dex loc val)
  "Return the node of a Xml/Dom tree with matching loc tag"

  ;(princ (concat "XML get node by loc: " loc))
  ;(terpri)
  
  (if (not dex)
      nil)
  (if (not loc)
      nil)

  (let ((hit nil)
	(tree-node dex)
	(node-item nil))

    (while tree-node

      (setq node-item (car tree-node))

      (if (listp node-item)
	  (if (string= (car (xml-get-child-value node-item loc)) val)	      
	      (progn
		(setq hit node-item)
		(setq tree-node nil)
		) ; progn
	    ) ; if string=
	) ; if listp
	
      (if tree-node
	  (setq tree-node (cdr tree-node)))
      
      ) ; while tree-node

    hit
    
    ) ; let hit
  
  )










(defun xml-process-tree (tree)
  "Prepare/strip Xml-dom object for further use"

  ;(princ "XML process dex tree")
  ;(terpri)
  
  (let ((temptree (cdr (car tree)))
	(templist nil))
    
    (setq temptree (remove nil temptree))

    (while temptree

      (if (listp (car temptree))
	  (if templist
	      (setq templist (append templist (list (car temptree))))
	    (setq templist (list (car temptree)))))
      
      (setq temptree (cdr temptree))

      ) ; while temptree

    templist

    ) ; let temptree

  )









(defun xml-read-conf-tree ()
  "function to read silent index XML into a DOM"
  (interactive)

  (with-temp-buffer
	  
    (insert-file-contents MB-conf nil nil nil)
    (goto-char (point-min))
    (setq *MB-conf-tree* (xml-parse-region (point-min) (point-max)))

    ) ; with-temp-buffer
      
  )







(defun xml-read-dex-tree ()
  "function to read silent index XML into a DOM"
  (interactive)

  (with-temp-buffer
	  
    (insert-file-contents MB-index nil nil nil)
    (goto-char (point-min))

    ;both of these work and produce, structurally, the same object. the second is more legible when printed.
    ;(setq doc-index (libxml-parse-xml-region (point-min) (point-max)))
    (setq *MB-dex-tree* (xml-parse-region (point-min) (point-max)))

    ) ; with-temp-buffer
      
  )






(defun xml-read-silent-marks (filename)
  "Return marks for a file using silent index"

  ;Read in the silent index if it hasn't been done so
  (if (not *MB-dex-tree*)
      (xml-read-dex-tree))

  ;If the read was unsuccessful, return nothing
  (if (not *MB-dex-tree*)
      nil)

  (setq silent-marks-loaded t)
  (xml-get-child-value (xml-get-node-by-match (xml-process-tree *MB-dex-tree*) "loc" filename) "mark")
  
  )








(defun xml-simple-target-entry (tag untag)
  "Returns (start stop) write positions for xml. Returns nil if not found or if xml is badly formed."

  (if (not tag)
      nil)

  (if (not untag)
      nil)

  (let ((target nil)
	(tag-begin -1)
	(break-flag nil))

    (while (not break-flag)
      
      (if (re-search-forward tag nil t)
	  
	  (progn "tag open"

		 (setq tag-begin (- (point) (length tag)))
		 
		 (if (re-search-forward untag nil t)
		     (setq target (list tag-begin (point)))
		   (setq break-flag t))
		   
		 ) ; progn "tag open"
	
	(setq break-flag t)

	) ; if re-search file
      
      ) ; while not break-flag

    target
    
    ) ; let contents
  
  )








(defun xml-dex-target-entry (loc)
  "Returns (start stop) write positions for xml-dex-entry-write. Returns nil if not found or if xml is badly formed."

  (if (not loc)
      nil)

  (let ((target nil)
	(file-begin -1)
	(file-end -1)
	(loc-start -1)
	(loc-stop -1)
	(break-flag -1)   ; 0 is success, 1 is reached-the-end, 2 is unclosed-tag
	(first-file -1))

    (while (= break-flag -1)
      
      (if (re-search-forward "<file " nil t)
	  
	  (progn "file open"

		 (setq file-begin (- (point) 6))

		 (if (= first-file -1)
		     (setq first-file file-begin))
		 
		 (if (re-search-forward "</file>" nil t)
		     
		     (progn "file close"

			    (setq file-end (point))
			    (goto-char file-begin)

			    (if (re-search-forward "<loc>")

				(progn "loc start"

				       (setq loc-start (point))
				       
				       (if (re-search-forward "</loc>")
					   
					   (progn "loc end"

						  (setq loc-stop (- (point) 6))
						  
						  (if (string= (buffer-substring loc-start loc-stop) loc)
						      (progn "found"
							     (setq break-flag 0)
							     (setq target (list file-begin file-end))
							     )) ; progn found, if string=
						  
						  ) ; progn loc end
					 
					 ) ; if re-search /loc

				       ) ; progn loc start
			      
			      ) ; if re-search loc
			     
			    ) ; progn file close
		   
		   (setq break-flag 2)
		   
		   ) ; if re-search /file
		   
		 ) ; progn "file open"

	(setq break-flag 1)

	) ; if re-search file
      
      ) ; while not break-flag

    ; test for reached-the-end and set target accordingly. In any other case, target should be untouched.
    (if (= break-flag 1)
	(setq target (list first-file first-file)))
	
    target
    
    ) ; let contents
  
  )







;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;; EMACS PLUGIN STUFF ;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;






(add-hook 'text-mode-hook 'memobook-mode)




;;;###autoload
(provide 'memobook-mode)
