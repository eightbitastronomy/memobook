######## configuration values ########

TAG_MARKER="@@"
XML_STACK_DEPTH=4
XML_MAX_CHAR=512
TAB_SIZE=8



######## debugging/tracing ########

DEBUG_PRINT=True     # activate printing of debug information
VERBOSITY=3          # 0: no printing;
                     # 1: Exception-error printing
                     # 2: Additional error and other priority printing
                     # 3: Flow-tracing printing

if DEBUG_PRINT:
    import sys

    
def dprint(level,errorstring):
    if DEBUG_PRINT:
        if VERBOSITY >= level:
            sys.stderr.write(errorstring)
            sys.stderr.flush()
    return
