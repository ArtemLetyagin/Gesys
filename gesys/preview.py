import cv2
from gesys.runner.runner import Runner
import numpy as np

GESTURES = {
    0: 'stop',
    1: 'two up',
    2: 'thrash'
}

def put_text(img, text, pos):
    font = cv2.FONT_HERSHEY_SIMPLEX 
    fontScale = 1
    color = (255, 0, 0)  
    thickness = 2
    cv2.putText(img, text, pos, font,  
                    fontScale, color, thickness, cv2.LINE_AA)

def preview(speed_mode):
    cap = cv2.VideoCapture(0)
    run = Runner(speed_mode=speed_mode)
    while True:
        _, frame = cap.read()
        
        centers, gestures = run(frame)
        
        for i, (x, y) in enumerate(centers):
            text = GESTURES[gestures[i]]
            put_text(frame, text, (int(x), int(y)))
            cv2.circle(frame, (int(x), int(y)), 5, (0,255,0))

        cv2.imshow('window', frame)

        if cv2.waitKey(1) > -1:
            break
    cv2.destroyAllWindows()

