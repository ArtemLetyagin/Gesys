from gesys.detector.detector import Detector
from gesys.recognizer.recognizer import Recognizer
from gesys.runner.hand_identifier import Identifier
import numpy as np
import time

SPEED_MODE_CONSTS = {
    0: (0.7, 100, 10),
    1: (0.8, 50, 5),
    2: (0.9, 10, 0)
}
class Runner:
    def __init__(self, speed_mode):
        
        # init speed settings
        self.set_speed_mode(speed_mode)

        # init models
        self.detector = Detector(self.detector_skipness)
        self.recognizer = Recognizer()
        self.identifier = Identifier()

        # init secondary variable
        self.gestures = [2, 2]
        self.use_prev_box = False
        self.t = time.time()
        self.regions = []

    def set_speed_mode(self, speed_mode):
        """
        Выставляем константы отвечающие за 
        переключение между only_lm и detector
        """
        self.lm_score_threshold = SPEED_MODE_CONSTS[speed_mode][0]
        self.velocity_threshold = SPEED_MODE_CONSTS[speed_mode][1]
        self.detector_skipness = SPEED_MODE_CONSTS[speed_mode][2]
        
    def __call__(self, frame):

        high_lm_score, low_velocity = False, False
        
        if time.time() - self.t > 1:
            self.regions = self.detector.run(frame)
            self.set_region_ids_and_velocity()
            high_lm_score = self.check_lm_score() # True/False
            low_velocity = self.check_velocity() # True/ False
            self.t = time.time()
        else:
            high_lm_score, low_velocity = False, False
            if self.use_prev_box:
                self.regions = self.detector.run_lm_only(frame)
                self.set_region_ids_and_velocity()
                high_lm_score = self.check_lm_score() # True/False
                low_velocity = self.check_velocity() # True/ False
                
            else:
                self.regions = self.detector.run(frame)
                self.set_region_ids_and_velocity()
                high_lm_score = self.check_lm_score() # True/False
                low_velocity = self.check_velocity() # True/ False

        #print(high_lm_score, low_velocity)
        if high_lm_score and low_velocity:
            self.use_prev_box = True
        else:
            self.use_prev_box = False
         
        self.gestures = self.recognize_gesture(frame.shape)

        landmarks, ids = self.prepare_regions_for_return()
        
        self.identifier.frame()
        return landmarks, self.gestures

    def prepare_regions_for_return(self):
        """
        Подготавливаем регионы для возврата пользователю
        Считаем центры каждого региона и получаем айдишники

        landmarks.shape = (num_hands, 2)
        ids.shape = (num_hands, )
        """
        landmarks = []
        ids = []
        for r in self.regions:
            lms = r.true_lm  # shape = (21, 3)
            x_center = lms[:,0].mean()
            y_center = lms[:,1].mean()
            landmarks.append((x_center, y_center))   
            ids.append(r.id)
        return landmarks, ids

    def set_region_ids_and_velocity(self):
        """
        Выставляем новые скорости и айдишники для регионов
        """
        for r in self.regions:
            i, dists = self.identifier.get_id(r.true_lm)
            r.id = i
            r.velocity = dists[i]

    def recognize_gesture(self, frame_shape):
        h, w, _ = frame_shape
        landmarks = []
        for r in self.regions:
            landmarks.append(r.true_lm)

        if len(landmarks) > 0:
            gestures = self.recognizer(landmarks, h, w)
            return gestures
        return [2,2]

    def check_lm_score(self):
        high_lm_score = True
        for r in self.regions:
            if r.lm_score < self.lm_score_threshold:
                high_lm_score = False
        return high_lm_score

    def check_velocity(self):
        for r in self.regions:
            if r.velocity > self.velocity_threshold:
                return False
        return True
        
        