import xml.dom.minidom
import sys
import scrubber
import config





    
class Configuration(dict):

    def __init__(self,doc,nd=None,parent=None):
        self.__doc = doc
        self.__src = nd
        self.__parent = parent

    def getnode(self):
        return self.__src

    def setnode(self,s):
        self.__src = s

    def getparent(self):
        return self.__parent

    def setparent(self,s):
        self.__parent = s

    def add_data_from_xml(self,key,val):
        if key in dict.keys(self):
            buff_val = dict.__getitem__(self,key)
            btype = type(buff_val)
            if btype==tuple:
                buff_list = list(buff_val)
                buff_list.append(val)
                dict.__setitem__(self,key,tuple(buff_list))
            else:
                buff_list = [ btype(buff_val) ]
                buff_list.append(val)
                dict.__setitem__(self,key,tuple(buff_list))
        else:
            dict.__setitem__(self,key,val)
          
    def __setitem__(self,key,val):
        target_nodes = []
        for c in self.__src.childNodes:
            if c.nodeType is c.TEXT_NODE:
                continue
            else:
                if c.tagName == key:
                    target_nodes.append(c)
        for target in target_nodes:
            self.__src.removeChild(target)
        if (type(val) is tuple) or (type(val) is list):
            for v in val:
                newn = self.__doc.createElement(key)
                newt = self.__doc.createTextNode(str(v))
                newn.appendChild(newt)
                self.__src.appendChild(newn)
            dict.__setitem__(self,key,tuple(val))
        else:
            newn = self.__doc.createElement(key)
            newt = self.__doc.createTextNode(str(val))
            newn.appendChild(newt)
            self.__src.appendChild(newn)
            dict.__setitem__(self,key,val)

    def xml(self):
        return self.__doc.toprettyxml()

    def print_config(self,target):
        if target:
            if type(target) == str:
                f=open(target,"w")
            else:
                #assuming file pointer
                f = target
        self.__doc.writexml(f,"  ","  ","\n")
        f.close()


        

def tree(doc,nd=None,mrk=""):
    if nd is None:
        nd = doc
    #print("(",len(nd.childNodes),")")
    for k in nd.childNodes:
        if k.nodeType is k.ELEMENT_NODE:
            print("\n",mrk,k.tagName,end=" > ")
            mrk_buffer = mrk
            for i in range(0,len(k.tagName)+1):
                mrk_buffer += " "
            mrk_buffer += " > "
            tree(doc,k,mrk_buffer)
        if k.nodeType is k.TEXT_NODE:
            buffer_data = k.data.strip(" \n")
            print(" ",buffer_data,end="")
            continue

        
        
def _traverse_dict(nd,parent):
    if len(nd.childNodes)==1:
        return str(nd.childNodes[0].data)
    else:
        holder = {}
        for k in nd.childNodes:
            if k.nodeType is k.TEXT_NODE:
                continue
            # else, it's an element: #
            if k.tagName in holder.keys():
                if type(holder[k.tagName])==list:
                    holder[k.tagName].append(_traverse_dict(k,parent))
                else:
                    htype = type(holder[k.tagName])
                    buff = htype(holder[k.tagName])
                    holder[k.tagName] = [ buff ]
                    holder[k.tagName].append(_traverse_dict(k,parent))
            else:
                holder[k.tagName] = _traverse_dict(k,parent)
        return holder

    

def _traverse_conf(doc,nd,parent):
    if len(nd.childNodes)==1:
        # either we have data, or we have a tag-within-a-tag
        if nd.childNodes[0].nodeType == nd.childNodes[0].TEXT_NODE:
            return str(nd.childNodes[0].data)
        else:
            holder = Configuration(doc,nd,parent)
            holder.add_data_from_xml(nd.childNodes[0].tagName,_traverse_conf(doc,nd.childNodes[0],nd))
            return holder
    else:
        # multiple children, we must skip any text (scrubber.py should have removed any)
        # this is a limitation: this extconf construct can't handle a tag w/ both data + children
        holder = Configuration(doc,nd,parent)
        for child in nd.childNodes:
            if child.nodeType is child.TEXT_NODE:
                continue
            # else, it's an element: #
            holder.add_data_from_xml(child.tagName,_traverse_conf(doc,child,nd))
        return holder

    
    
def _load_doc(name):
    f = open(name,"r")
    scrubbed = scrubber.ScrubberXML(length=config.XML_MAX_CHAR,depth=config.XML_STACK_DEPTH,text=f.read())
    #doc =  xml.dom.minidom.parse(f)
    doc =  xml.dom.minidom.parseString(scrubbed.get_parsed())
    f.close()
    return doc



def load_file(name):
    if name is not None:
        doc = _load_doc(name)
        extconf = _traverse_conf(doc,doc.childNodes[0],doc)
        return extconf


    
def load_string(scrub):
    if scrub is not None:
        doc = xml.dom.minidom.parseString(scrub)
        extconf = _traverse_conf(doc,doc.childNodes[0],doc)
        return extconf



    




######    unused    ###############################################################################

def _parse_branch(ec,nd):
    for c in nd.childNodes:
        if c.tagName == "configuration":
            _parse_branch(ec,c)
        if c.tagName == "display":
            _parse_display(ec,c)
        if c.tagName == "parse":
            for k in c.getElementsByTagName("*"):
                ec[k.tagName] = _get_text(c.getElementsByTagName(k.tagName)[0].childNodes)


def _parse_display(ec,nd):
    for el in nd.childNodes:
        if el.tagName == "size":
            for att in el.attributes.items():
                ec[att] = el.getAttribute(att).value


def _get_text(self,ndlist):
    buffer_array = []
    for nd in ndlist:
        if nd.nodeType == nd.TEXT_NODE:
            buffer_array.append(nd.data)
    return ''.join(buffer_array)
