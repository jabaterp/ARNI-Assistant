import sys
from gtts import gTTS
import os
import playsound
import speech_recognition as sr
import random
import bluetooth
import time
import re
import pychromecast
import random
from pychromecast.controllers.youtube import YouTubeController

#Bluetooth services
from selenium import webdriver
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.common.by import By
from webdriver_manager.chrome import ChromeDriverManager
from selenium.webdriver.chrome.options import Options
chrome_options = Options()
import chromedriver_autoinstaller

arniMACAddress = '00:0C:BF:13:7E:77'
homeSpeakerMACAddress = '00:12:6f:ac:55:e1'
connectedToSpeaker = False
port = 1
s = bluetooth.BluetoothSocket(bluetooth.RFCOMM)


#Variables in use
Direction = {
    "FORWARD": "F",
    "BACK": "B",
    "LEFT": 'L',
    "RIGHT": 'R',
    "BACKLEFT": 'X',
    "BACKRIGHT": 'Y',
    "FORWARDLEFT": 'FL',
    "FORWARDRIGHT": 'FR',
    "STOP": 'E'
}

#File Info
keys = []
dirSyns = {}
allCommands = {}
allActions = {}
questions = []
personas = {}
moves = {}
global orders

#Files
commandFile = open("MyCommands.txt", "r+")
dirFile = open("Directions.txt", "r+")
ghettoFile = open("GhettoCommands.txt", "r+")
foodFile = open("Food.txt", "r+")
topsMatchFile = open("TopsMatch.txt", "r+")
keysFile = open("Keys.txt", "r+")
questionsFile = open("Questions.txt", "r+", encoding="utf8")
personaFile = open("personas.txt", "r+")
movesFile = open("moves.txt", "r+", encoding="utf8")

currentPersona = "Jaren"
language = "en"
speakFile = 'temp'
fileNum = 0
fileToUse = "MyCommands.txt"
questionsFilePath = "Questions.txt"
personaFilePath = "personas.txt"
movesFilePath = "moves.txt"

class order:
    toppings = {}
    restaurants = {}
    usual = {}
    topsMatch ={}

    def __init__(self, tops, rest, us,topsMatch):
        self.toppings = tops
        self.restaurants = rest
        self.usual = us
        self.topsMatch = topsMatch


def readFiles():
    #Keys File
    for key in keysFile.readlines():
        keys.append(key.strip())

    #Moves file
    for line in movesFile.readlines():
        moveName = line.split(":")[0].strip()
        moveCmds = line.split(":")[1].strip()
        allMoves = moveCmds.split("||")
        movesToAdd = []
        for move in allMoves:
            move = move.strip()
            movesToAdd.append([move.split(" ")[0],move.split(" ")[1]])
        moves[moveName] = movesToAdd

    #Food file
    nextCount = 0
    restaurants = {}
    tops = {}
    usual = {}
    topsMatch ={}
    objToUse = [restaurants, tops, usual]
    count = 0
    for line in foodFile.readlines():
        line = line.strip()
        if line.strip() != '':
            if line == "next":
                count += 1
                continue
            lineSplit = line.split("=")
            subject = lineSplit[0]
            list = lineSplit[1].split(",")
            objToUse[count][subject] = []
            for item in list:
                objToUse[count][subject].append(item.lower().strip())

    #Questions
    for line in questionsFile:
        line = line.strip()
        questions.append(line)

    #Personas
    curr = "first"
    types = ["fact", "question"]
    type = ""
    for line in personaFile.readlines():
        line = line.strip()
        if "Name" in line:
            name = line.split("Name")[1].strip().split(" ")
            first = name[0]
            last = name[1]
            if curr != "first":
                curr = {}
                personas[curr[first]] = curr
            if curr == "first":
                curr = {}

            curr["first name"] = first
            curr["last name"] = last
            curr["name"] = first + " " +last
            curr["questions"] = {}
            curr["facts"] = []
            type = types[0]
        else:
            if type == "fact":
                curr["facts"].append(line)
            if line == "Questions":
                type = types[1]
                continue
            if type == "question" and line != "Questions":
                questSplit = line.split("||")
                quest = questSplit[0].strip()
                ans = questSplit[1].strip()
                curr["questions"][quest] = ans
    personas[curr["first name"]] = curr


    #Toppings Match File
    for line in topsMatchFile.readlines():
        restTopsSplit = line.strip().split("=")
        rest = restTopsSplit[0]
        topsMatch[rest] = {}
        topCodes = restTopsSplit[1].split("||")
        for topCode in topCodes:
            topping = topCode.split(":")[0]
            code = topCode.split(":")[1]
            topsMatch[rest][topping] = code

    global orders
    orders = order(tops, restaurants, usual,topsMatch)

    #Directions file
    for line in dirFile.readlines():
        if line.strip() != '':
            dirSplit = line.split("=")
            direct = dirSplit[0]
            synList = dirSplit[1]
            for syn in synList.split(","):
                dirSyns[syn.strip()] = direct.upper()

    #Commands File
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

    #mode = speak("Which mode shall I enter? Act, Learn, Read or Erase?")
    mode = "Act"
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


