from Gesys.gesys import GesysStatic
import cv2

gs = GesysStatic(30)
cap = cv2.VideoCapture(0)

while True:
    _, frame = cap.read()
    
    gesture = gs.frame(frame)
    if(gesture != 'thrash'):
        print(gesture)

    cv2.imshow('img', frame)
    if(cv2.waitKey(1)>0):
        break