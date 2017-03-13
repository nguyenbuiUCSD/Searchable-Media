import boto3
import numpy as np
import cv2
import os.path
import glob, os

#------------------------------------------------------
# Capture the video- and chop the images
cap = cv2.VideoCapture('../videos/ShapeOfYouEdSheeran.mp4')
#dictionary container
video = {}
count = 0
postfix = 0
prefix = "frame"
while(cap.isOpened()):
  ret, frame = cap.read()
  video[count] = frame
  if ret:
    name = prefix + str (postfix)
    if (count % 20 == 0):
      cv2.imwrite('../images/'+name+".png", frame)
      postfix+=1
    count +=1
  else:
    break
maxframe = count
maxframereduced = postfix

#------------------------------------------------------
# Try to display video
count = 0
for count in range(0, maxframe):
  img = video[count]
  cv2.imshow('frame',img)
  if cv2.waitKey(1) & 0xFF == ord('q'):
    break
#------------------------------------------------------
#Using resource from aws
#need to pip install boto3 first
#then aws configure
#If can not confiure, need to sudo -H brew install awscli
s3 = boto3.resource('s3')
# Print out bucket names
print "All of my bucket before: "
for bucket in s3.buckets.all():
	print(bucket.name)

# Create a bucket
# Dont need to create again if already done
#s3.create_bucket(Bucket='g6datatest')
#s3.create_bucket(Bucket='g6datatest', CreateBucketConfiguration={
#                 'LocationConstraint': 'us-west-1'})

# Print out bucket names
print "All of my bucket after: "
for bucket in s3.buckets.all():
  print(bucket.name)


# Upload a all images
metadata = {}
postfix = 0
name = "../images/frame" + str (postfix)+ ".png"
key = "frame" + str (postfix)+ ".png"
while os.path.exists(name):
  # Show image
  frame = cv2.imread(name,0)
  cv2.imshow('frame',frame)
  
  data = open(name, 'rb')
  key = "frame" + str (postfix)+ ".png"
  s3.Bucket('datatest').put_object(Key=key, Body=data)
  print "successfully upload ", name
  postfix +=1
  name = "../images/frame" + str (postfix)+ ".png"

# AWS rekognition
for count in range(0, postfix):
  key = "frame" + str (count)+ ".png"
  client = boto3.client('rekognition')
  # Send request to aws server
  print "Sending aws rekognition labels request for : ", key
  response = client.detect_labels(
    Image={
      'S3Object': {
        'Bucket': 'datatest',
        'Name': key,
      }
    },
    MaxLabels=20,
    MinConfidence=50.0
  )
  #print result
  print "Labels received for : ", key
  metadata[count] = response

#count = 0
#for count in range(0, postfix):
#  print "Labels received for : frame", count, ".png"
#  for datapair in metadata[count]['Labels']:
#    print (datapair['Name'])


keyword = ''
keyword2 = ''
# Start a loop that will run until the user enters 'quit'.
while (keyword2 != 'quit') and (keyword != 'quit'):
  keyword = raw_input("What you want to search, or quit: ")
  found = 0
  count = 0
  for count in range(0, postfix):
    for datapair in metadata[count]['Labels']:
#      print (datapair['Name'])
      if str(keyword).lower() == str(datapair['Name']).lower():
#        print str(keyword), " == " ,str(datapair['Name']), "Found. Location ", count*20
        found = 1
        img = video[count*20]
        cv2.imshow('frame',img)
        if cv2.waitKey(1) & 0xFF == ord('q'):
          break
        
        keyword2 = raw_input("Next(n) or search again(anykey)? ")
        if str(keyword2).lower() == str('n').lower():
          found = 0
          break
#      else:
#        print str(keyword), " == " ,str(datapair['Name']), "Not found yet"
    if found == 1:
      break
#-------------------------------------------------------------------
#Clean up
filelist = [ f for f in os.listdir("./images") if f.endswith(".png") ]
for f in filelist:
  os.remove("./images/"+f)


#release CV object
cap.release()
cv2.destroyAllWindows()