def act(actCmd="None"):
    if actCmd == "None":
        command = speak("Please enter a command")
    else:
        command = actCmd
    command = command.lower().strip()
    if command not in allCommands:
        wasAction = checkActionCommands(command)
        if wasAction:
            return
        teachBool = speak("That command does not yet exist. Would you like to teach me?")
        if "yes" in teachBool.lower() or "yeah" in teachBool.lower():
            learn(command)
    else:
        chooseResponse = random.randint(0, len(allCommands[command])-1)
        speak(allCommands[command][chooseResponse], False)


def checkActionCommands(actCmd):
    if actCmd == "save" or actCmd =="update":
        writeFile()
        speak("Okay, I just updated.", False)
        return True
    if actCmd == "connect":
        init()
        return True
    if checkRecordAndLearnMoves(actCmd):
        return True
    if checkMoveAction(actCmd):
        return True
    if checkSetSpeed(actCmd):
        return True
    if checkOrderFood(actCmd):
        return True
    if checkPlayYoutubeVid(actCmd):
        return True
    if checkPlayMusic(actCmd):
        return True
    if checkTellAboutSelf(actCmd):
        return True
    if checkAskQuestion(actCmd):
        return True
    return False


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
        equalsString = "that's like saying "
        if "that's like saying " in action or "that's the same as saying " in action:
            if "that's the same as saying " in action:
                equalsString = "that's the same as saying"
            cmd2 = action.split(equalsString)[1].strip()
            print(cmd2)
            while cmd2 not in allCommands and cmd2 != "cancel":
                cmd2 = speak(cmd2 +" is not a valid Fcommand. Please try again, or say cancel.")
            if cmd2.lower().strip() == "cancel":
                continue
            allCommands[command] = allCommands[cmd2]
            for action in allCommands[cmd2]:
                allActions[action].append(command)
                speak("Okay, got it!")
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
    success = False
    count = 0
    while not success and count < 3:
        try:
            audio.save(file)
            success = True
        except Exception as e:
            if count == 2:
                print("Could not connect to Google Audio at all.")
                #speak("Could not connect to Google Audio at all. Try restarting the program.", False)
                #sys.exit()
            count += 1

    if success:
        playsound.playsound(file)
        os.remove(file)
        fileNum += 1
    else:
        print(line)
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
                        cmdAction += ",,"+action2
                    else:
                        fstList = False
                        cmdAction += action2
            else:
                cmdAction += action
            allStringCommands += cmdAction
            completedCommands.append(allActions[action])
    newFile = open(fileToUse, "w")
    newFile.write(allStringCommands)
    newFile.close()

    allPersonas = ""
    for persona in personas:
        allPersonas += "Name "+personas[persona]["name"]+"\n"
        for fact in personas[persona]["facts"]:
            allPersonas += fact+"\n"
        allPersonas+="Questions\n"
        for question in personas[persona]["questions"]:
            allPersonas += question + " || " + personas[persona]["questions"][question]+"\n"
    newFile = open(personaFilePath, "w")
    newFile.write(allPersonas)
    newFile.close()

    allMoves = ""
    for move in moves.keys():
        allMoves += move + ": "
        first = True
        for action in moves[move]:
            if not first:
                allMoves += " || "
            else:
                first = False
            allMoves += action[0] + " " + action[1]
        allMoves += "\n"
    newFile = open(movesFilePath, "w")
    newFile.write(allMoves)
    newFile.close()



