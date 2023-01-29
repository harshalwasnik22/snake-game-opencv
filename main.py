import math
import cvzone
import cv2
import random
import numpy as np
from cvzone.HandTrackingModule import HandDetector

cam = cv2.VideoCapture(0)
# cam.set(3,1280)
# cam.set(4,720)

detector = HandDetector(detectionCon=0.9,maxHands=1)

class SnakeGameClass:
    def __init__(self,pathFood):
        self.points = [] #all points of the snake
        self.lengths = [] #distance between each points
        self.currentlength = 0 #total length of the snake
        self.allowedlength = 130 #total allowed length
        self.previoushead=0,0 #previous head point
        self.score=0
        self.lastscore=0;
        self.gameOver=False

        self.imgFood=cv2.imread(pathFood,cv2.IMREAD_UNCHANGED)
        self.imgFood=cv2.resize(self.imgFood,(50,50))
        self.hFood,self.wFood,_=self.imgFood.shape
        self.foodPoint= 0, 0
        self.randomFoodLocation()


    def randomFoodLocation(self):
        self.foodPoint=random.randint(100,400),random.randint(100,300)

    def update(self, imgMain, currentHead):
        
        if self.gameOver:
            cvzone.putTextRect(imgMain,"Game Over",[300,400],scale=3,thickness=2,offset=20)
            cvzone.putTextRect(imgMain,f'Your Score: {self.lastscore}',[100,300],scale=3,thickness=2,offset=20)
            return imgMain

        px,py=self.previoushead
        cx,cy=currentHead
        self.points.append([cx,cy])
        distance=math.hypot(cx-px,cy-py)
        self.lengths.append(distance)
        self.currentlength+=distance
        self.previoushead=cx,cy


        # length reduction
        if self.currentlength > self.allowedlength:
            for i,length in enumerate(self.lengths):
                self.currentlength-=length
                self.lengths.pop(i)
                self.points.pop(i)
                if self.currentlength < self.allowedlength:
                    break

        #checking if snake have food
        rx,ry=self.foodPoint
        if rx-self.wFood//2< cx <rx+self.wFood//2 and ry-self.hFood//2< cy <ry+self.hFood//2:
            self.randomFoodLocation()
            self.allowedlength += 50
            self.score += 1
            print(self.score)

    
        #drawing snake
        if self.points: 
            for i, point in enumerate(self.points):
                if i!=0:
                    cv2.line(imgMain,self.points[i-1],self.points[i],(0,0,255),10)
            cv2.circle(img,self.points[-1],10,(200,0,200),cv2.FILLED)
        
        #drawing food
        rx,ry=self.foodPoint
        imgMain=cvzone.overlayPNG(imgMain,self.imgFood,(rx-self.wFood//2,ry-self.hFood//2))
        cvzone.putTextRect(imgMain,f'Score: {self.score}',[50,80],scale=2,thickness=2,offset=10)

        #check for collision using polygon function=> min distance with points
        pts=np.array(self.points[:-2],np.int32)
        pts=pts.reshape((-1,1,2))
        cv2.polylines(imgMain,[pts],False,(0,200,0),3)
        minDist = cv2.pointPolygonTest(pts,(cx,cy),True)

        if -0.5 <= minDist <= 0.5:
            print("hit")
            self.lastscore = self.score
            self.gameOver=True
            self.points = [] 
            self.lengths = []
            self.currentlength = 0
            self.allowedlength = 150 
            self.previoushead=0,0
            self.score = 0
            self.randomFoodLocation()

        return imgMain

game=SnakeGameClass("donut.png")

while True:
    success,img=cam.read()
    img=cv2.flip(img,1)  #to flip the image of its not correct
    hands,img=detector.findHands( img , flipType=False) # to flip hand labels
    if hands:
        lmlist=hands[0]['lmList'] #list of all endpoints of
        pointIndex=lmlist[8][0:2]
        img=game.update(img,pointIndex)

    cv2.imshow("Image",img) 
    key=cv2.waitKey(1)
    if key == ord('r'):
        game.gameOver=False