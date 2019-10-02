from config import TAG_MARKER

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