def intro():
    name = speak("Hello! My name is Arni! It stands for Automated Robotic Neural Interface. What's your name?")
    if name == "skip":
        return True
    rightName = speak("I got your name as " + name + ", is that right?")
    if name != "Jaron":
        while rightName.lower() != "yes" and rightName.lower() != "yeah":
            name = speak("Okay, please tell me your name again.")
            rightName = speak("I got your name as " + name + ", is that right?")
    user = Arni(name)
    if name =="Jaron":
        currentPersona = "Jaren"
        name = "Jaren"
    else:
        if name in personas:
            currentPersona = name
        else:
            personas[name] = [] #dothis MAKE NEW PERSONA!!!!
    speak("Hello there "+name+", I am excited to help you! Just call me if you need anything.", False)
    return False


def listenForName():
    print("Begin")
    speak("Okay, lets get started!", False)
    passcode = ""
    with sr.Microphone() as source:
        while passcode != "exit":
            try:
                audio = recog.listen(source)
                passcode = recog.recognize_google(audio)
                passcode = passcode.lower()
                print(passcode)
                for key in keys:
                    if key in passcode:
                        print("Time to act!")
                        passcode = key+" "+passcode.split(key)[1]
                        if "honey" in passcode:
                            passcode.replace("honey","arnie")
                        if key != passcode:
                            passcode = passcode.replace(key,"").strip()
                        if passcode == "exit":
                            continue
                        act(passcode)
            except Exception as e:
                print("Nothing recorded...")
        speak("Alright, I guess I will log off for now. Bye-bye!", False)
        commandFile.close()
        writeFile()


def checkRecordAndLearnMoves(actCmd):
    keys = ["record this move", "record these moves", "learn this move", "learn these moves"]
    validMove = False
    finished = False
    newMoves = []
    if actCmd in keys:
        while not finished:
            moveName = speak("What's the name of this move?")
            moveName = moveName.lower()
            if moveName.lower() == "exit" or moveName.lower() == "stop":
                finished = True
            moveCmd = speak("And what should I do? Separate moves by saying, then")
            if moveCmd.lower() == "just watch":
                #Record movements through remote control
                return True
            else:
                while not validMove:
                    allMoves = moveCmd.split(" then ")
                    for currMove in allMoves:
                        validMove = False
                        currMove = currMove.replace("one","1")
                        move = re.match(r"move (?P<direction>\w+) *[for]* *(?P<duration>[0-9]+) *[second]*[s]*", currMove)
                        if move:
                            dir = move.group("direction")
                            duration = move.group("duration")
                            if dir in dirSyns:
                                newMoves.append([dir,duration])
                                validMove = True
                            else:
                                moveCmd = speak("I didnt get that move, please say the entire move again.")
                                validMove = False
                                if moveCmd.lower() == "exit" or moveCmd.lower() == "cancel":
                                    return True
                                break
                        else:
                            moveCmd = speak("I didnt get that move, please say the entire move again.")
                            validMove = False
                            if moveCmd.lower() == "exit" or moveCmd.lower() == "cancel":
                                return True
                            break
            moves[moveName] = newMoves
            newMoves = []
            if "these" in actCmd:
                speak("Got it, lets move on to the next move.", False)
            else:
                speak("Okay, I just added "+moveName, False)
                return True
    else:
        return False


def roam():
    duration = random.randint(1, 10)



