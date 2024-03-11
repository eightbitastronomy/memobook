###############################################################################################
#  extconf.py: External Configuration loading and saving class
#
#  Author: Miguel Abele
#  Copyrighted by Miguel Abele, 2020.
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
###############################################################################################



'''XML-Dictionary hybrid class'''



import xml.dom.minidom
import sys
import memo.scrubber as scrubber
import memo.config as conf
from memo.debug import dprint





    
class Configuration(dict):

    '''Structured container class for XML information/trees, as abstruse as possible'''
    

    def __init__(self, doc, nd=None, parent=None):
        dprint(3, "\nConfiguration::__init__")
        self.__doc = doc
        self.__src = nd
        self.__parent = parent
        self.__attr = None

        
    def getdoc(self):
        '''Get XML document object'''
        dprint(3, "\nConfiguration::getdoc")
        return self.__doc

    
    def getnode(self):
        '''Get node in XML document corresponding to Configuration object'''
        dprint(3, "\nConfiguration::getnode")
        return self.__src

    
    def setnode(self, s):
        '''Set XML document node for Configuration object'''
        dprint(3, "\nConfiguration::setnode")
        self.__src = s

        
    def getparent(self):
        '''Get parent node of Configuration object'''
        dprint(3, "\nConfiguration::getparent")
        return self.__parent

    
    def setparent(self, s):
        '''Set parent node of Configuration object'''
        dprint(3, "\nConfiguration::setparent")
        self.__parent = s

        
    def add_data_from_xml(self, key, val):
        '''Add key,val pair to Configuration dictionary. For use with XML parsing'''
        # Keys have associated tuples of values, so if key is already present,
        # this function primarily determines how to add the val to appropriate tuple
        dprint(3, "\nConfiguration::add_data_from_xml")
        if key in dict.keys(self):
            buff_val = dict.__getitem__(self, key)
            btype = type(buff_val)
            if btype==Configuration:
                buff_list = [ buff_val ]
                buff_list.append(val)
                dict.__setitem__(self, key, tuple(buff_list))
            elif btype==tuple:
                buff_list = list(buff_val)
                buff_list.append(val)
                dict.__setitem__(self, key, tuple(buff_list))
            else:
                buff_list = [ btype(buff_val) ]
                buff_list.append(val)
                dict.__setitem__(self, key, tuple(buff_list))
        else:
            # if there is no such key, __setitem__ may be used to insert the key,val pair
            dict.__setitem__(self, key, val)

            
    def __setitem__(self, key, val):
        '''Assign value to key in Configuration. Create element, node if appropriate'''
        dprint(3, "\nConfiguration::__setitem__")
        target_nodes = []
        for c in self.__src.childNodes:
            if c.nodeType is c.TEXT_NODE:
                continue
            else:
                if c.tagName == key:
                    target_nodes.append(c)
        for target in target_nodes:
            self.__src.removeChild(target)
        if isinstance(val, Configuration):
            self.__src.appendChild(val.getnode())
            dict.__setitem__(self, key, val)
        elif isinstance(val, tuple) or isinstance(val, list):
            for v in val:
                if isinstance(v, Configuration):
                    self.__src.appendChild(v.getnode())
                else:
                    newn = self.__doc.createElement(key)
                    newt = self.__doc.createTextNode(str(v))
                    newn.appendChild(newt)
                    self.__src.appendChild(newn)
            dict.__setitem__(self, key, tuple(val))
        else:
            newn = self.__doc.createElement(key)
            newt = self.__doc.createTextNode(str(val))
            newn.appendChild(newt)
            self.__src.appendChild(newn)
            dict.__setitem__(self, key, val)

            
    def get_attr(self, key):
        '''Get attribute value associated with key'''
        dprint(3, "\nConfiguration::get_attr")
        attr_dict = dict(self.__attr.items())
        if key in attr_dict.keys():
            return attr_dict[key]
        else:
            return None

        
    def get_attr_keys(self):
        '''Get list of attributes'''
        # returns the list of keys, not the values
        dprint(3, "\nConfiguration::get_attr_keys")
        if self.__attr:
            return self.__attr.items()
        return None

    
    def set_attr(self, key, val):
        '''Set attribute by key,val pair'''
        dprint(3, "\nConfiguration::set_attr")
        self.__src.setAttribute(key, val)

        
    def add_attr(self, attr):
        '''Add attribute to Configuration'''
        dprint(3, "\nConfiguration::add_attr")
        self.__attr = attr
        

    def xml(self):
        '''Get formatted string of XML document'''
        dprint(3, "\nConfiguration::xml")
        return self.__doc.toprettyxml()

    
    def print_config(self, target):
        '''Print xml to target. Target must be a file path or a file pointer'''
        dprint(3, "\nConfiguration::print_config")
        if target:
            if type(target) == str:
                f=open(target, "w")
            else:
                #assuming file pointer
                f = target
        self.__doc.writexml(f, "  ", "  ", "\n")
        f.close()


        
