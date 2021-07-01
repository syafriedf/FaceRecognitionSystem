import cv2
import numpy as np
import os
from datetime import datetime
import datetime as dt
import pandas as pd
import time, datetime
import requests
import MySQLdb
import pyttsx3

#Variable untuk mendefinisikan library
recognizer = cv2.face.LBPHFaceRecognizer_create()
recognizer.read('trainer/trainer.yml')
cascadePath = "haarcascades/haarcascade_frontalface_default.xml"
faceCascade = cv2.CascadeClassifier(cascadePath)

#Fungsi untuk mengambil data pegawai dan informasi nya
def getProfile(id):
    mydb = MySQLdb.connect("localhost","root","","sim_absensi_kominfo")
    mycursor = mydb.cursor()
    test = "SELECT * from data_pegawai WHERE id ="+str(id)
    mycursor.execute(test)
    results = mycursor.fetchall()
    profile=None
    for row in results:
        profile=row
    mydb.close()
    return profile

# Initialize and start realtime video capture
cam = cv2.VideoCapture(1)
cam.set(3, 1920)  # set video widht
cam.set(4, 1080)  # set video height

# Define min window size to be recognized as a face
minW = 0.1*cam.get(3)
minH = 0.1*cam.get(4)

#Font untuk camera vision 
font = cv2.FONT_HERSHEY_SIMPLEX

#Untuk memprediksi wajah
while True:
    ret, img = cam.read()
    img = cv2.flip(img,1)
    gray = cv2.cvtColor(img, cv2.COLOR_BGR2GRAY)
    faces = faceCascade.detectMultiScale(
        gray,
        scaleFactor=1.2,
        minNeighbors=5,
        minSize=(int(minW), int(minH)),)
    for(x, y, w, h) in faces:
        cv2.rectangle(img, (x, y), (x+w, y+h), (0,255,0), 2)
        id, confidence = recognizer.predict(gray[y:y+h, x:x+w])
        ts = time.time()
        now = datetime.datetime.now()
        timestamp_date = datetime.datetime.fromtimestamp(ts).strftime('%Y-%m-%d')
        timestamp_time = datetime.datetime.fromtimestamp(ts).strftime('%H:%M:%S')
        profile = getProfile(id)
        if(profile!=None):
            confidence = "{0}%".format(round(100 - confidence))
            if(confidence <= "{0}%".format(round(100 - 35))):
                cv2.putText(img,"Unknown", (x,y+h+20), font, 1, (200, 0, 0), 1)
            else:
                cv2.putText(img,"NIP :" +str(profile[1]), (x,y+h+20), font, 1, (255, 255, 0), 1)
                cv2.putText(img,"Nama :" +str(profile[2]), (x,y+h+50), font, 1, (255, 255, 0), 1)
                cv2.putText(img,"Divisi :" +str(profile[3]), (x,y+h+80), font, 1, (255, 255, 0), 1)
                mydb = MySQLdb.connect("localhost","root","","sim_absensi_kominfo")
                mycursor = mydb.cursor()
                test = "SELECT * from data_entri_waktu where tanggal ='"+str(timestamp_date)+"'and nip ='"+str(profile[1])+"'" 
                mycursor.execute(test)
                results = mycursor.fetchall()
                profilenip=None
                for row in results:
                    profilenip=row
                mydb.close()
            
                if(len(results)>0):
                    # today16pm = now.replace(hour=16, minute=0, second=0, microsecond=0)
                    today13am = now.replace(hour=13, minute=0, second=0, microsecond=0)
                    today23am = now.replace(hour=23, minute=0, second=0, microsecond=0)
                    if (now > today13am and now < today23am):
                        mydb = MySQLdb.connect("localhost","root","","sim_absensi_kominfo")
                        mycursor = mydb.cursor()
                        if(profilenip[4]==None):
                            engine = pyttsx3.init()
                            engine.say('See You'+str(profile[2]))
                            engine.runAndWait()
                            mycursor.execute("UPDATE data_entri_waktu SET jam_pulang='"+str(timestamp_time)+"'WHERE nip='"+str(profile[1])+"'")
                            mydb.commit()
                            mydb.close()
                        else:
                            cv2.rectangle(img, (x, y), (x+w, y+h), (255,0,0), 2)
                            cv2.putText(img,"Already Absent", (x,y+h+120), font, 1, (255, 0, 0), 1)
                    else:
                        # cv2.rectangle(img, (x, y), (x+w, y+h), (255,0,0), 2)
                        # cv2.putText(img,"Already Absent", (x,y+h+120), font, 1, (255, 0, 0), 1)
                        cv2.putText(img,"NIP :" +str(profile[1]), (x,y+h+20), font, 1, (255, 255, 0), 1)
                        cv2.putText(img,"Nama :" +str(profile[2]), (x,y+h+50), font, 1, (255, 255, 0), 1)
                        cv2.putText(img,"Divisi :" +str(profile[3]), (x,y+h+80), font, 1, (255, 255, 0), 1)
                else:
                    today7am = now.replace(hour=7, minute=0, second=0, microsecond=0)
                    today12am = now.replace(hour=12, minute=0, second=0, microsecond=0)
                    if(now < today7am or now > today12am):
                        cv2.putText(img,"NIP :" +str(profile[1]), (x,y+h+20), font, 1, (255, 255, 0), 1)
                        cv2.putText(img,"Nama :" +str(profile[2]), (x,y+h+50), font, 1, (255, 255, 0), 1)
                        cv2.putText(img,"Divisi :" +str(profile[3]), (x,y+h+80), font, 1, (255, 255, 0), 1)
                    else:
                        if(confidence >= "{0}%".format(round(100 - 50))):
                            today8am = now.replace(hour=8, minute=0, second=0, microsecond=0)
                            if(now > today8am):
                                status = 'LATE'
                            else:
                                status = 'PRESENT'
                            mydb = MySQLdb.connect("localhost","root","","sim_absensi_kominfo")
                            cv2.putText(img,"Detected", (x,y+h+20), font, 1, (255, 0, 0), 1)
                            engine = pyttsx3.init()
                            engine.say('Good Morning'+str(profile[2]))
                            engine.runAndWait()
                            cv2.rectangle(img, (x, y), (x+w, y+h), (208,4,239), 2)
                            mycursor = mydb.cursor()        
                            mycursor.execute("INSERT into data_entri_waktu (nip,tanggal,jam_masuk,status) values('"+str(profile[1])+"','"+str(timestamp_date)+"','"+str(timestamp_time)+"','"+str(status)+"')")
                            mydb.commit()
                            mydb.close()
                        elif(confidence <= "{0}%".format(round(100 - 70))):
                            cv2.putText(img,"Unknown", (x,y+h+20), font, 1, (200, 0, 0), 1)
        else:
            confidence = "{0}%".format(round(100 - confidence))
            cv2.putText(img,"Unknown", (x,y+h+20), font, 1, (200, 0, 0), 1)

        cv2.putText(img, str(confidence), (x+5, y+h-5),font, 1, (255, 255, 0), 1)
    cv2.imshow('Face', img)
    k = cv2.waitKey(10) & 0xff  # Press 'ESC' for exiting video
    if k == 27:
        break

cam.release()
cv2.destroyAllWindows()