def checkMoveAction(actCmd):
    actCmd = actCmd.replace("one","1")
    if "roam" in actCmd:
        roam()
        return True
    action = re.match(r"move (?P<direction>\w+) *[for]* *(?P<duration>[0-9]*) *[second]*[s]*", actCmd)
    if action:
        dir = action.group("direction")
        duration = action.group("duration")
        if "one" in duration:
            duration = 1
        results = "Found direction " + dir
        cmd = "arnie move"
        if duration != '':
            results += " and found duration " + duration
        print(results)
        if dir in dirSyns:
            chooseResponse = random.randint(0, len(allCommands[cmd]) - 1)
            speak(allCommands[cmd][chooseResponse] + " " + dir + "!", False)
            if duration != '':
                move(dirSyns[dir], duration)
            else:
                move(dirSyns[dir])
            return True
        else:
            speak("That direction does not exist, please try again.", False)
    else:
        action = re.match("do the (?P<moveName>.+) *(?P<times>[0-9]*) *[time]*[s]*", actCmd)
        if action:
            moveName = "the " + action.group("moveName")
            times = action.group("times")
            if times == '':
                times = 1
            if moveName in moves.keys():
                count = 0
                while count< times:
                    for currMove in moves[moveName]:
                        move(dirSyns[currMove[0]], currMove[1])
                        time.sleep(int(currMove[1]))
                    count += 1
            else:
                teach = speak("I'm sorry, I don't know that move. Would you like to teach me?")
                if teach.lower() =="yes" or teach.lower() == "yeah":
                    checkRecordAndLearnMoves("record this move")
            return True
        return False


def checkTellAboutSelf(actCmd):
    ask = ["tell me about myself", "what do you know about me", "tell me something about me",
           "tell me what you know about me", "tell me something you know about me", "tell me something about myself"]
    if actCmd in ask:
        resp = "Your name is " + currentPersona + ". "
        if len(personas[currentPersona]["questions"].keys()) != 0:
            questNum = random.randint(0, len(personas[currentPersona]["questions"].keys()))
            quest = list(personas[currentPersona]["questions"].keys())[questNum]
            resp += "When I asked you "+quest+", you said " + personas[currentPersona]["questions"][quest]+". "
        else:
            qs = speak("I dont know much about you yet, but I know your name is " + personas[currentPersona]["name"]
                       + ". Can I go ahead and ask you some questions?")
            if qs == "yes" or qs == "yeah" or qs == "sure":
                checkAskQuestion("ask me a question")
            else:
                return True
        factNum = random.randint(0, len(personas[currentPersona]["facts"]))
        fact = personas[currentPersona]["facts"][factNum]
        factNum2 = random.randint(0, len(personas[currentPersona]["facts"]))
        fact2 = personas[currentPersona]["facts"][factNum2]
        resp += fact
        if fact2 != fact:
            resp += ", and  " + fact2
        speak(resp, False)
        return True
    return False


def checkAskQuestion(actCmd):
    ask = ["ask me a question about myself", "ask me a question", "ask me about myself",
           "ask me another question", "ask me some questions", "ask me some questions"]
    if actCmd in ask:
        quest = "start"
        count = 1
        i = 0
        if "some" in actCmd:
            count = random.randint(2, 4)
        while i < count:
            while quest == "start" or quest in personas[currentPersona]["questions"].keys():
                quest = questions[random.randint(0, len(questions) - 1)]
            response = speak(quest)
            personas[currentPersona]["questions"][quest] = response
            quest = "start"
            i+= 1
        return True
    return False


def checkSetSpeed(actCmd):
    action = re.match("set speed to (?P<speed>[0-9]*)", actCmd)
    if action:
        sendArduinoMessage("Speed "+action.group("speed"))
        return True
    return False


def checkPlayMusic(actCmd):
    action = re.match(r"shuffle [my]* *(?P<playlist>.+?(?= playlist)) *[playlist]* *[on]* *[from]* *(?P<musicApp>\w+)", actCmd)
    action2 = re.match(r"play (?P<playlist>.+?(?= on)) on (?P<musicApp>\w+)", actCmd)
    action3 = re.match(r"play (?P<playlist>.+?(?= by)) by (?P<artist>\w+) on (?P<musicApp>\w+)", actCmd)
    if action or action2 or action3:
        if action2:
            action = action2
        elif action3:
            action = action3
            global connectedToSpeaker
        if not connectedToSpeaker:
            try:
                s.connect((homeSpeakerMACAddress, port))
                connectedToSpeaker = True
            except:
                speak("I can't connect to the home speaker, make sure its on and in bluetooth mode.", False)
        try:
            if action3:
                playMusic(action.group("playlist"), action.group("musicApp"), action.group("artist"))
            else:
                playMusic(action.group("playlist"), action.group("musicApp"))
        except:
            speak("I'm having trouble playing music right now, please try again later.", False)
        return True
    return False


