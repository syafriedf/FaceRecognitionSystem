''''
Training Multiple Faces stored on a DataBase:
	==> Each face should have a unique numeric integer ID as 1, 2, 3, etc                       
	==> LBPH computed model will be saved on trainer/ directory. (if it does not exist, pls create one)
	==> for using PIL, install pillow library with "pip install pillow"

Based on original code by Anirban Kar: https://github.com/thecodacus/Face-Recognition    

Developed by Marcelo Rovai - MJRoBot.org @ 21Feb18   

'''

import cv2
import numpy as np
from PIL import Image
import os

# Path for face image database
path = 'dataset'

recognizer = cv2.face.LBPHFaceRecognizer_create()
# detector = cv2.CascadeClassifier("haarcascades/haarcascade_frontalface_default.xml")

def getImagesAndLabels(path):
    imagePaths = [os.path.join(path, f) for f in os.listdir(path)]
    faceSamples = []
    IDs = []
    for imagePath in imagePaths:
        PIL_img = Image.open(imagePath).convert('L')  # convert it to grayscale
        img_numpy = np.array(PIL_img, 'uint8')
        ID = int(os.path.split(imagePath)[-1].split(".")[1])
        faceSamples.append(img_numpy)
        IDs.append(ID)
        cv2.imshow("training",img_numpy)
        cv2.waitKey(10)
    return np.array(IDs), faceSamples
    #     faces = detector.detectMultiScale(img_numpy)
    #     for (x, y, w, h) in faces:
    #         faceSamples.append(img_numpy[y:y+h, x:x+w])
    #         ids.append(id)
    # return faceSamples, ids
IDs, faceSamples = getImagesAndLabels(path)
recognizer.train(faceSamples,IDs)
# recognizer.train(faces, np.array(ids))
# Save the model into trainer/trainer.yml
# recognizer.save() worked on Mac, but not on Pi
recognizer.save('trainer/trainer.yml')
cv2.destroyAllWindows()