################################  Utility Functions for Configuration objects ################################



def fill_configuration(config, tag, members, attributes=None):
    '''An external constructor for Configuration: Arguments are...
       config => the Configuration object initialized at least with a document
       tag => the tag under which config will be access when presumably it is inserted into a subsuming Configuration
       members => a dictionary of keys,values for whatever data config represents
       attributes => optional, a dictionary of keys,values of config's attributes'''
    dprint(3, "\nextconf.py::fill_configuration")
    doc = config.getdoc()
    config.setnode(doc.createElement(tag))
    for key in members:
        child = None
        if isinstance(members[key], str):
            child = doc.createElement(key)
            datum = doc.createTextNode(members[key])
            child.appendChild(datum)
            config.getnode().appendChild(child) #
        elif isinstance(members[key], list) or isinstance(members[key], tuple):
            for listitem in members[key]:
                if isinstance(listitem, str):
                    child = doc.createElement(key) #
                    datum = doc.createTextNode(listitem)
                    child.appendChild(datum)
                else:
                    # it's a configuration
                    child = doc.createElement(key) #
                    child.appendChild(listitem.getnode())
                    listitem.setparent(child)
                config.getnode().appendChild(child) #
        else:
            listitem = members[key]
            child = doc.createElement(key)
            child.appendChild(listitem.getnode())
            listitem.setparent(child)
            config.getnode().appendChild(child) #
        config[key] = members[key]
    if attributes:
        for key in attributes:
            config.add_attr(doc.createAttribute(key))
            config.set_attr(key, attributes[key])
    return



def attach_configuration(destconf, desttag, srcconf):
    '''Tool for attaching a "filled" Configuration to both a document and to a subsuming Configuration.
       Caution: desttag must match the tag-argument with which srcconf was "filled"'''
    ### Additional notes:
    ### destconf should be the closest Configuration prior to reaching destconf[desttag], e.g.,
    ### To attach srconf into conf["list"]["files"],
    ### destconf should be a Configuration found in conf["list"], and
    ### desttag should be "files".
    ### THIS CANNOT BE USED FOR ADDING THE FIRST ELEMENT TO AN EMPTY DOC
    dprint(3, "\nextconf.py::attach_configuration")
    parent = destconf.getnode()
    if not (desttag in destconf.keys()):
        destconf[desttag] = srcconf
    else:
        if isinstance(destconf[desttag], list) or isinstance(destconf[desttag], tuple):
            destlist = list(destconf[desttag])
            destlist.append(srcconf)
            destconf[desttag] = tuple(destlist)
        else:
            destlist = [ destconf[desttag], srcconf ]
            destconf[desttag] = tuple(destlist)
    srcconf.setparent(parent)
    parent.appendChild(srcconf.getnode())



def remove_configuration(destconf, tag, srcconf):
    '''Tool for removing a Configuration from a document.'''
    ### destconf is the Configuration containing the target, srcconf,
    ### which must be found under destconf[desttag]
    dprint(3, "\nextconf.py::remove_configuration")
    parent = destconf.getnode()
    if isinstance(destconf[tag], list) or isinstance(destconf[tag], tuple):
        destlist = list(destconf[tag])
        for i in range(0,len(destlist)):
            if srcconf == destlist[i]:
                parent.removeChild(srcconf.getnode())
                destlist.pop(i)
                destconf[tag] = tuple(destlist)
                break
    elif isinstance(destconf[tag], Configuration):
        parent.removeChild(srcconf.getnode())
        del destconf[tag]



def attach_top_configuration(doc, tag, srcconf, parenttag, destconf):
    '''Special case tool: Add Configuration to a Configuration tree which exists but is not populated'''
    ### When the topmost dictionary call is a string or empty,
    ### XML might appear as <?xml version="1.0" ?><contents></contents>,
    ### then to add a Configuration inside contents tag is a slightly specialized
    ### case where attach_configuration is not the best choice because
    ### a call like destconf[parenttag] returns a string from which no parent
    ### may be resolved (as would be attempted in attach_configuration).
    ### tag & srcconf refer to the Configurations to be attached,
    ### parenttag & destconf refer to the existing top/empty Configuration for
    ### the XML tree (i.e., the <contents> tag).
    dprint(3, "\nextconf.py::attach_top_configuration")
    topc = Configuration(doc)
    if doc.hasChildNodes():
        parent = doc.childNodes[0]
    else:
        parent = doc.createElement(parenttag)
    fill_configuration(topc,
                       parenttag,
                       members={tag:srcconf},
                       attributes=None)
    topc.setnode = parent
    srcconf.setparent(parent)
    destconf[parenttag] = topc

        