def checkPlayYoutubeVid(actCmd):
    action = re.match("play (?P<search>.*) *[videos]* on my tv", actCmd)
    if action:
        devices, browser = pychromecast.get_chromecasts()
        for chromecast in devices:
            if chromecast.device.friendly_name == "Family Room TV":
                cast = chromecast
        cast.wait()
        yt = YouTubeController()
        cast.register_handler(yt)
        search = action.group("search")
        driver = webdriver.Chrome(service=Service(ChromeDriverManager().install()))
        driver.get("https://www.youtube.com/")
        chrome_options.add_experimental_option("detach", True)
        driver.find_element(by=By.XPATH, value="//input[@aria-label='Search']").send_keys(search)
        driver.find_element(By.ID, "search-icon-legacy").click()
        time.sleep(3)
        ytIDs = []
        youtubeElts= driver.find_elements(By.XPATH, value="//a[@id='video-title']")
        for vid in youtubeElts:
            url = vid.get_attribute("href")
            id = url.split("?v=")[1]
            ytIDs.append(id)
        time.sleep(2)
        idCount = 0
        yt.play_video(ytIDs[idCount])
        speak("Okay, playing "+search+" on your TV", False)
        time.sleep(3)
        goodVideo = speak("Is this the right video?")
        while goodVideo != "yes" and goodVideo != "yeah" and goodVideo != "yep":
            idCount+=1
            yt.play_video(ytIDs[idCount])
            time.sleep(3)
            goodVideo = speak("Is this the right video?")
        speak("Okay, enjoy your video!", False)
        return True
    return False


def playMusic(music, app, artist="null", tryAgain=True):
    if app.lower().strip() == "spotify":
        speak("Okay, playing "+music+" on spotify. Give me a sec.",False)
        playSpotify(music)
    elif app.lower().strip() == "google":
        #playYoutubeMusic(music)
        return
    elif app.lower().strip() == "youtube":
        #playYoutube(music)
        return
    else:
        if tryAgain:
            app = speak("I can't find the music app "+app+", please try one more time.")
            playMusic(music, app, False)
            return
        speak("I couldn't find the music app "+app+", please try again later.", False)


def playSpotify(music, artist="empty"):
    try:
        driver = webdriver.Chrome(service=Service(ChromeDriverManager().install()))
        driver.get("https://accounts.spotify.com/en/login?continue=https:%2F%2Fopen.spotify.com%2F")
        chrome_options.add_experimental_option("detach", True)
        driver.find_element(By.ID, "login-username").send_keys("jbutler119@student.umgc.edu")
        driver.find_element(By.ID, "login-password").send_keys("EgYa9846!!!100273")
        driver.find_element(By.ID, "login-button").click()
        time.sleep(5)
        driver.find_element(by=By.XPATH, value="//a[@href='/search']").click()
        time.sleep(2)
        if artist != "empty":
            driver.find_element(by=By.XPATH, value="//input[@data-testid='search-input']").send_keys(music+" "+artist)
        else:
            driver.find_element(by=By.XPATH, value="//input[@data-testid='search-input']").send_keys(music)
        time.sleep(2)
        driver.find_element(by=By.XPATH, value="//section[@aria-label='Top result']").click()
        time.sleep(2)
        try:
            driver.find_element(By.ID, "onetrust-close-btn-container").click()
            time.sleep(1)
        except:
            print("Cookies message not found")
        play = driver.find_element(by=By.XPATH, value="//button[@data-testid='play-button']")
        driver.find_element(by=By.XPATH, value="//button[@data-testid='control-button-shuffle']").click()
        time.sleep(1)
        driver.execute_script("arguments[0].click();", play)
        time.sleep(1)
    except Exception as e:
        print(e)
        speak("I had trouble opening chrome. Make sure you have the latest chromedriver downloaded to play music.", False)


