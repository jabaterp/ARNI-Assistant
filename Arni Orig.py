from gtts import gTTS
import os
import playsound
import speech_recognition as sr
import random
import google.cloud
from google.cloud import speech_v1
import pyglet
import pyaudio

allCommands = {}
allActions = {}
commandFile = open("MyCommands.txt", "r+")
gettoFile = open("GhettoCommands.txt", "r+")
language = "en-US"
speakFile = 'temp'
fileNum = 0
fileToUse = "MyCommands.txt"


def readFile():
    for line in commandFile.readlines():
        allCommandsSplit = line.split("||")
        for command in allCommandsSplit:
            cmdAndAct = command.strip().lower().split(":")
            if ",," in cmdAndAct[0]:
                cmds = cmdAndAct[0].split(",,")
                for cmd in cmds:
                    cmd = cmd.strip().lower()
                    if ",," in cmdAndAct[1]:
                        acts = cmdAndAct[1].strip().lower().split(",,")
                        allCommands[cmd] = acts
                        for act in acts:
                            if act in allActions and cmd not in allActions[act]:
                                allActions[act].append(cmd)
                            elif act not in allActions:
                                allActions[act] = [cmd]
                    else:
                        allCommands[cmd] = [cmdAndAct[1].strip().lower()]
                        if cmdAndAct[1].strip().lower() in allActions and cmd not in allActions[cmdAndAct[1].strip().lower()]:
                            allActions[cmdAndAct[1].strip().lower()].append(cmd)
                        elif cmdAndAct[1].strip().lower() not in allActions:
                            allActions[cmdAndAct[1].strip().lower()] = [cmd]

            else:
                cmd = cmdAndAct[0].strip().lower()
                if ",," in cmdAndAct[1]:
                    for act in cmdAndAct[1].strip().lower().split(",,"):
                        allCommands[cmd] = act
                        if act in allActions and cmd not in allActions[act]:
                            allActions[act].append(cmd)
                        elif cmdAndAct[1].strip().lower() not in allActions:
                            allActions[act] = [cmd]
                else:
                    allCommands[cmd] = [cmdAndAct[1].strip().lower()]
                    if cmdAndAct[1].strip().lower() in allActions and cmd not in allActions[
                        cmdAndAct[1].strip().lower()]:
                        allActions[cmdAndAct[1].strip().lower()].append(cmd)
                    elif cmdAndAct[1].strip().lower() not in allActions:
                        allActions[cmdAndAct[1].strip().lower()] = [cmd]


def readFileOld():
    for line in commandFile.readlines():
        allCommandsSplit = line.split("||")
        for command in allCommandsSplit:
            cmdAndAct = command.split(":")
            acts = [cmdAndAct[1].strip().lower()]
            if ",," in cmdAndAct[1]:
                acts = cmdAndAct[1].strip().lower().split(",,")
            if ",," in cmdAndAct[0]:
                cmds = cmdAndAct[0].strip().lower().split(",,")
                for cmd in cmds:
                    allCommands[cmd.strip().lower()] = acts
                    if cmd in allActions and cmd not in allActions[cmdAndAct[1].strip().lower()]:
                        allActions[cmdAndAct[1].strip().lower()].append(cmd)
                    else:
                        allActions[cmdAndAct[1].strip().lower()] = [cmd]
            else:
                allCommands[cmdAndAct[0].strip().lower()] = acts
                allActions[cmdAndAct[1].strip().lower()] = [cmdAndAct[0].strip().lower()]


def thugListen():
    allModes = ["Act", "learn", "Read", "Erase", "stop"]

    mode = speak("What's up mutha, whatchu need.")
    while mode not in allModes:
        mode = speak("That aint no mode main, choose a real mode pimp.")
    mode = mode.lower()
    retVal = ""
    print(speak("Aiight, ima be in " + mode + " mode.", False))
    while mode != "stop" and mode != "exit":
        if mode == "act":
            retVal = act()
        elif mode == "learn":
            retVal = learn()
        elif mode == "read":
            for cmd in allCommands:
                print(cmd + " : " + allCommands[cmd])
        elif mode == "erase":
            erase()
        if retVal == "exit":
            break
        mode = speak("What's up main whatchu need.")
        mode = mode.lower()
        while mode not in allModes:
            mode = speak("That aint no mode bitch, choose a real mode pimp.")
            mode = mode.lower()

    speak("Aiight Im finna hit up this j and down some henny. If you need me, too bad. Peace monig", False)
    commandFile.close()
    writeFile()


