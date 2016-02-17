import fileinput
import sys
import re
import os
import HTSeq


def replaceAll(file, searchExp, replaceExp):
    """
    Replace an expression in a file
    """
    for line in fileinput.input(file, inplace=1):
        if searchExp in line:
            line = line.replace(searchExp, replaceExp)
        sys.stdout.write(line)


##patch HTseq library to increse buffer size
def path_htseq():
    """
    Patch the htseq library increaseing the buffer size
    """
    initfile = os.path.splitext(HTSeq.__file__)[0] + '.py'
    print "Set patch for %s" %initfile
    replaceAll(initfile, 'max_buffer_size=3000000', 'max_buffer_size=9000000')


if __name__ == "__main__":
    path_htseq()

