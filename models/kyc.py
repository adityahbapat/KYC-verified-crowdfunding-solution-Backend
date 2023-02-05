import json
from flask import Flask, Response, request, jsonify
from flask_restful import Resource, Api
from dotenv import load_dotenv, find_dotenv
import cv2
import datetime
import time
import requests
import fitz
import re
from deepface import DeepFace
from bson import ObjectId

import os
load_dotenv(find_dotenv())

app = Flask(__name__)
app.config["IMAGE_UPLOADS"] = r"C:\Users\Aditya Bapat\Downloads\kyc_images"

def upload_image(image):
    print("IMAGE-- ",image.filename)
    image.save(os.path.join(app.config["IMAGE_UPLOADS"]+'\\Uploads\\', image.filename))
    dirname=str(datetime.datetime.now())
    dirname=dirname.replace(':','')
    dirname=dirname.replace('-','')
    dirname=dirname.replace(' ','')
    directory = str(dirname)
    newpath = r'C:\Users\Aditya Bapat\Downloads\kyc_images\\imgdatabase'+str(dirname) +'\\Dataset'
    print(newpath)
    if not os.path.exists(newpath):
        os.makedirs(newpath)
    
    if allowed_pdf(image.filename):
        formImg(image.filename,dirname)
        print("formImg working")
    else:
        print(image.filename) 
        formDirectImg(image.filename,dirname)
    return [True, directory]

#------------If the file is PDF----------------------------------------------------
def allowed_pdf(filename):
    return '.' in filename and \
           filename.rsplit('.', 1)[1].lower() =='pdf'

count1=0
#-------------- Get Images from PDF & extracting Faces---------------------------------------
def formImg(fileName,dirname):
    doc = fitz.open(app.config["IMAGE_UPLOADS"]+'\\Uploads\\' + fileName)
    if len(doc)!=0:
        print("Length doc -- ", len(doc))
    counter = 0
    for i in range(len(doc)):
        for img in doc.get_page_images(i):
            xref = img[0]
            pix = fitz.Pixmap(doc, xref)
            if pix.n < 5:       # this is GRAY or RGB
                pix.save(app.config["IMAGE_UPLOADS"]+"\pdf%s.png" % (i))
                counter += 1
            else:               # CMYK: convert to RGB first
                pix1 = fitz.Pixmap(fitz.csRGB, pix)
                pix1.save(app.config["IMAGE_UPLOADS"]+"\pdf%s.png" % (i))
                pix1 = None
                counter += 1
            pix = None
    global count1
    count1=0
    for i in range(0, counter):
        imagePath = r"C:\Users\Aditya Bapat\Downloads\kyc_images\pdf" +str(i)+".png"
        image = cv2.imread(imagePath)
        print("Image read - ",image)
        try:
            gray = cv2.cvtColor(image, cv2.COLOR_BGR2GRAY)
            print("Gray -- ", gray)
        except:
            return ''
        #create the haar cascade
        faceCascade = cv2.CascadeClassifier(cv2.data.haarcascades + "haarcascade_frontalface_default.xml")
        #Detect faces in image
        faces = faceCascade.detectMultiScale(
            gray,
            scaleFactor=1.1,
            minNeighbors=3,
            minSize=(30, 30)
        )
        
        print("[INFO] Found {0} Faces.".format(len(faces)))
        padding = 30
        #drawing the rectangles in the image
        for (x, y, w, h) in faces:
            image = cv2.rectangle(image, (x-padding, y-padding),(x + w+padding, y + h+padding), (0, 255, 0), 2)
            roi_color = image[y-30:y + h+30, x-30:x + w+30]
            print("[INFO] Object found. Saving locally.")
            #if(count==0):
            cv2.imwrite(r'C:\Users\Aditya Bapat\Downloads\kyc_images\\imgdatabase'+str(dirname)+'\\Dataset\\face'+str(count1)+'.jpg', roi_color)
            count1=count1+1
        status = cv2.imwrite(r'C:\Users\Aditya Bapat\Downloads\kyc_images\\faces_detected.jpg', image)
        print('count: ',count1)
        print("[INFO] Image faces_detected.jpg written to filesystem: ", status)
    return ''

#-------------------Getting faces from Image directly---------------------------------
def formDirectImg(filename,dirname):
    print("OK NO PDF ONLY IMAGE")
    global count1
    count1=0
    image = cv2.imread(app.config["IMAGE_UPLOADS"] +'\\Uploads\\'+ filename)
    print(filename,dirname)
    print("Image : ")
    #print(image)
    gray = cv2.cvtColor(image, cv2.COLOR_BGR2GRAY)
    print(gray)
    #create the haar cascade
    faceCascade = cv2.CascadeClassifier(cv2.data.haarcascades + "haarcascade_frontalface_default.xml")
    #Detect faces in image
    faces = faceCascade.detectMultiScale(
            gray,
            scaleFactor=1.1,
            minNeighbors=9,
            minSize=(30, 30)
    )
    print("[INFO] Found {0} Faces.".format(len(faces)))
    padding = 40
    #drawing the rectangles in the image
    for (x, y, w, h) in faces:
        image = cv2.rectangle(image, (x-padding, y-padding),(x + w+padding, y + h+padding), (0, 255, 0), 2)
        roi_color = image[y-30:y + h+30, x-30:x + w+30]
        print("[INFO] Object found. Saving locally.")
        #if(count1==0):
        cv2.imwrite(r'C:\Users\Aditya Bapat\Downloads\kyc_images\\imgdatabase'+str(dirname)+'\\Dataset\\face'+str(count1)+'.jpg', roi_color)
        count1=count1+1
    status = cv2.imwrite(r'C:\Users\Aditya Bapat\Downloads\kyc_images\\faces_detected.jpg', image)
    print("[INFO] Image faces_detected.jpg written to filesystem: ", status)
    return ''



