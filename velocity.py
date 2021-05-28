
class velocity():
    def __init__(self,size):
        self.vs=[]
        self.size =size
    
    def generate_vs(self):
        for i in range(self.size*2):
            self.vs.append(0)
        return self.vs
            