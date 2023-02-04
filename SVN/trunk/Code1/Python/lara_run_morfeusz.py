
import sys
import os.path
import os
import json

# -------------------------------------------

def run_morfeusz_on_files(InFile, OutFile):
    InText = read_lara_text_file(InFile)
    if InText == False:
        print('*** Error: unable to read file: ' + InFile)
        return False
    dag = run_morfeusz_on_text(InText)
    if dag == False:
        return False
    else:
        #OutText = str(dag)
        #write_lara_text_file(OutText, OutFile)
        write_json_to_file(dag, OutFile)

def run_morfeusz_on_text(Str):
    try:
        from morfeusz2 import Morfeusz
        morfeusz = Morfeusz(expand_tags=True)
        return morfeusz.analyse(Str)
    except Exception as e:
        lara_utils.print('*** Error: something went wrong when trying to run Morpheusz')
        lara_utils.print(str(e))
        return False

# Utilities. We can't use lara_utils.py, since this needs to run under earlier versions of Python

## return the name of the current python executable 
def python_executable():
    import sys
    return os.path.splitext(os.path.basename(sys.executable))[0]

encodings_to_try = ['utf-8-sig', 'utf-8', 'iso-8859-1', 'utf-16le', 'utf-16be']

# Read a LARA text file and return a string.
# Then try to read it as a utf-8 encoded file
def read_lara_text_file(pathname):
    global encodings_to_try
    if not file_exists(pathname):
        print('*** Error: unable to find ' + pathname)
        return False
    else:
        abspathname = absolute_file_name(pathname)
        return read_lara_text_file1(abspathname, encodings_to_try)

def file_exists(pathname):
    return os.path.isfile(absolute_file_name(pathname))

def absolute_file_name(pathname):
    return os.path.abspath(os.path.expandvars(pathname)).replace('\\', '/')

def read_lara_text_file1(abspathname, encodings):
    if len(encodings) == 0:
        print('*** Error: no more encodings to try, giving up.')
        return False
    else:
        ( this_encoding, remaining_encodings ) = ( encodings[0], encodings[1:] )
        try:
            with open(abspathname, encoding=this_encoding) as f:
                lines = [ line for line in f ]
            print('--- Read LARA text file as ' + this_encoding + ': ' + abspathname)
            return "".join(lines)
        except Exception as e:
            print('*** Warning: unable to read text file ' + abspathname + ' as ' + this_encoding)
            print(str(e))
            return read_lara_text_file1(abspathname, remaining_encodings)

def write_lara_text_file(string, pathname):
    try:
        abspathname = absolute_file_name(pathname)
        with open(abspathname, 'w', encoding='utf-8') as f:
            f.write(string)
        print('--- Written LARA text file ' + abspathname)
        return True
    except Exception as e:
        print('*** Error: when trying to write LARA text file ' + pathname)
        print(str(e))
        return False

def write_json_to_file(data, pathname):
    abspathname = absolute_file_name(pathname)
    try:
        with open(abspathname, 'w', encoding='utf-8') as f:
            json.dump(data, f, indent=4, sort_keys=True) # prettyprint json output, and sort any keys
        print('--- Written JSON file ' + pathname)
        return True
    except Exception as e:
        print('*** Error: unable to write JSON to file ' + pathname)
        print(str(e))
        return False

# -------------------------------------------

args = sys.argv

if len(args) == 3:
    ( infile, outfile ) = args[1:]
    run_morfeusz_on_files(infile, outfile)
else:
    print('Usage: ' + python_executable()  + '$LARA/Code/Python/lara_run_morfeusz <infile> <outfile>')

