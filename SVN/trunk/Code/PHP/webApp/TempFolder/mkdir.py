import os
import sys

a = "This is line"
os.makedirs("TempFolder")
f= open("TempFolder/TempFile.txt","w+")
for i in range(10):
     f.write(sys.argv[1] + str(i+1) + "\r")
f.close() 
