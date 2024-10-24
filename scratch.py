keysFile = open("RawQuestions.txt", "r+")
allLines = ""

for line in keysFile.readlines():
    if "?" in line:
        curr = line.split(".")[1].strip();
        allLines += curr+"\n"
newFile = open("extraQuestions.txt", "w")
newFile.write(allLines)
newFile.close()