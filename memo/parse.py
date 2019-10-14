from memo.config import TAG_MARKER

def parse(t):
    if t is None:
        return []
    if t is "":
        return []
    tags = []
    working_strings = t.splitlines()
    try:
        while working_strings.index(''):
            working_strings.remove('')
    except:
        pass
    for line in working_strings:
        while (True):
            index = line.find(TAG_MARKER)
            if index < 0 :
                break
            line = line[index+len(TAG_MARKER):]
            temp_str = line.split(' ').pop(0)
            tags.append( temp_str.rstrip("\t") )
            line = line[len(temp_str):]
    return tags

def split_by_unknown(t):
    if t is None:
        return []
    if t is "":
        return []
    tags = []
    maxpair = ("",0)
    results = []
    splitters = (" ", ",", ";", TAG_MARKER, "|", ) # not all non-alphanumeric characters are here b/c tags should be mostly unrestricted in form.
    for s in splitters:
        tmp_list = t.split(s)
        results.append( (s,len(tmp_list)) )
    for pair in results:
        if pair[1] > maxpair[1]:
            maxpair = pair
    working_list = []
    if maxpair[1] == 0:
        # no split found
        return t
    working_list = t.split(maxpair[0])
    try:
        while working_list.index('') > -1:
            working_list.remove('')
    except:
        pass
    finally:
        tags = []
        for item in working_list:
            for s in splitters:
                item = item.strip(s)
            tags.append(item)
        return tags