def tree(doc, nd=None, mrk=""):
    '''Diagnostic tool for printing the xml doc'''
    dprint(3, "\nextconf.py::tree")
    if nd is None:
        nd = doc
    for k in nd.childNodes:
        if k.nodeType is k.ELEMENT_NODE:
            print("\n", mrk, k.tagName, end=" > ")
            mrk_buffer = mrk
            for i in range(0, len(k.tagName)+1):
                mrk_buffer += " "
            mrk_buffer += " > "
            tree(doc, k, mrk_buffer)
        if k.nodeType is k.TEXT_NODE:
            buffer_data = k.data.strip(" \n")
            print(" ", buffer_data, end="")
            continue



def _to_string(node, nt):
    '''Diagnostic function: string equivalents of node-types in XML.DOM.MINIDOM'''
    dprint(3, "\nextconf.py::_to_string")
    if nt == node.ELEMENT_NODE:
        return "ELEMENT: " + node.tagName
    if nt == node.TEXT_NODE:
        return "TEXT: " + node.data
    if nt == node.CDATA_SECTION_NODE:
        return "CDATA_SECTION"
    if nt == node.ENTITY_REFERENCE_NODE:
        return "ENTITY_REFERENCE"
    if nt == node.PROCESSING_INSTRUCTION_NODE:
        return "PROCESSING_INSTRUCTION"
    if nt == node.COMMENT_NODE:
        return "COMMENT"
    if nt == node.NOTATION_NODE:
        return "NOTATION"

    

def _delve(doc, node, space):
    '''Diagnostic function: recurse through an XML.DOM.MINIDOM document and print children'''
    dprint(3, "\nextconf.py::_delve")
    if node.hasChildNodes():
        print(space, "Children:")
        for child in node.childNodes:
            print(space, _to_string(child, child.nodeType))
            _delve(doc, child, space+"   ")
    else:
        print(space,"No children")

        
        
def _traverse_conf(doc, nd, parent):
    '''Internal function: map an XML.DOM.MINIDOM document to a Configuration complex'''
    dprint(3, "\nextconf.py::_traverse_conf")
    if len(nd.childNodes)==1:
        # either we have data, or we have a tag-within-a-tag
        if nd.childNodes[0].nodeType == nd.childNodes[0].TEXT_NODE:
            return str(nd.childNodes[0].data)
        else:
            holder = Configuration(doc, nd, parent)
            holder.add_attr(nd.attributes)
            holder.add_data_from_xml(nd.childNodes[0].tagName,
                                     _traverse_conf(doc,
                                                    nd.childNodes[0],
                                                    nd))
            return holder
    else:
        # multiple children, we must skip any text (scrubber.py should have removed any)
        # this is a limitation: this extconf construct can't handle a tag w/ both data + children
        holder = Configuration(doc, nd, parent)
        holder.add_attr(nd.attributes)
        for child in nd.childNodes:
            if child.nodeType is child.TEXT_NODE:
                continue
            # else, it's an element: #
            holder.add_data_from_xml(child.tagName,
                                     _traverse_conf(doc,
                                                    child,
                                                    nd))
        return holder



def _load_doc(name):
    '''Internal function: Open XML file, scrub, parse into XML Document object, and close file. Returns XML doc'''
    dprint(3, "\nextconf.py::_load_doc")
    f = open(name, "r")
    scrubbed = scrubber.ScrubberXML(length=conf.XML_MAX_CHAR,
                                    depth=conf.XML_STACK_DEPTH,
                                    text=f.read())
    doc =  xml.dom.minidom.parseString(scrubbed.get_parsed())
    f.close()
    return doc



def load_file(name):
    '''Load XML into Configuration-complex representation'''
    dprint(3, "\nextconf.py::load_file")
    if name is not None:
        doc = _load_doc(name)
        extconf = _traverse_conf(doc, doc.childNodes[0], doc)
        if isinstance(extconf, str):
            extconf = _traverse_conf(doc, doc, doc)
        return extconf



def load_string(scrub):
    '''Process XML string into Configuratio-complex representation'''
    dprint(3, "\nextconf.py::load_string")
    if scrub is not None:
        doc = xml.dom.minidom.parseString(scrub)
        extconf = _traverse_conf(doc, doc.childNodes[0], doc)
        return extconf
