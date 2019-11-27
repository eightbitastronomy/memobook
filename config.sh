#!/usr/bin/bash


# Memobook Note Suite installation script for bash
#
# Usage
#   ./config.sh [options]
#   ./config.sh -h ...or... ./config.sh --help ...for options/switches
#
# Default values:
#   Changing installation values should be done on the the command-line,
#   i.e., calling config.sh with switches, since this script builds up 
#   the config vars from the list below, sometimes reusing vars.
#   Despite this, changing the DEFAULT<VAR> vars below might be useful and
#   would break the least of the mechanics of the script if done poorly.
#
#  Author (pseudonomously): eightbitastronomy (eightbitastronomy@protonmail.com)
#  Copyrighted by eightbitastronomy, 2019.
#
#  License information:
#
#  This file is a part of Memobook Note Suite.
#
#  Memobook Note Suite is free software; you can redistribute it and/or
#  modify it under the terms of the GNU General Public License
#  as published by the Free Software Foundation; either version 3
#  of the License, or (at your option) any later version.
#
#  Memobook Note Suite is distributed in the hope that it will be useful,
#  but WITHOUT ANY WARRANTY; without even the implied warranty of
#  MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
#  GNU General Public License for more details.
#
#  You should have received a copy of the GNU General Public License
#  along with this program; if not, write to the Free Software
#  Foundation, Inc., 51 Franklin Street, Fifth Floor, Boston, MA  02110-1301, USA.



LOC=$PWD
DEFAULTCONF="conf.xml"
CONF="conf.xml"
DEFAULTDB="archive.db"
DB="archive.db"
DEFAULTDEX="index.xml"
DEX="index.xml"
MARK="@@"
VIMDIR=$HOME"/.vim"
VIMRC=$HOME"/.vimrc"
VIMPLUG=""
EMACSCONF=$HOME"/.emacsconf.txt"
PYTHONVAR=python3
SQLITE=sqlite3
NOVIM=0
NOPY=0
NOMACS=1



function usage
{
    echo "Configuration script for Memobook Note Suite:"
    echo "Will automatically setup suite from PWD, or the following variables may be set:"
    echo "-b/--basedir [=]   Path to Memobook directory containing pad.py and source subdirectories. Default is PWD"
    echo "-c/--conf [=]      Path to configuration xml file if not BASEDIR/conf.xml"
    echo "-d/--dbfile [=]    Path of sqlite3 database file if not BASEDIR/archive.db"
    echo "-D/--dbbin [=]     Path of alternate sqlite3 binary if not /usr/bin/sqlite3"
    echo "-e/--emacs [=]     Path of emacs configuration file (currently under construction)"
    echo "-E/--noemacs       Disable emacs configuration (currently under construction)"
    echo "-i/--index [=]     Path of silent xml file if not BASEDIR/index.xml"
    echo "-p/--python [=]    Path of alternate python binary if not PATH/python3"
    echo "-P/--nopython      Disable python 3 configuration (currently under construction)"
    echo "-u/--vimplug [=]   Name/type of vim plugin utility (plugin utility must be installed prior; default is to do nothing)"
    echo "-v/--vimrc [=]     Path of vim startup script if not HOME/.vimrc"
    echo "-w/--vimdir [=]    Path of vim directory if not HOME/.vim"
    echo "-V/--novim         Disable emacs configuration (currently under construction)"
}


function resolve_path  #expects argument switches to be removed already  (path,base)
{
    path=$1
    # remove any final /
    path="${1%/}"
    # if the first character is /, treat as an absolute path
    # if the first character is not /, treat as a relative path and prepend the BASE
    if [ "${path:0:1}" != '/' ] ; then
	path=$2"/"$path
    fi
    # check for existence
    if [ ! -d $path ] ; then
	# can we create it?
	mkdir -p $path #2>/dev/null
	if [ $? -ne 0 ]; then
	    ret_var=""
	else
	    ret_var=$path
	fi
    else
	if [ ! -w $path ]; then
	    ret_var=""
	else
	    ret_var=$path
	fi
    fi
}


