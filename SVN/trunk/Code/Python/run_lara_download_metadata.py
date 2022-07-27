
import lara_download_metadata 
import lara_utils
import sys

args = sys.argv

if len(args) == 6:
    ( LaraResourcesFile, ReaderDataFile, ReaderID, L2, TmpDir ) = args[1:]
    lara_download_metadata.download_metadata(LaraResourcesFile, ReaderDataFile, ReaderID, L2, TmpDir)
else:
    print(f'Usage: {lara_utils.python_executable()} run_lara_download_metadata ResourcesFile, ReaderFile, ReaderID, L2, TmpDir')