def listen():
    allModes=["Act", "learn", "Read", "Erase", "stop"]

    mode = speak("Which mode shall I enter? Act, Learn, Read or Erase?")
    if mode.strip().lower() == "ghetto mode" or mode.strip().lower() == "thug mode":
        return thugListen()
    while mode not in allModes:
        mode = speak("That is not a mode. Please enter either Act, Learn, Read or Erase.")
    mode = mode.lower()
    retVal=""
    print(speak("Entering "+mode+" mode.", False))
    while mode != "stop" and mode != "exit":
        if mode == "act":
            retVal = act()
        elif mode == "learn":
            retVal = learn()
        elif mode == "read":
            for cmd in allCommands:
                print(cmd+" : "+allCommands[cmd])
        elif mode == "erase":
            erase()
        if retVal == "exit":
            break
        mode = speak("Which mode shall I enter? Act, Learn, Read or Erase)")
        mode = mode.lower()
        while mode not in allModes:
            mode = speak("That is not a mode. Please enter either Act, Learn, Read or Erase.")
            mode = mode.lower()

    speak("Alright, I guess I will log off for now. Bye-bye!", False)
    commandFile.close()
    writeFile()


def act():
    while True:
        command = speak("Please enter a command")
        command = command.lower().strip()
        if command == "stop":
            return
        if command == "exit":
            return "exit"
        if command not in allCommands:
            teachBool = speak("That command does not yet exist. Would you like to teach me?")
            if teachBool.lower() == "yes" or teachBool.lower() == "yeah":
                learn(command)
        else:
            chooseAction = random.randint(0, len(allCommands[command])-1)
            speak(allCommands[command][chooseAction], False)


def learn(command="none"):
    initialized = command != "none"
    begin = True
    while not initialized or begin:
        begin = False
        if not initialized:
            command = speak("Please enter the command precisely:")
            command = command.lower().strip()
        if command == "stop":
            return
        if command =="exit":
            return "exit"
        action = speak("Please tell me how to respond to this command, or say wrong Command to change.")
        if(action.strip().lower() == "wrong command"):
            return learn()
        action = action.strip().lower()
        equalsString = command.lower()+" equals "
        if equalsString in action:
            cmd2 = action.split(equalsString)[1].strip()
            print(cmd2)
            while cmd2 not in allCommands and cmd2 != "cancel":
                cmd2 = speak(cmd2 +" is not a valid command. Please try again, or say cancel.")
            if cmd2.lower().strip() == "cancel":
                continue
            allCommands[command] = allCommands[cmd2]
            for action in allCommands[cmd2]:
                allActions[action].append(command)
        else:
            if command in allCommands and action not in allCommands[command]:
                allCommands[command].append(action)
            elif command not in allCommands:
                allCommands[command] = [action]
            if action in allActions:
                if command not in allActions[action]:
                    allActions[action].append(command)
            else:
                allActions[action] = [command]


def erase():
    while True:
        command = speak("Please enter the command to erase")
        if command == "stop":
            return
        while command not in allCommands:
            command = speak("That is not a valid command. Please enter a command or enter cancel")
            if command == "cancel":
                return
        allCommands.pop(command)


def speak(line, response=True):

    audio = gTTS(text=line, lang=language)
    global fileNum
    file = speakFile+fileNum.__str__()+".mp3"
    audio.save(file)

    playsound.playsound(file)

    os.remove(file)
    fileNum += 1
    if response:

        with sr.Microphone() as source:
            audio_text = recog.listen(source)
            try:
                respConv = recog.recognize_google(audio_text)
                print("Text: " + respConv)
            except:
                return speak("Sorry, I didn't get that, can you say it again?")
        return respConv


def writeFile():
    allStringCommands = ""
    first = True
    completedCommands =[]
    for action in allActions:
        if(allActions[action] not in completedCommands):
            cmdAction = ""
            if not first:
                cmdAction += " || "
            first = False
            fstList = True
            if len(allActions[action]) > 1:
                for command in allActions[action]:
                    if not fstList:
                        cmdAction += ",,"+command
                    else:
                        fstList = False
                        cmdAction += command
            else:
                cmdAction += allActions[action][0]
            fstList = True
            cmdAction += " : "
            if len(allCommands[allActions[action][0]]) > 1:
                for action2 in allCommands[allActions[action][0]]:
                    if not fstList:
                        cmdAction+=",,"+action2
                    else:
                        fstList = False
                        cmdAction+=action2
            else:
                cmdAction+= action
            allStringCommands += cmdAction
            completedCommands.append(allActions[action])
    newFile = open(fileToUse, "w")
    newFile.write(allStringCommands)
    newFile.close()


def intro():
    name = speak("Hello! My name is Arni! It stands for Automated Robotic Neural Interface. What's your name?")
    rightName = speak("I got your name as " + name + ", is that right?")
    while rightName.lower() != "yes" and rightName.lower()!="yeah":
        name = speak("Okay, please tell me your name again.")
        rightName = speak("I got your name as " + name + ", is that right?")
    user = Arni(name)
    speak("Hello there "+name+", I am excited to help you!", False)


class Arni:
    locX = 0
    locY = 0
    name = ""

    def __init__(self, newname):
        name = newname


recog = sr.Recognizer()
user = None
#intro()
readFile()
listen()
