import os

if 'LARA' in os.environ:
    print('--- Found environment variable LARA')
else:
    print('--- Unable to find environment variable LARA')