def checkOrderFood(actCmd):
    action = re.match(r"order a* *(?P<food>\w+) *[from]* *(?P<restaurant>\w*\'*s*)", actCmd)
    if action:
        food = action.group("food").lower().strip().replace("'","")
        rest = action.group("restaurant").lower().strip().replace("'","")
        if rest != "":
            if food in orders.restaurants and rest in orders.restaurants[food]:
                addString =""
                if food =="pizza" and rest == "dominos":
                    addString="Just say 4 toppings, the first two will be for the first pizza and the next two for the second."
                topsString = speak("What toppings would you like with that?"+addString)
                topsString = topsString.strip()
                topsString = topsString.replace("and ",'')
                tops = topsString.split(" ")
                orderFood(food, rest, tops)
            else:
                speak("I could not find your order for "+food+" from "+rest+", please try again.", False)
        elif food in orders.food:
            orderFood(food)
        return True
    return False


def orderFood(food, rest="usual", tops="usual"):
    actualTops = []
    cancelCount = 0
    if tops != "usual":
        for top in tops:
            while top not in orders.toppings[food+" toppings"] and cancelCount<3:
                top = speak("I could not find the topping "+top+" please say this topping again.")
                cancelCount += 1
            if cancelCount == 3:
                speak("Sorry, I could not complete your order. Please try again.")
                return
            actualTops.append(top)
            cancelCount = 0
    else:
        tops = orders.usual[food+" "+tops]
    if rest == "usual":
        rest = orders.restaurants[food][0]  #default restaurants are first
    actuallyOrder = speak("Are you sure you want me to order "+food+" from "+rest+"?")
    if actuallyOrder =="yes" or actuallyOrder =="yeah" or actuallyOrder =="yep":
        speak("Okay, ordering "+food+" from "+rest+". Hold tight, this will take a minute, I'll let you know when I'm done.", False)
        findRestaurantFunction(rest, tops)
    #order food from rest


def findRestaurantFunction(rest, tops):
    if rest == "dominos":
        orderDominos(tops)
    elif rest == "papa johns":
        #orderPapaJohns(tops)
        return
    elif rest == "paisanos":
        #orderPaisanos(tops)
        return
    elif rest == "wise guys":
        #orderWiseGuys(tops)
        return
    elif rest == "paisanos":
        #orderPaisanos(tops)
        return
    elif rest == "nandos":
        #orderNandos(tops)
        return
    elif rest == "all about burger":
        #orderAllAboutBurger(tops)
        return
    elif rest == "five guys" or rest == "5 guys":
        #orderFiveGuys(tops)
        return
    elif rest == "buffalo wild wings":
        #orderBW3s(tops)
        return
    elif rest == "the goat":
        #orderTheGoat(tops)
        return
    else:
        #orderChipotle(tops)
        return

def checkDominosStatus():
    driver = webdriver.Chrome(service=Service(ChromeDriverManager().install()))
    driver.get("https://www.dominos.com/en/pages/tracker/#!/track/order/")
    chrome_options.add_experimental_option("detach", True)
    #document.getElementbyId("majorStatus").innerHTML


