
import lara_tagging as l
import lara_utils
import sys

args = sys.argv

if len(args) == 3:
    ( infile, outfile ) = args[1:]
    l.tag_file(infile, outfile)
else:
    print(f'Usage: {lara_utils.python_executable} $LARA/Code/Python/run_lara_tagging infile outfile')

