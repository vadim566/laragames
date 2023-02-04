# This file is intended to be run under Python 2.7, because hazm requires that.
# Consequently, we don't use the usual LARA infrastructure

import lara_farsi_tagging
import sys

try:
    
    full_args = sys.argv

    if len(full_args) == 3:
        ( FromFile, ToFile ) = ( full_args[1], full_args[2] ) 
        lara_farsi_tagging.tag_file(FromFile, ToFile)
    else:
        print('Usage: python2.7 $LARA/Code/Python <PlainFile> <TaggedFile>')
              
except Exception as e:
    print('*** Error: An internal exception occurred and the program was aborted!')
    print('*** Error: Exception message: ' + str(e))
