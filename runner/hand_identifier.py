import numpy as np

class one_hand:
    def __init__(self, idx):
        self.center = []
        self.free = True
        self.updated = False
        self.in_row = 0
        self.idx = idx
        
    def get_dist(self, lands):
        """
        lands.shape = (21,3)
        """
        if self.free:
            return 1000
        
        x = np.mean(lands[:,0])
        y = np.mean(lands[:,1])
        
        d = np.sqrt((self.center[0] - x)**2 + (self.center[1] - y)**2)
        if(d<100):
            return d
        else:
            return 1000
    
    def update(self, lands):
        self.center = [np.mean(lands[:,0]), np.mean(lands[:,1])]
        self.free = False
        self.updated = True
    
    def frame(self):
        if(not self.free):
            if(self.updated):
                self.in_row = 0
            else:
                self.in_row += 1
        
        if(self.in_row > 10):
            self.free = True
            self.center = []
            self.in_row = 0
        
        self.updated = False

class Identifier:
    def __init__(self):
        self.hands = [one_hand(0), one_hand(1)]
        
    def get_id(self, lands):
        idx, dists = self.update(lands)
        
        return idx, dists
    
    def update(self, lands):
        dists = []
        for hand in self.hands:
            d = hand.get_dist(lands)
            dists.append(d)
            
        idx = np.argmin(dists)
        if(dists[idx] == 1000):
            for k, hand in enumerate(self.hands):
                if hand.free:
                    hand.update(lands)
                    return hand.idx, [-1, -1]
        else:
            self.hands[idx].update(lands)
        return self.hands[idx].idx, dists
    
    def frame(self):
        for hand in self.hands:
            hand.frame()