function resolve_path_and_name # (path_to_be_resolved, base_path)
{
    ret_var=""
    # check that the last character is not /
    path=$1
    last=$((${#path[@]}-1))
    if [ "${path[$last]}" == '/' ]; then
	return 1
    fi
    # is this a file name for the PWD?
    if [ `expr index $path "/"` = 0 ]; then
	altpath=$2"/"$path
	if [ -e $altpath ] && [ -f $altpath ]; then
	    ret_var=$altpath
	    return 0
	else
	    if [ -w $2 ]; then
		ret_var=$altpath
		return 0
	    else
		return 4
	    fi
	fi
    fi
    # check whether the path exists, and whether it's a file
    if [ -e $path ] && [ -f $path ]; then
	ret_var=$path
	return 0
    fi
    # dissect the path into base + file
    file="${path##*/}"
    base="${path%/*}"
    # second, if the first character is /, treat as an absolute path
    # if the first character is not /, treat as a relative path and prepend the PWD
    if [ "${path:0:1}" != '/' ] ; then
	base=$2"/"$base
    fi
    # check for existence
    if [ ! -d $base ] ; then
	# can we create it?
	mkdir -p $base #2>/dev/null
	if [ $? -ne 0 ]; then
	    return 2
	fi
    else
	if [ ! -w $base ]; then
	    return 3
	fi
    fi
    ret_var=$base"/"$file
    return 0
}


function vimrc_entry
{
    ret_var=""
    if [ "${1}" == "vim-plug" ]; then
	ret_var="Plug '${2}'"
	return 0
    fi
}


function skeleton_conf  #  (database-path,index-path,conf-path)
{
    echo "<?xml version=\"1.0\" ?>
<configuration>
   <db>
      <src>$1</src>
      <table>bookmarks</table>
      <scan>.</scan>
    </db>
    <mime>
      <Text>
        <suff>.txt</suff>
      </Text>
      <Image>
        <suff>.blp</suff>
        <suff>.bmp</suff>
        <suff>.cur</suff>
        <suff>.dcx</suff>
        <suff>.dds</suff>
        <suff>.dib</suff>
        <suff>.eps</suff>
        <suff>.fli</suff>
        <suff>.flc</suff>
        <suff>.fpx</suff>
        <suff>.ftex</suff>
        <suff>.gbr</suff>
        <suff>.gd</suff>
        <suff>.gif</suff>
        <suff>.icns</suff>
        <suff>.ico</suff>
        <suff>.im</suff>
        <suff>.imt</suff>
        <suff>.jpeg</suff>
        <suff>.jpg</suff>
        <suff>.mic</suff>
        <suff>.mpo</suff>
        <suff>.msp</suff>
        <suff>.pcd</suff>
        <suff>.pcx</suff>
        <suff>.pixar</suff>
        <suff>.png</suff>
        <suff>.ppm</suff>
        <suff>.psd</suff>
        <suff>.sgi</suff>
        <suff>.tga</suff>
        <suff>.tiff</suff>
        <suff>.wal</suff>
        <suff>.xbm</suff>
        <suff>.xpm</suff>
      </Image>
      <PDF>
        <suff>.pdf</suff>
      </PDF>
    </mime>
    <font>
      <family>FreeSans</family>
      <size>10</size>
      <weight>normal</weight>
    </font>
    <style>
      <theme>default</theme>
      <font>
        <size>0</size>
      </font>
    </style>
    <wrap>word</wrap>
    <save>.</save>
    <open>.</open>
    <loc>.</loc>
    <index>$2</index>
    <x>200</x>
    <y>200</y>
  </configuration>" > $3
}


function skeleton_index   # (index-path)
{
    echo "<?xml version=\"1.0\" ?>
  <contents>
  </contents>" > $1
}


function plugin_vimplug  # (vimdir,vimrc,loc)
{
    # it is assumed that vim-plug has already been installed and configured.
    # if .vimrc is not present, then this assumption is blown; abort.
    [ ! -f $2 ] && echo "vimrc file is absent: cannot make plugin preparations." && return 1
    sed -i "/call plug#begin(/aPlug '${3}'" $2
    cp -r autoload/ $LOC/
    cp -r plugin/ $LOC/
}


function plugin_pathogen # (vimdir,vimrc,loc)
{
    local ret_var
    [ ! -f $2 ] && echo "vimrc file is absent: cannot make plugin preparations." && return 1
    # dealing with 2 possibilities here:
    # 1) alternate .vim subdirectory, 'bundle/{}' --> some other name
    # 2) a second parameter is present, and that's where memobook files should be copied,
    #    e.g., ('bundle/{}','~/mysrc/files/{}')
    bundledir=""
    line_number=$(sed -n "/execute pathogen#infect/=" $2)
    [ ! $line_number ] && echo "Please check pathogen setup in vimrc" && return 1
    line=$(sed -n "${line_number}p" ${2})
    target="${line#execute pathogen#infect(}"
    if [[ "${target}" == ")" ]]; then
	# simplest case: default directory structure
	bundledir=$1/bundle
    else
	pathogenargs=()
	if [[ "${target}" =~ .*,.* ]] ; then
	    # we have multiple arguments
	    IFS="," read -r -a bufferargs <<< "${target}"
	    for arg in ${bufferargs[@]}; do
		strippedleft="${arg#*\'}"
		pathogenargs+=("${strippedleft%/\{\}*}")
	    done
	else
	    strippedleft="${target#*\'}"
	    pathogenargs+=("${strippedleft%/\{\}*}")
	fi
	if ((${#pathogenargs[@]} == 1)); then
	    bundledir="${1}"/"${pathogenargs[0]}"
	else
	    bundledir="${pathogenargs[1]/\~/${HOME}}"
	fi
    fi
    resolve_path "${bundledir}" "${1}"
    [[ ! $ret_var ]] && echo "failed to set bundle directory" && return 1
    target=$ret_var
    targetdirs="autoload plugin docs"
    #if [ $? -ne 0 ]; then #	    return 2 #   fi
    for sub in $targetdirs ; do
	mkdir -p $target/memobook/$sub || return 2
	cp $PWD/$sub/* $target/memobook/$sub/
    done
}


function configure_configs
{
    local ret_var=""
    if [ ! `command -v ${SQLITE}` ]; then
	echo "Command not found: " $SQLITE
	exit 1
    fi
    # basedir / location of memobook: this forms the base of other paths
    resolve_path "${LOC}" "${HOME}"
    [[ ! $ret_var ]] && echo "failed to set base dir" && exit 1
    LOC=$ret_var
    echo "Resolved basedir: " $LOC
    # archive.db
    resolve_path_and_name "${DB}" "${LOC}"
    [[ ! $ret_var ]] && echo "failed to set database source file" && exit 1
    DB=$ret_var
    if [ "${DB}" == "${DEFAULTDB}" ]; then
	DB=$LOC"/"$DEFAULTDB
    fi
    if [ ! -f $DB ]; then
	$SQLITE -line $DB "create table bookmarks (mark NCHAR(255) NOT NULL,file NCHAR(1023) NOT NULL,type SMALLINT);"
    else
	if [ -z "$($SQLITE -line $DB "select * from sqlite_master where type=\"table\" and name=\"bookmarks\";")" ]; then
	    echo "Database file found without bookmarks table. Creating..."
	    $SQLITE -line $DB "create table bookmarks (mark NCHAR(255) NOT NULL,file NCHAR(1023) NOT NULL,type SMALLINT);"
	else
	    echo "Database file found. No need to create bookmarks table."
	fi
    fi
    echo "Prepared archive.db: " $DB
    # conf.xml & index.xml
    resolve_path_and_name "${CONF}" "${LOC}"
    [[ ! $ret_var ]] && echo "failed to set conf xml file" && exit 1
    CONF=$ret_var
    if [ "${CONF}" == "${DEFAULTCONF}" ]; then
	CONF=$LOC"/"$DEFAULTCONF
    fi
    resolve_path_and_name "${DEX}" "${LOC}"
    [[ ! $ret_var ]] && echo "failed to set index xml file" && exit 1
    DEX=$ret_var
    if [ "${DEX}" == "${DEFAULTDEX}" ]; then
	DEX=$LOC"/"$DEFAULTDEX
    fi
    if [ ! -f $CONF ]; then
	skeleton_conf $DB $DEX $CONF
    else
	sed -i "s@^      <src>.*</src>@      <src>${DB}</src>@" $CONF
    fi
    echo "Prepared conf.xml: " $CONF
    if [ ! -f $DEX ]; then
	skeleton_index $DEX
    else
	sed -i "s@^    <index>.*</index>@    <index>${DEX}</index>@" $CONF
    fi
    echo "Prepared index.xml: " $DEX
}


function configure_vim
{
    local ret_var
    echo "Configuring Vim extension."
    resolve_path "${VIMDIR}" "${HOME}"
    [[ ! $ret_var ]] && echo "failed to set vim dir" && exit 1
    VIMDIR=$ret_var
    echo "Resolved Vim dir: " $VIMDIR
    resolve_path_and_name "${VIMRC}" "${PWD}"
    [[ ! $ret_var ]] && echo "failed to set vimrc" && exit 1
    VIMRC=$ret_var
    # edit in-place for memo variables:
    sed -i "s|s:memo_loc = \".*\"|s:memo_loc = \"${LOC}\"|" "autoload/memobook.vim"
    sed -i "s|s:memo_db = \".*\"|s:memo_db = \"${DB}\"|" "autoload/memobook.vim"
    sed -i "s|s:memo_econf = \".*\"|s:memo_econf = \"${CONF}\"|" "autoload/memobook.vim"
    sed -i "s|s:memo_dex = \".*\"|s:memo_dex = \"${DEX}\"|" "autoload/memobook.vim"
    sed -i "s|s:memo_mark = \".*\"|s:memo_mark = \"${MARK}\"|" "autoload/memobook.vim"
    sed -i "s|s:memo_sqlite = \".*\"|s:memo_sqlite = \"${SQLITE}\"|" "autoload/memobook.vim"
    if [ $NOPY == 1 ]; then
	    sed -i "s|memobook#Scan()|memobook#Scann()|g" "plugin/memobook.vim"
    fi
    if [ ! -z $VIMPLUG ]; then
	# MOVE FILE TEST HERE IF ALL PLUGIN UTILS HAVE LINES IN .VIMRC
	case $VIMPLUG in
	    vim-plug)
		(! plugin_vimplug $VIMDIR $VIMRC $LOC) && echo "failed to configure plugin utility" && exit 1
		;;
	    pathogen)
		(! plugin_pathogen $VIMDIR $VIMRC $LOC) && echo "failed to configure plugin utility" && exit 1
		;;
	esac
    fi
    echo "Prepared" $VIMRC "for plugin utility" $VIMPLUG
}


function configure_python
{
    local ret_var=""
    echo "Configuring Python 3 usage."
    # 1) check python command and then check for modules
    if [ ! `command -v ${PYTHONVAR}` ]; then
	echo "Command not found: " $PYTHONVAR
	exit 1
    fi
    $PYTHONVAR pyconfig.py 
    if [ $? -ne 0 ]; then
	echo "failed to configure python 3 modules"
	exit 1
    fi
    # 2) make substitions
    sed -i "s/TAG_MARKER=\".*\"/TAG_MARKER=\"${MARK}\"/" $PWD/memo/config.py
    sed -i "s|^cctrll =.*|cctrll = \"$CONF\"|" pad.py
    sed -i "s|^ddexx =.*|ddexx = \"$DEX\"|" pad.py
    sed -i "s|^python3 .*|python3 $LOC/pad.py|" memobook 
    # 3) make copies to specified directories
    cp -r {pad.py,memod.py,config.sh,memo} $LOC
    # 4) place a link to pad.sh in /usr/local/bin ? or just add something to path in bashrc?
    ## $HOME/.local/bin seems to be a standard place...so check for its existence / add $LOC to path
    if [ -d $HOME/.local/bin ] && [ -w $HOME/.local/bin ]; then
	cp memobook $HOME/.local/bin
    else
	cp memobook $LOC
	    [ ! -f $HOME/.bash_profile ] && echo "Cannot add ${LOC} to path in .bash_profile" && return 1
	    sed -i "s|PATH=.*|:${LOC} &|p" $HOME/.bash_profile
    fi
    echo "Prepared Python 3 modules with command" $PYTHONVAR
}


function configure_emacs
{
    ret_var=""
}


# parse command line

function parse # parse functions
{
    local ret_var=""

    for i in "$@"
    do
	case $i in
	    -b=*|--basedir=*)
		VAR="${i#*=}"
		[[ $VAR ]] || (echo "Unable to parse command-line switches"; exit 1)
		LOC=${VAR/\~/${HOME}}
		shift
		;;
	    -c=*|--conf=*)
		VAR="${i#*=}"
		[[ $VAR ]] || (echo "Unable to parse command-line switches"; exit 1)
		CONF=${VAR/\~/${HOME}}
		shift
		;;
	    -d=*|--dbfile=*)
		VAR="${i#*=}"
		[[ $VAR ]] || (echo "Unable to parse command-line switches"; exit 1)
		DB=${VAR/\~/${HOME}}
		shift
		;;
	    -D=*|--dbbin=*)
		VAR="${i#*=}"
		[[ $VAR ]] || (echo "Unable to parse command-line switches"; exit 1)
		SQLITE=${VAR/\~/${HOME}}
		shift
		;;
	    -e=*|--emacs=*)
		VAR="${i#*=}"
		[[ $VAR ]] || (echo "Unable to parse command-line switches"; exit 1)
		EMACSCONF=${VAR/\~/${HOME}}
		shift
		;;
	    -h|--help)
		usage
		exit 0
		shift
		;;
	    -i=*|--index=*)
		VAR="${i#*=}"
		[[ $VAR ]] || (echo "Unable to parse command-line switches"; exit 1)
		DEX=${VAR/\~/${HOME}}
		shift
		;;
	    -p=*|--python=*)
		VAR="${i#*=}"
		[[ $VAR ]] || (echo "Unable to parse command-line switches"; exit 1)
		PYTHONVAR=${VAR/\~/${HOME}}
		shift
		;;
	    -t=*|-tag=*)
		MARK="${i#*=}"
		[[ $MARK ]] || (echo "Unable to parse command-line switches"; exit 1)
		shift
		;;
	    -u=*|--vimplug=*)
		# for now, only vim-plug and pathogen will be supported
		VAR="${i#*=}"
		[[ $VAR ]] || (echo "Unable to parse command-line switches"; exit 1)
		VIMPLUG=$VAR
		shift
		;;
	    -v=*|--vimrc=*)
		VAR="${i#*=}"
		[[ $VAR ]] || (echo "Unable to parse command-line switches"; exit 1)
		VIMRC=${VAR/\~/${HOME}}
		shift
		;;
	    -w=*|--vimdir=*)
		VAR="${i#*=}"
		[[ $VAR ]] || (echo "Unable to parse command-line switches"; exit 1)
		VIMDIR=${VAR/\~/${HOME}}
		shift
		;;
	    -E|--noemacs)
		NOMACS=1
		shift
		;;
	    -P|--nopython)
		NOPY=1
		shift
		;;
	    -V|--novim)
		NOVIM=1
		shift
		;;
	    *)
		# unknown option
		echo "Unknown option: ${i}"
		break
		;;
	esac
    done

    if [[ -n $1 ]]; then
	exit 1
    fi
}



parse "$@"
configure_configs
[ $NOVIM == 0 ] && configure_vim
[ $NOPY == 0 ] && configure_python
[ $NOMACS == 0 ] && configure_emacs


exit 0