def kycUserCreate(request, db):
    print(request.files)
    print(json.loads(request.form.get("data2")))
    try:
        data = json.loads(request.form.get("data2"))

        headers1={ "Content-Type": "application/json",
        "apy-token": "APT0EppjfyDqxgfYbu4iQllrhIhETXsrnlQEvancq2Vu5Sj" }


        data1 = '{"email":"'+data["email"]+'"}'
        res = requests.post("https://api.apyhub.com/validate/email/dns", data = data1,
        headers=headers1 )
        # res = res.json()
        print("res -- ",res.json())
        res = res.json()
        # print("res status --", res.status())
        if(not res["data"]):
            return Response(
                response=json.dumps({
                "message":"User Email not valid"
            }),
            status = 400,
            mimetype="application/json"
            )


        headers1={ "Content-Type": "application/json",
            "apy-token": "APT0EppjfyDqxgfYbu4iQllrhIhETXsrnlQEvancq2Vu5Sj" }
        data1 = '{"postcode":"'+str(data["pincode"])+'"}'
        res = requests.post("https://api.apyhub.com/validate/postcodes/in", data = data1,
        headers=headers1 )
        # res = res.json()
        print("res -- ",res.json())
        res = res.json()
        # print("res status --", res.status())
        if(not res["data"]):
            return Response(
                response=json.dumps({
                "message":"User Pincode not valid"
            }),
            status = 400,
            mimetype="application/json"
            )

        if request.files:
            image = request.files["document"]
            directory = upload_image(image)
            if(directory[0]):
                print("Image uploaded successfully")
            else:
                Exception("Image uploading error")
        else:
            raise Exception("Sorry, no file exist")
        
        query = {
            "fname": data["fname"],
            "lname": data["lname"],
            "email": data["email"],
            "city": data["city"],
            "pincode": data["pincode"],
            "password": data["password"],
            "kycstatus": False
        }
        dbresponse = db.user.insert_one(query)
        if(dbresponse):
            return Response(
                response=json.dumps({
                "message":"User created",
                "id":f"{dbresponse.inserted_id}",
                "dirname":directory[1]
            }),
            status = 200,
            mimetype="application/json"
            )
        else:
            return Response(
                response=json.dumps({
                "message":"User Creation Failed"
            }),
            status = 400,
            mimetype="application/json"
            )
    except Exception as ex:
        print("Exception --- ", ex)
        return Response(
                response=json.dumps({
                "message":"User Creation Failed",
                "error":ex
            }),
            status = 400,
            mimetype="application/json"
            )


def camera(request, db):
    data= json.loads(request.data)
    dirname = data["dirname"]
    print(dirname)
    t=int(1000)
    cam = cv2.VideoCapture(0)
    cv2.namedWindow("Test")
    count = 0
    while True and t:
        ret,img=cam.read()
        cv2.imshow("Test", img)
        cv2.waitKey(1)
        
        cv2.imshow("Test",img)
        mins,secs=divmod(t,60)
		#timer='{:02d}:{02d}'.format(mins,secs)
        if(t==500 or t==750):
            print("Image "+str(count)+"saved")
            cv2.imwrite(r'C:\Users\Aditya Bapat\Downloads\kyc_images\imgdatabase'+str(dirname)+'\\Dataset\\cam'+str(count)+'.jpeg', img)
            count +=1
            #time.sleep(1)
            
        time.sleep(0.01)
            
        t-=2
        #cv2.imshow("Test",img)
        if(t==0 and cv2.waitKey(1)):
            print("Close")
            break
    cam.release()
    cv2.destroyAllWindows() 
    value = compare(dirname)
    print("1 Value is:",value)
    print("1 Value Type:",type(value))

    newvalues = {"$set": { "kycstatus": value}}
    myquery = {"_id": ObjectId(data["id"])}
    if value:
        newvalues = {"$set": { "kycstatus": True } }
    else:
        newvalues = {"$set": { "kycstatus": False } }
    print("2 Value is:",value)
    print("newVal:",newvalues)
    dbresponse = db.user.update_one(myquery, newvalues)

    print("dbres:",dbresponse)
    if(dbresponse):
        return Response(
            response=json.dumps({
            "message":"KYC Data Result",
            "kycstatus":value
        }),
        status = 200,
        mimetype="application/json"
        )
    else:
        return Response(
            response=json.dumps({
            "message":"Error on KYC video verification"
        }),
        status = 400,
        mimetype="application/json"
        ) 

def compare(dirname):
    print('Compare')
    global count1
    print('Count1 : ',count1)
    for j in range(2):
        print('Path1 '+str(j))
        path1=r'C:\Users\Aditya Bapat\Downloads\kyc_images\\imgdatabase'+str(dirname)+'\\Dataset\\cam'+str(j)+'.jpeg'
        for i in range(0,count1):
            print('Path2 '+str(i))
            try:
                path2=r'C:\Users\Aditya Bapat\Downloads\kyc_images\\imgdatabase'+str(dirname)+'\\Dataset\\cam'+str(i)+'.jpeg'
                print('Comparing image cam'+str(j)+' & face'+str(i))
                result = DeepFace.verify(img1_path =path1,img2_path =path2, model_name = "VGG-Face", distance_metric = "cosine")
                threshold = 0.30 #threshold for VGG-Face and Cosine Similarity
                print("Is verified: ", result["verified"])
                print("type:", type(result["verified"]))
                if result["verified"]:
                    return True
                else:
                    return False
            except:
                print("There was an issue")
    return False