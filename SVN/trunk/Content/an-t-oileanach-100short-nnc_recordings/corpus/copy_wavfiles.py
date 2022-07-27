import sys, os, json


namelines = sys.stdin.readlines()
jsonfile = sys.argv[1]

with open(jsonfile) as fh:
    meta = json.load(fh)

#print(len(meta))
#print(len(namelines))
assert len(meta) == len(namelines)

i = 0
while i < len(namelines):
    nameline = namelines[i]
    info = meta[i]

    #print(nameline)
    #print(info)

    
    (name,text) = nameline.split("\t")

    info["file"] = f"{name}.mp3"
    i += 1

print(json.dumps(meta, indent=4))
