import Arni
import time
import re
import pychromecast
import random
from pychromecast.controllers.youtube import YouTubeController
import bluetooth

#Bluetooth services
from selenium import webdriver

arniMACAddress = '00:0C:BF:13:7E:77'
homeSpeakerMACAddress = '00:12:6f:ac:55:e1'
port = 1
s = bluetooth.BluetoothSocket(bluetooth.RFCOMM)


