import sys
import time
from xml.etree.ElementTree import tostring

import speech_recognition as sr
import pyttsx3 

from Adafruit_IO import MQTTClient
from uart import *
from nlp import *
import pandas as pd
import pickle
import datetime

# Get the current date, month, and year
today = datetime.datetime.now()
year = today.year
month = today.month
day = today.day
hour = today.hour

with open('model_temperature.pkl', 'rb') as file:
    temperature_model = pickle.load(file)

with open('model_humid.pkl', 'rb') as file:
    humid_model = pickle.load(file)


r = sr.Recognizer() 

def SpeakText(command):
	# Initialize the engine
	engine = pyttsx3.init()
	engine.say(command) 
	engine.runAndWait()

AIO_FEED_IDs = ["button1","button2","sensor1","sensor2","sensor3","ai","Ack"]
AIO_USERNAME = ""
AIO_KEY = ""

def connected(client):
    print("Connected ...")
    for topic in AIO_FEED_IDs:
        client.subscribe(topic)
    client.publish("Ack","0")


def subscribe(client , userdata , mid , granted_qos):
    print("Subscribe successfully ...")

def disconnected(client):
    print("Disconnected ...")
    client.publish("Ack","2")
    sys.exit(1)

def message(client , feed_id , payload):
    print("Receive data: " + payload, feed_id)
    if feed_id == "Ack":
        if payload == "0.5":
            client.publish("Ack","0")
    if feed_id == "button1":
        client.publish("Ack","1")
        if payload == '1':
            writeData("Light Bulb is turned On\n")
        elif payload == '0':
            writeData("Light Bulb is turned OFF\n")
    if feed_id == 'button2':
        client.publish("Ack","1")
        if payload == '1':
            writeData("Pump is turned ON\n")
        elif payload == '0':
            writeData("Pump is turned OFF\n")


client = MQTTClient(AIO_USERNAME , AIO_KEY)
client.on_connect = connected
client.on_disconnect = disconnected
client.on_message = message
client.on_subscribe = subscribe
client.connect()
client.loop_background()

try:
    while True:
        try:
		
		# use the microphone as source for input.
            with sr.Microphone() as source2:
                
                # wait for a second to let the recognizer
                # adjust the energy threshold based on
                # the surrounding noise level 
                r.adjust_for_ambient_noise(source2, duration=0.2)
                
                #listens for the user's input 
                audio2 = r.listen(source2)
                
                # Using google to recognize audio
                MyText = r.recognize_google(audio2)
                MyText = MyText.lower()

                print("Did you say ",MyText)
                result = chatbot(MyText)

                if result[0]['fan'] == 'off':
                    #publish data fan to off
                    client.publish("button2",0)
                elif result[0]['fan'] == 'on':
                    ##publish data fan to on
                    client.publish("button2",1)

                if result[0]['light'] == 'off':
                    #publish data light to off
                    client.publish("button1",0)
                elif result[0]['light'] == 'on':
                    ##publish data light to on
                    client.publish("button1",1)
                # SpeakText(MyText)
                
        except sr.RequestError as e:
            print("Could not request results; {0}".format(e))
            pass
            
        except sr.UnknownValueError:
            print("unknown error occurred")
            pass

        # Assuming you have the new data point
        new_data = pd.DataFrame({'hour': [hour], 'day': [day], 'month': [month]})
        next_temp = temperature_model.predict(new_data)
        prediction = "Predicted next temperature and humid: " + str(next_temp[0]) + "°C"
        next_humid = humid_model.predict(new_data)
        prediction += " and " + str(next_humid[0]) + "%"
        print(prediction)
        client.publish("ai",prediction)

        readSerial(client)
        time.sleep(5)
        
        
except KeyboardInterrupt:
    client.publish("Ack","2")
    time.sleep(2)