def orderDominos(tops):
    #This assumes the usual will be 2 medium 2 topping pizzas
    pizzas = [[tops[0], tops[1]],[tops[2], tops[3]]]
    driver = webdriver.Chrome(service=Service(ChromeDriverManager().install()))
    driver.get("https://www.dominos.com/en/pages/customer/#!/customer/login/")
    chrome_options.add_experimental_option("detach", True)
    time.sleep(3)
    email = driver.find_element(By.ID, "Email")
    email.send_keys("jabdesigning@gmail.com")
    pw = driver.find_element(By.ID, "Password")
    pw.send_keys("EgYa9846!!!100273")

    submit = driver.find_element(by=By.CLASS_NAME, value="js-loginSubmit")
    submit.click()
    time.sleep(5)
    driver.find_element(by=By.CLASS_NAME, value="qa-Cl_Coupons").click()
    time.sleep(3)
    driver.find_element(by=By.CLASS_NAME, value="featured-coupon-599MixMatch").click()
    time.sleep(3)
    driver.find_element(by=By.CLASS_NAME, value="js-delivery").click()
    time.sleep(1)
    driver.find_element(by=By.CLASS_NAME, value="js-search-cta").click()
    time.sleep(10)
    firstPizza = True
    for pizza in pizzas:
        driver.find_element(by=By.CLASS_NAME, value="js-cardExpandCollapse").click()
        driver.find_element(by=By.CLASS_NAME, value="js-productImage").click()
        time.sleep(3)
        driver.find_element(by=By.XPATH, value="//button[@data-quid = 'start-from-scratch']").click()
        time.sleep(2)
        driver.find_element(by=By.XPATH, value="//button[@data-quid = 'pizza-builder-next-btn']").click()
        time.sleep(3)
        driver.find_element(by=By.XPATH, value="//select[@aria-label='Robust Inspired Tomato Sauce']/option[@value='1.5']").click()
        time.sleep(1)
        driver.find_element(by=By.XPATH, value="//button[@data-quid='pizza-builder-next-btn']").click()
        time.sleep(1)
        if firstPizza:
            driver.find_element(by=By.XPATH, value="//button[@data-quid='builder-no-step-upsell']").click()
        time.sleep(1)
        for topping in pizza:
            topCode = orders.topsMatch["dominos"][topping]
            driver.find_element(by=By.CLASS_NAME, value=topCode).click()
        time.sleep(1)
        driver.find_element(by=By.CLASS_NAME, value="c-order-addToOrder").click()
        time.sleep(3)
        if firstPizza:
            driver.find_element(by=By.XPATH, value="//button[@data-quid='pizza-sides-no-thanks']").click()
        firstPizza =False
        time.sleep(3)

    driver.find_element(by=By.XPATH, value="//a[@data-quid='fulfiller-wizard-done-with-coupon']").click()
    time.sleep(3)
    driver.find_element(by=By.XPATH, value="//a[@data-quid='order-checkout-button']").click()
    time.sleep(6)
    try:
        driver.find_element(by=By.CLASS_NAME, value="js-nothanks").click()
        time.sleep(3)
    except:
        print("Not Found")
    driver.find_element(by=By.XPATH, value="//button[@data-quid='upsell-product-F_SIDGAR-button']").click()
    time.sleep(2)
    driver.find_element(by=By.XPATH, value="//button[@data-quid='add-button-default']").click()
    time.sleep(2)
    driver.find_element(by=By.XPATH, value="//a[@data-quid='continue-checkout-btn']").click()
    time.sleep(6)
    try:
        driver.find_element(by=By.CLASS_NAME, value="contactless-payment-instructions__cta").click()
        time.sleep(3)
    except:
        print("Not Found")
    driver.find_element(by=By.XPATH, value="//input[@data-quid='credit-payment-type']").click()
    driver.find_element(by=By.XPATH, value="//label[@data-quid='tips-tip-amount-option-value-1']").click()
    #Heres where it actually gets ordered, commenting out for obvious reasons
    #driver.find_element(by=By.XPATH, value="//button[@data-quid='payment-order-now']").click()
    speak("Okay. Pizza Ordered! Check your email for some updates.")


def sendArduinoMessage(message):
    s.send(bytes(message, 'UTF-8'))
    print('Sending '+message)


def move(direct, duration=3):
    sendArduinoMessage(Direction[direct])
    time.sleep(int(duration))
    sendArduinoMessage(Direction["STOP"])


class Arni:
    locX = 0
    locY = 0
    name = ""

    def __init__(self, newname):
        self.name = newname


def init():

    try:
        s.connect((arniMACAddress, port))
    except:
        resp = speak("I couldn't Connect to my body via Bluetooth. Shall I try again?")
        if resp == "yes" or resp == "yeah":
            init()

recog = sr.Recognizer()
user = None
readFiles()
chromedriver_autoinstaller.install()
skip = intro()
if not skip:
    init()
listenForName()
#listen()

