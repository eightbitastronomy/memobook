import xml.dom.minidom
import sys



MARKER="@@"


          
class ExternalConfiguration2(dict):

    _doc = None
    _src = None

    def __init__(self,xname=None):
        if xname is not None:
            self.__load_doc(xname)
            self.__load_config_from_doc()

    def __setitem__(self,key,value):
        if key in self.keys():
            target_node = self.find_node(key)
            if target_node:
                np = target_node.parentNode
                newn = self._doc.createElement(key)
                newt = self._doc.createTextNode(str(value))
                newn.appendChild(newt)
                np.replaceChild(newn,target_node)
                dict.__setitem__(self,key,value)
        else:
            dict.__setitem__(self,key,value)    
        
    def __load_doc(self,name):
        self._src = name
        f = open(name,"r")
        self._doc =  xml.dom.minidom.parse(f)
        f.close()
        
    def __load_config_from_doc(self):
        for k in self._doc.getElementsByTagName("*"):
            if k.parentNode.nodeType is not k.DOCUMENT_NODE:
                self[k.tagName] = self.__get_text(self._doc.getElementsByTagName(k.tagName)[0].childNodes)

    def load_config(self,fn):
        if fn is None:
            raise Exception('''Configuration error: "None" cannot be opened for parsing''')
        else:
            self.__load_doc(fn)
            self.__load_config_from_doc()

    def reload(self):
        self.__load_config_from_doc()
            
    def clear(self):
        for k in self.keys():
            del k
                   
    def __get_text(self,ndlist):
        buffer_array = []
        for nd in ndlist:
            if nd.nodeType == nd.TEXT_NODE:
                buffer_array.append(nd.data)
        return ''.join(buffer_array)

    def print_config(self,target=None):
        #for k in self.keys():
        #    print(str(k) + ": " + self[k])
        if target:
            if type(target) == str:
                f=open(target,"w")
            else:
                #assuming file pointer
                f = target
        else:
            f = open(self._src,"w")
        self._doc.writexml(f)
        f.close()

    def tree(self,nd=None,mrk=""):
        if nd is None:
            nd = self._doc
        for k in nd.childNodes:
            if k.nodeType is k.ELEMENT_NODE:
                print("\n",mrk,k.tagName,end=" > ")
                mrk_buffer = mrk
                for i in range(0,len(k.tagName)+1):
                    mrk_buffer += " "
                mrk_buffer += " > "
                self.tree(k,mrk_buffer)
            if k.nodeType is k.TEXT_NODE:
                buffer_data = k.data.strip(" \n")
                print(" ",buffer_data,end="")
                continue
        
    def __str__(self):
        if self._doc:
            return self._doc.toprettyxml()
        else:
            return ""

    def find_node(self,name,tree=None):   # assumes the uniqueness of a node
        if not tree:
            tree = self._doc.childNodes
        ret_node = None
        for c in tree:
            if c.nodeType is c.TEXT_NODE:
                continue
            else:
                if c.tagName == name:
                    return c
            ret_node =  self.find_node(name,c.childNodes)
        return ret_node

    ### broken until this is altered for the new find_node which doesn't return a list ###
    #def set_value(self,name,data):
    #    target_node = self.find_node(name)
    #    for n in target_node:
    #        np = n.parentNode
    #        newn = self._doc.createElement(name)
    #        newt = self._doc.createTextNode(str(data))
    #        newn.appendChild(newt)
    #        np.replaceChild(newn,n)
    #        break
    #    self.reload()


    
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
        else:
            newn = self.__doc.createElement(key)
            newt = self.__doc.createTextNode(str(val))
            newn.appendChild(newt)
            self.__src.appendChild(newn)
        dict.__setitem__(self,key,tuple(val))

    def xml(self):
        return self.__doc.toprettyxml()

    def print_config(self,target):
        if target:
            if type(target) == str:
                f=open(target,"w")
            else:
                #assuming file pointer
                f = target
        self.__doc.writexml(f,"","","")
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
        return str(nd.childNodes[0].data)
    else:
        holder = Configuration(doc,nd,parent)
        for child in nd.childNodes:
            if child.nodeType is child.TEXT_NODE:
                continue
            # else, it's an element: #
            holder.add_data_from_xml(child.tagName,_traverse_conf(doc,child,nd))
        return holder

    
def _load_doc(name):
    f = open(name,"r")
    doc =  xml.dom.minidom.parse(f)
    f.close()
    return doc


def load(name):
    if name is not None:
        extconf = _load_doc(name)
        extconf = _traverse_conf(extconf,extconf.childNodes[0],extconf)
        return extconf
        




    
#######     testing     #################################################################3





#control = ExternalConfiguration2()
#control.load_config("conf.xml")
#tree(control._doc,None,"")
#ctrl=Configuration(control._doc,control._doc,None)
#ctrl = traverse2(control._doc,control._doc.childNodes[0],control._doc)

#ctrl = load("conf.xml")
#print("------------")
#for k,v in ctrl.items():
#    print(k," ",v)

#print("------------")
#print(ctrl.xml())
#ctrl["db"]["src"]="notes.db"
#print(ctrl["db"]["src"])
#print("------------")
#print(ctrl["db"].xml())
#ctrl["db"]["scan"].append("/home/")
#ctrl["db"].add_to_list("src","memotest1.db")
#ctrl["db"]["scan"].append("/home/")

#l = list(ctrl["db"]["scan"])
#l.append("/home/")
#ctrl["db"]["scan"]=l
#print(ctrl["db"]["scan"])
#print(ctrl.xml())
##ctrl.print_config("conf2.xml")

#print(control)
#for k,v in control.items():
#    print(k,": ",v)
#print("y was: " + control["y"])
#control["y"] = "250"
#print("y is: " + control["y"])
#fn = control.find_node("x")
#if fn:
#    print("Found x: " + str(fn))
#    n=fn
##for n in fn:
#    np = n.parentNode
#    newn = control._doc.createElement("x")
#    newt = control._doc.createTextNode("430")
#    newn.appendChild(newt)
#    np.replaceChild(newn,n)
#control.reload()
#control.print_config("conf2.xml")
#sys.exit(0)





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
