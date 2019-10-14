import xml.dom.minidom
import sys
import scrubber
import config





    
class Configuration(dict):

    def __init__(self,doc,nd=None,parent=None):
        self.__doc = doc
        self.__src = nd
        self.__parent = parent
        self.__attr = None

    def getdoc(self):
        return self.__doc
    
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
            if btype==Configuration:
                buff_list = [ buff_val ]
                buff_list.append(val)
                dict.__setitem__(self,key,tuple(buff_list))
            elif btype==tuple:
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
        if isinstance(val,Configuration):
            self.__src.appendChild(val.getnode())
            dict.__setitem__(self,key,val)
        elif isinstance(val,tuple) or isinstance(val,list):
            for v in val:
                if isinstance(v,Configuration):
                    self.__src.appendChild(v.getnode())
                else:
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

    def get_attr(self,key):
        attr_dict = dict(self.__attr.items())
        if key in attr_dict.keys():
            return attr_dict[key]
        else:
            return None

    def get_attr_keys(self):
        if self.__attr:
            return self.__attr.items()
        return None
    
    def set_attr(self,key,val):
        self.__src.setAttribute(key,val)

    def add_attr(self,attr):
        self.__attr = attr

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



def fill_configuration(config,tag,members,attributes=None):
    '''An external constructor for Configuration: Arguments are...
       config => the Configuration object initialized at least with a document
       tag => the tag under which config will be access when presumably it is inserted into a subsuming Configuration
       members => a dictionary of keys,values for whatever data config represents
       attributes => optional, a dictionary of keys,values of config's attributes'''
    doc = config.getdoc()
    config.setnode(doc.createElement(tag))
    for key in members:
        child = None
        if isinstance(members[key],str):
            child = doc.createElement(key)
            datum = doc.createTextNode(members[key])
            child.appendChild(datum)
            config.getnode().appendChild(child) #
        elif isinstance(members[key],list) or isinstance(members[key],tuple):
            for listitem in members[key]:
                if isinstance(listitem,str):
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
            config.set_attr(key,attributes[key])
    return



def attach_configuration(destconf,desttag,srcconf):
    '''Tool for attaching a "filled" Configuration to both a document and to a subsuming Configuration.
       Caution: desttag must match the tag-argument with which srcconf was "filled"'''
    ### Additional notes:
    ### destconf should be the closest Configuration prior to reaching destconf[desttag], e.g.,
    ### To attach srconf into conf["list"]["files"],
    ### destconf should be a Configuration found in conf["list"], and
    ### desttag should be "files".
    ### THIS CANNOT BE USED FOR ADDING THE FIRST ELEMENT TO AN EMPTY DOC
    parent = destconf.getnode()
    if not (desttag in destconf.keys()):
        destconf[desttag] = srcconf
    else:
        if isinstance(destconf[desttag],list) or isinstance(destconf[desttag],tuple):
            destlist = list(destconf[desttag])
            destlist.append(srcconf)
            destconf[desttag] = tuple(destlist)
        else:
            destlist = [ destconf[desttag], srcconf ]
            destconf[desttag] = tuple(destlist)
    srcconf.setparent(parent)
    parent.appendChild(srcconf.getnode())



def remove_configuration(destconf,tag,srcconf):
    '''Tool for removing a Configuration from a document.'''
    ### destconf is the Configuration containing the target, srcconf,
    ### which must be found under destconf[desttag]
    parent = destconf.getnode()
    if isinstance(destconf[tag],list) or isinstance(destconf[tag],tuple):
        destlist = list(destconf[tag])
        for i in range(0,len(destlist)):
            if srcconf == destlist[i]:
                parent.removeChild(srcconf.getnode())
                destlist.pop(i)
                destconf[tag]=tuple(destlist)
                break
    elif isinstance(destconf[tag],Configuration):
        parent.removeChild(srcconf.getnode())
        del destconf[tag]



def attach_top_configuration(doc,tag,srcconf,parenttag,destconf):
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
    topc = Configuration(doc)
    if doc.hasChildNodes():
        parent = doc.childNodes[0]
    else:
        parent = doc.createElement(parenttag)
    fill_configuration(topc,parenttag,members={tag:srcconf},attributes=None)
    topc.setnode = parent
    srcconf.setparent(parent)
    destconf[parenttag] = topc

        

def tree(doc,nd=None,mrk=""):
    '''Diagnostic tool for printing the xml doc'''
    if nd is None:
        nd = doc
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


        
def _to_string(node,nt):
    '''Diagnostic function: string equivalents of node-types in XML.DOM.MINIDOM'''
    if nt==node.ELEMENT_NODE:
        return "ELEMENT: " + node.tagName
    if nt==node.TEXT_NODE:
        return "TEXT: " + node.data
    if nt==node.CDATA_SECTION_NODE:
        return "CDATA_SECTION"
    if nt==node.ENTITY_REFERENCE_NODE:
        return "ENTITY_REFERENCE"
    if nt==node.PROCESSING_INSTRUCTION_NODE:
        return "PROCESSING_INSTRUCTION"
    if nt==node.COMMENT_NODE:
        return "COMMENT"
    if nt==node.NOTATION_NODE:
        return "NOTATION"

    

def _delve(doc,node,space):
    '''Diagnostic function: recurse through an XML.DOM.MINIDOM document and print children'''
    if node.hasChildNodes():
        print(space,"Children:")
        for child in node.childNodes:
            print(space,_to_string(child,child.nodeType))
            _delve(doc,child,space+"   ")
    else:
        print(space,"No children")

        
        
def _traverse_dict(nd,parent):
    '''Traverse dictionary test function. No longer is updated; use _traverse_conf'''
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
    '''Function to map an XML.DOM.MINIDOM document to a Configuration complex'''
    if len(nd.childNodes)==1:
        # either we have data, or we have a tag-within-a-tag
        if nd.childNodes[0].nodeType == nd.childNodes[0].TEXT_NODE:
            return str(nd.childNodes[0].data)
        else:
            holder = Configuration(doc,nd,parent)
            holder.add_attr(nd.attributes)
            holder.add_data_from_xml(nd.childNodes[0].tagName,_traverse_conf(doc,nd.childNodes[0],nd))
            return holder
    else:
        # multiple children, we must skip any text (scrubber.py should have removed any)
        # this is a limitation: this extconf construct can't handle a tag w/ both data + children
        holder = Configuration(doc,nd,parent)
        holder.add_attr(nd.attributes)
        for child in nd.childNodes:
            if child.nodeType is child.TEXT_NODE:
                continue
            # else, it's an element: #
            holder.add_data_from_xml(child.tagName,_traverse_conf(doc,child,nd))
        return holder

    
    
def _load_doc(name):
    f = open(name,"r")
    scrubbed = scrubber.ScrubberXML(length=config.XML_MAX_CHAR,depth=config.XML_STACK_DEPTH,text=f.read())
    doc =  xml.dom.minidom.parseString(scrubbed.get_parsed())
    f.close()
    return doc



def load_file(name):
    if name is not None:
        doc = _load_doc(name)
        extconf = _traverse_conf(doc,doc.childNodes[0],doc)
        if isinstance(extconf,str):
            extconf = _traverse_conf(doc,doc,doc)
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
